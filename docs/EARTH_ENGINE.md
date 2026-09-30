# Sentinel-2 / Sentinel-1 field signals via Google Earth Engine

KrishiSathi reads **real Sentinel-2 surface reflectance** from
[`COPERNICUS/S2_SR_HARMONIZED`](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED)
to show a field's NDVI on **My farm → Satellite vegetation signal** (drawn field, or a circle around the farm). There is no fallback data: without working
credentials, the endpoint returns `"status": "unavailable"` with a reason code, and no value.

| Provenance | |
|---|---|
| Source | Sentinel-2 via Google Earth Engine |
| Dataset | `COPERNICUS/S2_SR_HARMONIZED` (the harmonized collection; no other Sentinel-2 collection is substituted) |
| Provider | Copernicus / ESA |
| Processing | Level-2A surface reflectance |
| Output | *Satellite-derived vegetation signal* (NDVI). It is not ground-truth crop health. |

> **Security:** never commit service-account private keys or credential files (`*.json` keys, `.env`).
> The key is read only from the environment and is never logged or returned by the API.

## Source status

At start-up (module import, so it also happens on serverless cold starts), the backend:

1. reads `EE_SERVICE_ACCOUNT_KEY_JSON`: **configured**;
2. initializes Earth Engine for the project and makes one tiny request (`ee.Number(1).getInfo()`): **authenticated**;
3. reads the metadata of `COPERNICUS/S2_SR_HARMONIZED` (`ee.data.getAsset`, no computation): **available**.

Only step 3 makes the source usable. The Data & methods page shows the result of `/api/sources`:

| Backend `status` | `/api/sources` `status` | Page shows |
|---|---|---|
| `not_configured` (no key) | `not_configured` | Not set up |
| `available` (all three steps passed) | `configured` | Enabled |
| `unavailable` (key set, a step failed; `detail` has the code) | `unavailable` | Not available |

A failed start-up is retried every 5 minutes on the next crop-health request, except for key-format errors
and a missing library, which need a redeploy. If Google rejects the key or project after start-up, the
source switches to `unavailable`. Earth Engine is optional: it never blocks `/health/ready` or any other feature.

## What is computed

Two region modes, one method (`backend/services/earth_engine_service.py`):

| Mode | Endpoint | Region | When |
|---|---|---|---|
| **Polygon** (preferred) | `GET /api/farms/{id}/crop-health` (+ `/history`), farm token | the farmer's drawn field outline | the farm has a plot within 5 km of its location |
| **Point** (fallback) | same endpoints without a plot, or `GET /api/farm/crop-health?lat=&lng=` | a 250 m circle around the point | no plot drawn |

Every response has `roi.mode` (`polygon` with `area_ha` and `pixel_count`, or `point` with the circle) so the
UI can say what the numbers describe. A polygon's coordinates are never echoed back, logged or used in cache
keys (the key is a SHA-256 of the coordinates).

Latitude must be within −90…90 and longitude within −180…180; other values return HTTP 422 `INVALID_INPUT`.

1. It selects Sentinel-2 scenes intersecting the region (field outline or **250 m radius**) in two windows: the last 30 days, and the 30 days before.
2. It drops scenes with more than 60 % cloud (`CLOUDY_PIXEL_PERCENTAGE`), then masks each remaining pixel with the Scene Classification Layer. Only vegetation, bare soil, water and unclassified pixels are kept; cloud, cloud shadow, cirrus, snow, saturated and no-data pixels are removed.
3. For each pixel it computes NDVI = (B8 − B4) / (B8 + B4), takes the median across scenes, and averages it over the region at 10 m scale (pixels whose centre falls inside the outline).
4. A window counts only if enough of the region had clear pixels; otherwise a mean would describe a few scattered pixels, not the field. Point: at least 10 % of the circle. Polygon (a small area, so stricter): at least 30 % of the field's pixels **and** at least 10 clear pixels.
5. It returns `ndvi`, `ndvi_previous`, `change`, `image_count`, `latest_image_date`, `clear_pixel_fraction`, `observation` (newest scene: `image_id`, `sensed_at`, `scene_cloud_pct`), `roi`, both windows and provenance. Both windows come back in a single Earth Engine request.
6. If no usable observation exists (for example during the monsoon), it returns `"status": "no_data", "reason": "no_suitable_observation"`, never a number. `observation` still names the newest scene, if any, so you can see it was cloudy.

### Field outline, pixels and mixed land (data quality)

A drawn outline can include a road, a pond, trees or a neighbour's land, and a 250 m circle almost always does.
Every answer therefore carries a `quality` block instead of implying the number is "the crop":

| Field | Meaning |
|---|---|
| `pixel_count` | 10 m pixels in the region (polygon: counted by Earth Engine; point: the circle, ≈ 1963) |
| `clear_pixel_count`, `clear_pixel_fraction` | pixels with at least one cloud-free observation in the current window |
| `valid_pixel_fraction` | pixels with any Sentinel-2 observation at all (clouds included) |
| `land_cover` | shares of cropland, trees, grass/shrub, built-up, water and other inside the region from **ESA WorldCover 10 m 2021 (v200)**; `unavailable` if it could not be read |
| `flags` | `field_too_small` (< 10 pixels, i.e. < 0.1 ha), `too_few_clear_pixels`, `mixed_land_cover` (< 50 % mapped cropland), `contains_water` (≥ 10 %), `contains_trees` (≥ 20 %), `contains_built_up` (≥ 10 %), `point_circle_not_field_boundary` |
| `level` | `good` (usable, ≥ 60 % clear, none of the limiting flags), `limited`, or `insufficient` |

WorldCover is a 2021 map and is used only to flag mixed regions; it never changes the NDVI value. The
point circle is always at most `limited`, because it is not the field.

When a polygon has some clear pixels but too few to stand for the field, the answer is
`"status": "insufficient_data", "reason": "too_few_clear_pixels"`; below 10 pixels it is
`"reason": "field_too_small"` (radar and baseline are then not computed either). Neither returns a number.
The risk engine turns `good` into moderate evidence confidence and anything else into low (see
`docs/INTELLIGENCE.md`).

### Same-season baseline (temporal context)

The same request also computes steps 1–4 for the **same 30-day window in each of the previous 3 years**
(`baseline.years`). With at least 2 usable years, `baseline.position` says whether the current NDVI is
`below_range`, `within_range` or `above_range` of those years (their min–max). With fewer, `baseline.status`
is `insufficient_data` and no position is given. No threshold is involved; rotation, a different sowing date
or a different crop in past years also move this comparison, so it is shown as context, not a diagnosis.

### History series

`GET /api/farm/crop-health/history?lat=&lng=` returns NDVI for the last **six consecutive 30-day windows**
(one Earth Engine request). A window without a clear observation is `null` and the UI draws it as a gap;
nothing is interpolated. Fewer than 2 usable windows gives `"status": "insufficient_data"`.

### Sentinel-1 radar (cloud-resilient)

[`COPERNICUS/S1_GRD`](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD) is read in the same
request when its metadata check passed at start-up (`radar_available` in `/api/debug/earth-engine-status`; a
failing radar check never disables Sentinel-2). For the last 12 days and the 12 days before, it takes IW-mode
scenes with VV and VH, averages backscatter (dB, already calibrated and terrain-corrected) over the 250 m circle,
separately for ascending and descending passes, and compares only the same pass direction.

| Field | Meaning | Interpretation |
|---|---|---|
| `vv_db`, `vh_db` | mean backscatter now | Shown, not scored. VH responds to vegetation volume; both respond to soil moisture, tillage and water. |
| `vh_change_db` | change from the earlier pass | Shown, not scored: growth, harvest, tillage and flooding all change it. |
| `water_signal` | `vh_now / vh_before > 1.25` (both dB) | UN-SPIDER Recommended Practice change-detection threshold for new open water. Applied to the circle's mean, so it is a *screening* signal for standing water, never a flood map. `null` without an earlier pass. |

Radar does not measure crop health, pH or nutrients and is never turned into a crop-health score. Its only use in
the risk engine is the `water_signal`, which can raise waterlogging to *moderate* (confidence *low*).
Averaging dB values is a simplification; over ~2 000 pixels it mainly suppresses speckle.

## One-time setup

1. **Google Cloud project.** Create a project, or reuse one, in the [Cloud console](https://console.cloud.google.com/).
2. **Register the project for Earth Engine** at <https://code.earthengine.google.com/register>. Choose noncommercial use if it applies; commercial use needs a paid Earth Engine plan.
3. **Enable the API.** Enable the *Google Earth Engine API* (`earthengine.googleapis.com`) for the project.
4. **Service account.** Under *IAM & Admin → Service accounts*:
   1. Create an account, for example `krishisathi-ndvi`.
   2. Grant it **Earth Engine Resource Viewer** (`roles/earthengine.viewer`) and **Service Usage Consumer** (`roles/serviceusage.serviceUsageConsumer`) on the project.
   3. Open the account and go to *Keys → Add key → JSON*. This downloads the key file. The key must contain `client_email`, `private_key` and `project_id`.
5. **Set the environment variable** on the backend. For Vercel: *Project → Settings → Environment Variables*, then redeploy.
   - `EE_SERVICE_ACCOUNT_KEY_JSON`: the whole JSON file. If your dashboard mangles multi-line values, paste the base64 output of `base64 -w0 key.json` instead.
   - `EE_PROJECT` (optional): set this only if the project registered in step 2 differs from the key's `project_id`.
   - Without a key (for example, when an organisation policy blocks JSON key creation): set only `EE_PROJECT` and the backend uses Application Default Credentials — `gcloud auth application-default login` locally, or the host's attached service account. Status and error codes are the same as with a key.
   - Render: the variables are declared in `render.yaml` with `sync: false`; set their values in the dashboard.
   - Docker / other hosts: pass them as environment variables or secrets. With a key set, no credential file, `gcloud` login or browser authentication is used.
6. **Keep the key secret.** Never commit it. `.env` is git-ignored, and the key is read only from the environment.

## Verify

```bash
cd backend
# Health check only: authenticate and read the dataset metadata (cheap)
EE_SERVICE_ACCOUNT_KEY_JSON="$(cat /path/to/key.json)" python scripts/check_earth_engine.py --status-only
# Real query at a coordinate; prints the API response (default point: Ludhiana)
EE_SERVICE_ACCOUNT_KEY_JSON="$(cat /path/to/key.json)" python scripts/check_earth_engine.py 30.90 75.85
# The same check as a test; it is skipped when the variable is unset
EE_SERVICE_ACCOUNT_KEY_JSON="$(cat /path/to/key.json)" python -m pytest tests/test_earth_engine.py -k live -q
```

After deploying, run these checks:

| Check | Expected |
|---|---|
| `GET /health/ready` | `"earth_engine": "available"` |
| `GET /api/sources` | the `satellite` source has `"status": "configured"`, `"detail": null`, `"dataset": "COPERNICUS/S2_SR_HARMONIZED"` |
| `GET /api/farm/crop-health?lat=30.90&lng=75.85` | `"status": "available"` with `ndvi`, `observation.image_id` and `latest_image_date`; or `"no_data"` / `no_suitable_observation` when every recent scene is cloudy |
| Data & methods page | Sentinel-2 shows **Enabled** |

To run the live test in CI, add the key as the GitHub Actions secret `EE_SERVICE_ACCOUNT_KEY_JSON`. The backend job passes it to pytest.

## Error codes

`/health/ready` reports `earth_engine: "unavailable:<code>"`, `/api/sources` reports the code as `detail`, and
`/api/farm/crop-health` reports it as `reason` with `retryable`. Raw Google errors appear only in server logs.

| Code | Meaning | Fix |
|---|---|---|
| `not_configured` | Neither `EE_SERVICE_ACCOUNT_KEY_JSON` nor `EE_PROJECT` is set | Set them (step 5) and redeploy |
| `invalid_key_encoding` | The value is neither JSON nor base64 | Paste the file contents, or `base64 -w0 key.json` |
| `invalid_key_json` | The JSON is truncated or malformed | Paste the whole file again |
| `not_a_service_account_key` | The value is a user OAuth token or another credential type | Create a service-account **JSON key** (step 4) |
| `key_missing_fields` | `client_email`, `private_key` or `project_id` is missing | Download a fresh key |
| `library_missing` | `earthengine-api` is not installed | `pip install -r requirements.txt` |
| `auth_failed` | Google rejected the key or application default credentials (deleted or disabled account, revoked key, expired `gcloud` login, `invalid_grant`) | Create a new key (step 4.3) |
| `project_configuration_error` | The project is not registered for Earth Engine, the API is disabled, or the account lacks a role | Repeat steps 2–4; set `EE_PROJECT` if the registered project differs |
| `dataset_query_failed` | Authenticated, but reading or querying `COPERNICUS/S2_SR_HARMONIZED` failed | Check server logs |
| `earth_engine_unavailable` | Network error or Earth Engine server error | None; retried automatically (`retryable: true`) |
| `timeout` | Earth Engine did not answer within 25 s | None; retried automatically (`retryable: true`) |
| `no_suitable_observation` | Not an error: no scene in 30 days had enough clear pixels over the field (`status: "no_data"`) | None |
| `too_few_clear_pixels` | Not an error: a drawn field had some clear pixels but too few to describe it (`status: "insufficient_data"`) | None |
| `field_too_small` | Not an error: the drawn field covers fewer than 10 pixels (`status: "insufficient_data"`) | Draw the whole field |

Start-up failures with the codes `auth_failed`, `project_configuration_error`, `dataset_query_failed`,
`earth_engine_unavailable` and `timeout` are retried every 5 minutes.

## Limits

* NDVI depends on crop and growth stage. Compare a field with itself over time, not with other crops.
* The 250 m circle can include neighbouring fields, roads or water; draw the field to avoid this. Even a
  drawn field can contain mixed land, which `quality.land_cover` and `flags` report.
* NDVI is a satellite vegetation signal, not crop health, not yield. VV/VH backscatter is not soil moisture.
* Regional (state-level) NDVI aggregation is not implemented. The policy dashboard says so and shows no values.
* Plots are limited to 0.01–200 ha (≤ 20 000 pixels at 10 m); `maxPixels` is capped at 1 000 000 so an
  oversized request fails instead of quietly computing over a huge area. Processing resolution is 10 m.
* Each request makes one Earth Engine call (all windows, baseline years, radar and land cover in one
  round trip), bounded at 25 s. Successful and no-data answers are cached for 6 hours per region per day
  (point: rounded coordinates; polygon: hash of the outline), and concurrent requests for the same region
  share one query. The farm view waits at most 8 s and shows "still loading" rather than blocking.

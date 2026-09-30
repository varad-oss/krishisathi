# Sentinel-2 crop health via Google Earth Engine

KrishiSathi reads **real Sentinel-2 surface reflectance** from
[`COPERNICUS/S2_SR_HARMONIZED`](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED)
to show a farm's NDVI on **My farm → Crop health**. There is no fallback data: without working
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

`GET /api/farm/crop-health?lat=&lng=` (`backend/services/earth_engine_service.py`):

Latitude must be within −90…90 and longitude within −180…180; other values return HTTP 422 `INVALID_INPUT`.

1. It selects Sentinel-2 scenes intersecting a **250 m radius** around the point in two windows: the last 30 days, and the 30 days before.
2. It drops scenes with more than 60 % cloud (`CLOUDY_PIXEL_PERCENTAGE`), then masks each remaining pixel with the Scene Classification Layer. Only vegetation, bare soil, water and unclassified pixels are kept; cloud, cloud shadow, cirrus, snow, saturated and no-data pixels are removed.
3. For each pixel it computes NDVI = (B8 − B4) / (B8 + B4), takes the median across scenes, and averages it over the circle at 10 m scale.
4. A window counts only if at least 10 % of the circle had clear pixels; otherwise a mean would describe a few scattered pixels, not the field.
5. It returns `ndvi`, `ndvi_previous`, `change`, `image_count`, `latest_image_date`, `clear_pixel_fraction`, `observation` (newest scene: `image_id`, `sensed_at`, `scene_cloud_pct`), `roi`, both windows and provenance. Both windows come back in a single Earth Engine request.
6. If no usable observation exists (for example during the monsoon), it returns `"status": "no_data", "reason": "no_suitable_observation"`, never a number. `observation` still names the newest scene, if any, so you can see it was cloudy.

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
   - Render: the variables are declared in `render.yaml` with `sync: false`; set their values in the dashboard.
   - Docker / other hosts: pass them as environment variables or secrets. No credential file, `gcloud` login or browser authentication is used.
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
| `not_configured` | `EE_SERVICE_ACCOUNT_KEY_JSON` is not set | Set it (step 5) and redeploy |
| `service_account_key_missing` | `EE_PROJECT` is set, so Earth Engine was intended, but the key is not | Set `EE_SERVICE_ACCOUNT_KEY_JSON` |
| `invalid_key_encoding` | The value is neither JSON nor base64 | Paste the file contents, or `base64 -w0 key.json` |
| `invalid_key_json` | The JSON is truncated or malformed | Paste the whole file again |
| `not_a_service_account_key` | The value is a user OAuth token or another credential type | Create a service-account **JSON key** (step 4) |
| `key_missing_fields` | `client_email`, `private_key` or `project_id` is missing | Download a fresh key |
| `library_missing` | `earthengine-api` is not installed | `pip install -r requirements.txt` |
| `auth_failed` | Google rejected the key (deleted or disabled account, revoked key, `invalid_grant`) | Create a new key (step 4.3) |
| `project_configuration_error` | The project is not registered for Earth Engine, the API is disabled, or the account lacks a role | Repeat steps 2–4; set `EE_PROJECT` if the registered project differs |
| `dataset_query_failed` | Authenticated, but reading or querying `COPERNICUS/S2_SR_HARMONIZED` failed | Check server logs |
| `earth_engine_unavailable` | Network error or Earth Engine server error | None; retried automatically (`retryable: true`) |
| `timeout` | Earth Engine did not answer within 25 s | None; retried automatically (`retryable: true`) |
| `no_suitable_observation` | Not an error: no scene in 30 days had enough clear pixels over the field (`status: "no_data"`) | None |

Start-up failures with the codes `auth_failed`, `project_configuration_error`, `dataset_query_failed`,
`earth_engine_unavailable` and `timeout` are retried every 5 minutes.

## Limits

* NDVI depends on crop and growth stage. Compare a field with itself over time, not with other crops.
* The 250 m circle can include neighbouring fields, roads or water.
* Regional (state-level) NDVI aggregation is not implemented. The policy dashboard says so and shows no values.
* Each request makes one synchronous Earth Engine call, bounded at 25 s. Results are not cached.

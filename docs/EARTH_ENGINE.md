# Sentinel-2 crop health via Google Earth Engine

KrishiSathi reads **real Sentinel-2 surface reflectance** from
[`COPERNICUS/S2_SR_HARMONIZED`](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED)
to show a farm's NDVI on **My farm → Crop health**. There is no fallback data: without working
credentials, the endpoint returns `"status": "unavailable"`, and the Data & methods page shows "Not set up".

## What is computed

`GET /api/farm/crop-health?lat=&lng=` (`backend/services/earth_engine_service.py`):

1. It selects Sentinel-2 scenes intersecting a **250 m radius** around the point in two windows: the last 30 days, and the 30 days before.
2. It drops scenes with more than 60 % cloud (`CLOUDY_PIXEL_PERCENTAGE`), then masks each remaining pixel with the Scene Classification Layer. Only vegetation, bare soil, water and unclassified pixels are kept; cloud, cloud shadow, cirrus, snow, saturated and no-data pixels are removed.
3. For each pixel it computes NDVI = (B8 − B4) / (B8 + B4), takes the median across scenes, and averages it over the circle at 10 m scale.
4. It returns `ndvi`, `ndvi_previous`, `change`, `image_count`, `latest_image_date`, both windows and provenance. Both windows come back in a single Earth Engine request.
5. If no clear pixel exists (for example during the monsoon), it returns `"status": "no_data", "reason": "no_clear_imagery"`, never a number.

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
6. **Keep the key secret.** Never commit it. `.env` is git-ignored, and the key is read only from the environment.

## Verify

```bash
cd backend
# Queries real Sentinel-2 data with your key and prints the API response (default point: Ludhiana)
EE_SERVICE_ACCOUNT_KEY_JSON="$(cat /path/to/key.json)" python scripts/check_earth_engine.py 30.90 75.85
# The same check as a test; it is skipped when the variable is unset
EE_SERVICE_ACCOUNT_KEY_JSON="$(cat /path/to/key.json)" python -m pytest tests/test_earth_engine.py -k live -q
```

After deploying, run these checks:

| Check | Expected |
|---|---|
| `GET /health/ready` | `"earth_engine": "configured"` |
| `GET /api/sources` | the `satellite` source has `"status": "configured"` and `"detail": null` |
| `GET /api/farm/crop-health?lat=30.90&lng=75.85` | `"status": "available"` with `ndvi`, `image_count` and `latest_image_date`; or `"no_data"` when every recent scene is cloudy |
| Data & methods page | Sentinel-2 shows **Enabled** |

To run the live test in CI, add the key as the GitHub Actions secret `EE_SERVICE_ACCOUNT_KEY_JSON`. The backend job passes it to pytest.

## Error codes

`/health/ready` reports `earth_engine: "<status>:<code>"`, and `/api/sources` reports the code as `detail`. Raw exceptions appear only in server logs.

| Code | Meaning | Fix |
|---|---|---|
| *(status `not_configured`)* | `EE_SERVICE_ACCOUNT_KEY_JSON` is not set | Set it (step 5) and redeploy |
| `invalid_key_encoding` | The value is neither JSON nor base64 | Paste the file contents, or `base64 -w0 key.json` |
| `invalid_key_json` | The JSON is truncated or malformed | Paste the whole file again |
| `not_a_service_account_key` | The value is a user OAuth token or another credential type | Create a service-account **JSON key** (step 4) |
| `key_missing_fields` | `client_email`, `private_key` or `project_id` is missing | Download a fresh key |
| `authentication_failed` | Google rejected the account or project. Usually the project is not registered for Earth Engine, the API is disabled, the account lacks the roles, or the key was deleted | Repeat steps 2–4; set `EE_PROJECT` if the registered project differs. The server retries every 5 minutes. |
| `library_missing` | `earthengine-api` is not installed | `pip install -r requirements.txt` |

## Limits

* NDVI depends on crop and growth stage. Compare a field with itself over time, not with other crops.
* The 250 m circle can include neighbouring fields, roads or water.
* Regional (state-level) NDVI aggregation is not implemented. The policy dashboard says so and shows no values.
* Each request makes one synchronous Earth Engine call, bounded at 25 s. Results are not cached.

# KrishiSathi — Repository Audit (2026-09-26)

This audit was written before the production-readiness overhaul on branch
`claude/sleepy-brown-b55czw`. It records what the code did at commit `4feae0d`,
what was wrong with it, and the order the fixes were done in. The later
sections of this file say what the overhaul changed.

## 1. Architecture map (as found)

```
Next.js 16 (App Router, all pages "use client")          FastAPI (Vercel serverless / Docker)
  /            landing                                     /api/diagnose        Gemini vision → JSON
  /diagnose    upload → diagnosis → follow-up chat  ───▶   /api/advisory        Gemini "agent" + tools
  /chat        advisory chat + "local intelligence"        /api/advisory/*      transcribe / voice / tts (gTTS)
  /map         outbreak map + alerts + NDVI                /api/weather         Open-Meteo
  /dashboard   policymaker dashboard                       /api/alerts          outbreaks from DB
  /about       "model accuracy" page                       /api/dashboard/*     stats, report (Gemini), crop-health
  lib/api.ts   fetch wrappers + DEMO_MODE mock fallback    /api/states/*        state config + federation signals (JWT)
  lib/mock-data.ts                                         /api/kvk/nearest     static JSON of 23 KVKs
  lib/translations.ts  10 languages, English-key lookup    /api/debug/*         EE status (JWT), DB internals (open)
                                                           SQLAlchemy async (SQLite dev / Postgres prod), Alembic
                                                           Redis (rate limit, idempotency, stats cache)
                                                           BigQuery telemetry (optional), Earth Engine (optional)
```

## 2. User flows traced

| Flow | What actually happened |
|---|---|
| Landing → Dashboard | "Dashboard" is the policymaker view. There was no farmer dashboard; the farmer's "local intelligence" lived in the chat sidebar. |
| Advisory (`/chat`) | Four hardcoded demo locations. Each query made three Gemini calls in sequence (translate in, agent, translate out). The agent's `get_state_config_tool` gave the model made-up "farmers reached" numbers. The greeting said "I have analyzed your local satellite data", which was never true. |
| Diagnosis | If geolocation was denied, the app **silently used New Delhi coordinates**. Those were saved and fed into outbreak clustering. The UI showed the LLM's self-reported score as a precise percentage (e.g. "94.5%"). If that field was missing, the frontend **substituted 0.9**. |
| Weather | The request included `soil_moisture_0_to_7cm`, which is **not a variable of Open-Meteo's forecast endpoint** (it exists only in the seasonal API; checked against the open-meteo-website docs source), so live weather most likely failed. Humidity, rain and soil moisture labelled "current" were actually `hourly[0]`, the value at local midnight. |
| Alerts | `getAlerts()` called `/api/dashboard/alerts`, which **does not exist**. The map sidebar always failed, or in demo mode showed a made-up "Locust swarm" alert. |
| Crop health | `/api/dashboard/crop-health` returned **hardcoded NDVI for 8 states** labelled `"status": "success"`. Its own regression test (`test_crop_health_unavailable`) failed. |
| Policymaker dashboard | `farmers_reached: 28,710,000` and `diagnoses_trend: +14.5%` were hardcoded in `persistence_service`. The state list had invented per-state farmer counts and alert counts. "Live Data Feed" was a static green dot. |
| State selection | The frontend matched outbreaks by `region === state name`, but outbreak regions look like "Cluster near 18.52, 73.86", so the state filter never matched anything. |

## 3. Fallback / fabrication inventory

| # | Location | Behaviour | Severity |
|---|---|---|---|
| F1 | `routers/dashboard.py::get_crop_health` | Hardcoded NDVI, drought risk and health status for 8 states, labelled success | Critical |
| F2 | `persistence_service.get_dashboard_stats` | `farmers_reached=28710000`, `diagnoses_trend=14.5` | Critical |
| F3 | `routers/states.py::INDIAN_STATES` | Invented `farmers_reached`, `active_alerts`, unsourced `arable_land_mha` | High |
| F4 | `frontend/lib/mock-data.ts` + `IS_DEMO_MODE` | Every API wrapper returned mock diagnosis, weather, outbreaks, NDVI, alerts or report on failure | Critical (if enabled) |
| F5 | `frontend/lib/api.ts::diagnoseCrop` | `model_confidence_score ?? 0.9` | Critical |
| F6 | `frontend/app/diagnose` | Silent New Delhi location fallback, persisted into outbreak data | Critical (data integrity) |
| F7 | `routers/alerts.py` | `affected_area_km2 = π·r²` of a fixed 50 km clustering radius, shown as "affected area" | High |
| F8 | `persistence_service.save_diagnosis` | "Healthy" and low-certainty results counted towards outbreak clusters | High |
| F9 | `frontend/app/about` | "93.4% top-1 accuracy", "fine-tuned", with no evaluation artefact in the repo | High |
| F10 | Landing page | "38+ diseases", "Join millions of Indian farmers" | Medium |
| F11 | `chat` sidebar | NDVI "fallback" to `data[0]` (another state's value); "Optimal / Needs Water" badge derived from rainfall when soil moisture was missing | High |
| F12 | `core/security.py` | Without `JWT_SECRET`, any bearer token was accepted; `mock-system-token-123` granted the **system** role and was hardcoded in the client bundle | Critical (security) |
| F13 | `core/rate_limit.py` | Rate limiting silently disabled when Redis was missing | Medium |
| F14 | `.env.example` | "Other services fall back to mock data gracefully" | Low (docs) |

## 4. Security risks

* **CORS** allowed `*` together with `allow_credentials=True`.
* **`/api/debug/db`** was unauthenticated. It ran DDL and returned `engine.url`, which can include the database username and host.
* **Auth bypass** via the dummy token (F12). Federation signals could be forged by anyone.
* **Error leakage**: the global middleware returned `f"Internal Server Error: {e}"`, and `/api/kvk` returned `str(e)`.
* **`/api/advisory/tts`** had no rate limit and no length limit on text sent to gTTS.
* **Prompt injection**: `disease_name`, `severity` and `crop_type` from query strings went straight into prompts. `crop_type` and `language` were not allow-listed.
* **Privacy**: the public dashboard returned exact farmer GPS coordinates in `recent_activity` and as outbreak centroids.
* **MIME trust**: the multipart upload trusted the client `content_type`, and every image was sent to Gemini as `image/jpeg`.
* **Unused cloud SDKs** (translate, speech, TTS, firestore, storage, twilio, scikit-learn) made the serverless bundle larger and the attack surface wider.

## 5. Reliability and performance risks

* Gemini SDK calls were **synchronous inside async handlers**. Each one blocked the event loop for the whole model latency, and none had a timeout.
* The agent's weather tool made a **second, blocking** Open-Meteo call for data the handler had already fetched.
* Non-English advisories made **three sequential LLM calls**. Non-English diagnoses translated JSON through an LLM, and any parse glitch returned a 500.
* Persisting an advisory could fail and **discard a successful answer** with a 503.
* The frontend made unhandled promise rejections (`getWeather().then(...)` with no catch), which left spinners showing "..." forever.
* All 10 languages (about 2,500 lines) were bundled into every page.
* The Leaflet marker icons were loaded from a CDN at a mismatched version (1.7.1 vs 1.9.4).

## 6. UX and accessibility problems

* No farmer dashboard, and no way to set or keep a farm location or crop.
* Many strings were not translated: error states, "Loading Dashboard Data...", severity badges, the low-confidence warning, and the upload hint ("SVG, PNG, JPG or GIF (max. 10MB)" was also wrong; the backend accepts JPEG/PNG/WebP up to 5 MB).
* `<html lang="en">` was fixed regardless of the chosen language.
* The mobile menu button had no accessible name, and icon-only buttons had no labels.
* Charts had no text alternative.
* The "Find Nearest KVK" button did nothing.
* The dashboard was one full-page spinner until every request finished, and one failure blanked the whole page.

## 7. Build and test status at HEAD

* `npm run lint`: **4 errors**. `next build`: **fails** because `ReactMarkdown` is used but not imported in `dashboard/page.tsx`.
* Backend pytest: 55 passed, **2 failed** (`test_crop_health_unavailable`, `test_redis_failure_prod`). Both failures were regressions introduced by recent "fix" commits.
* 25 one-off `fix_*.py` / `update_*.py` scripts were committed at the repo root.

## 8. Implementation order

1. Make the build green and remove fabricated values (F1–F11). Security fixes: CORS, the debug endpoint, auth fail-closed, and error leakage.
2. A consistent error envelope `{error: {code, message, request_id, retryable}}`, request IDs, security headers, and an in-memory rate-limit fallback.
3. Fix the weather contract. Add deterministic agronomic rules with explicit thresholds and sources, SoilGrids soil properties, regenerative recommendations with visible reasoning, and a point-level Earth Engine NDVI that reports itself as unavailable when not configured.
4. AI hardening: async calls with timeouts, a validated diagnosis schema with an explicit status (`disease_detected | healthy | uncertain | not_a_plant`) and a qualitative certainty, a separate verified-reference block, a single grounded advisory call, and allow-listed inputs.
5. Frontend: a typed API client, localized error codes, lazy-loaded locale files, shared state and provenance components, and a farm profile. Then a redesign of every page around the farmer and policymaker jobs.
6. Tests: backend regression tests, i18n completeness checks, and Playwright end-to-end tests of the main journeys, including failure states.
7. Visual QA at 320–1280 px, documentation, and an updated Graphify graph.

## 9. What was done

**Fallbacks removed.** F1–F14 are all resolved.

| Item | Resolution |
|---|---|
| F1 | Regional crop health returns an explicit `unavailable` status. Point-level NDVI comes from Earth Engine only when it is configured. |
| F2, F3 | Dashboard and state endpoints return only real counts with provenance. |
| F4 | Mock data and demo mode are deleted. |
| F5 | The confidence percentage is replaced by the model's qualitative certainty plus a reason. |
| F6 | No default location. Diagnosis runs without weather context when no location is set. |
| F7 | `affected_area_km2` is replaced by the actual `alert_radius_km`. |
| F8 | Only confident `disease_detected` results with a location feed clusters. Clusters older than 21 days are dropped. |
| F9, F10 | Invented claims are removed. The About page states that accuracy has not been measured. |
| F11 | The chat page is replaced by the grounded advisor, which lists the data sources it used and marks unavailable ones. |
| F12 | Auth fails closed (503 without `JWT_SECRET`) and the hardcoded token is gone. |
| F13 | Rate limiting falls back to an in-process window when Redis is absent. |
| F14 | `.env.example` is rewritten. |

**Backend**

* Every error uses one envelope: `{"error":{"code","message","request_id","retryable"}}`.
* Request-ID propagation, structured access logs, security headers, and a restricted CORS configuration.
* Liveness and readiness probes.
* `/api/debug/db` is removed.
* The weather contract is fixed and extended with forecast, ET₀ and soil moisture.
* New services:
  * rule-based agronomic insights using IMD thresholds, each carrying its basis and source
  * SoilGrids soil properties with Soil Health Card ratings
  * a regenerative-practice recommender that exposes its triggers
  * farm-level `/api/farm/*` endpoints
* Gemini calls are async with timeouts and validated against a schema.
* Prompt-injection fencing wraps farmer input.
* Chemical options are gated on a matched verified reference and adequate certainty.
* Uploaded images are validated by content, not by the file extension.
* Stored locations are coarsened to about 1 km, and public output is coarsened to about 11 km.

**Frontend**

* Every page is redesigned: landing, farm dashboard, diagnosis, advisor, policy dashboard, and data & methods.
* A typed API client with timeouts and localized error codes.
* Every screen has loading, error-with-retry (showing the request ID), empty and unavailable states.
* A provenance line appears on every data panel.
* Ten languages with native numerals, loaded lazily.
* Mobile bottom navigation.
* Charts and maps are lazy-loaded.
* CSP and security headers.

**Tests and CI**

* Backend: 116 tests.
* Locale integrity tests.
* 10 Playwright journeys plus overflow checks at 320 px and 360 px, each run on desktop and Pixel 7.
* CI runs lint, typecheck, i18n, build, e2e, backend tests on SQLite, and the Postgres concurrency test.

## 10. What remains

* Measure diagnosis accuracy on an Indian field dataset. The script exists; the dataset and results do not.
* Have native-speaking agronomists review all nine translations.
* Aggregate regional satellite crop health (Earth Engine batch job + storage). It is currently reported as unavailable.
* Expand `disease_reference.json`. Reference text is English-only and is labelled as such in the UI.
* Build an issuing flow for publisher tokens. Tokens are currently minted out of band with `JWT_SECRET`.
* Add offline support with a service worker for low-connectivity areas.
* Verify the Open-Meteo and SoilGrids field names against the live APIs in staging. The development sandbox could not reach them; the parsers were written from the providers' published schemas and are covered by fixture tests.

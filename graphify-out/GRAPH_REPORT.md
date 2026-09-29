# Graph Report - krishisathi  (2026-09-29)

## Corpus Check
- 159 files · ~109,310 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 6, .example 2, .ini 1)

## Summary
- 1225 nodes · 2786 edges · 95 communities (71 shown, 24 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 63 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ad71c9be`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- en.ts
- test_security.py
- test_failure_states.py
- sqlalchemy
- routers/advisory.py
- layout.tsx
- ServiceUnavailableException
- insight-text.ts
- diagnose.py
- api.ts
- test_kvk.py
- errors.py
- useI18n
- test_advisory.py
- test_diagnosis.py
- validate_plantvillage.py
- mock-api.ts
- .save_diagnosis
- Conversation.tsx
- diagnose/page.tsx
- interop.py
- package.json
- gemini_service.py
- compilerOptions
- dependencies
- env.py
- utils.ts
- main.py
- persistence_service.py
- eslint.config.mjs
- rate_limit.py
- cn
- ApiError
- test_p03_outbreaks.py
- soil_service.py
- advisory_context.py
- request
- devDependencies
- speech.ts
- config.py
- get
- manifest.json
- scripts
- test_earth_engine.py
- test_intelligence.py
- exports.md
- github-and-merge.md
- query.md
- update.md
- SKILL.md
- AGENTS.md
- .log_diagnosis
- AUDIT.md
- OutbreakMap.tsx
- README.md
- Footer.tsx
- transcribe.md
- earth_engine_service.py
- add-watch.md
- hooks.md
- next.config.ts
- frontend/README.md
- TrendChart.tsx
- vercel.json
- rules/graphify.md
- ponytail.md
- extraction-spec.md
- workflows/graphify.md
- requirements.txt
- frontend/AGENTS.md
- postcss.config.mjs
- datetime
- farm.py
- test_p02_regression.py
- diagnosis.py
- i18n.tsx
- normalize_crop
- get_weather_risk
- dashboard.py
- fastapi_testclient
- Sentinel-2 crop health via Google Earth Engine
- helpers.py
- pytest
- WeatherService
- reset_limits

## God Nodes (most connected - your core abstractions)
1. `useI18n()` - 67 edges
2. `cn()` - 53 edges
3. `ServiceUnavailableException` - 43 edges
4. `get()` - 36 edges
5. `request()` - 25 edges
6. `ApiError` - 23 edges
7. `post()` - 22 edges
8. `ApiError` - 18 edges
9. `MessageKey` - 18 edges
10. `lucide-react` - 16 edges

## Surprising Connections (you probably didn't know these)
- `test_weather_failure_raises_exception()` --uses--> `ServiceUnavailableException`  [INFERRED]
  backend/tests/test_failure_states.py → backend/models/exceptions.py
- `test_weather_timeout_has_specific_message()` --uses--> `ServiceUnavailableException`  [INFERRED]
  backend/tests/test_failure_states.py → backend/models/exceptions.py
- `get_voice_advisory()` --uses--> `ApiError`  [INFERRED]
  backend/routers/advisory.py → backend/core/errors.py
- `diagnose_multipart()` --uses--> `ApiError`  [INFERRED]
  backend/routers/diagnose.py → backend/core/errors.py
- `install_error_handlers()` --uses--> `ServiceUnavailableException`  [INFERRED]
  backend/core/errors.py → backend/models/exceptions.py

## Import Cycles
- None detected.

## Communities (95 total, 24 thin omitted)

### Community 0 - "en.ts"
Cohesion: 0.14
Nodes (11): bn, en, Messages, gu, hi, kn, ml, mr (+3 more)

### Community 1 - "test_security.py"
Cohesion: 0.07
Nodes (27): ai_down(), create_token(), err(), image_payload(), MockRedis, fixture, Regression: without Redis the limiter used to be silently disabled., Regression: allow_origins used to include '*' together with credentials. (+19 more)

### Community 2 - "test_failure_states.py"
Cohesion: 0.13
Nodes (15): jpeg_bytes(), test_tiny_image_rejected(), clear_caches(), asyncio, fixture, parametrize, Every upstream failure must surface as an explicit, retryable error, never as…, test_ai_not_configured_is_explicit() (+7 more)

### Community 4 - "routers/advisory.py"
Cohesion: 0.08
Nodes (41): AdvisoryRequest, AdvisoryResponse, DataSourceUse, _decode_limited(), FollowUpRequest, BaseModel, field_validator, TranscribeRequest (+33 more)

### Community 5 - "layout.tsx"
Cohesion: 0.11
Nodes (17): frontend_src_app_globals, beng, body, deva, display, gujr, guru, knda (+9 more)

### Community 6 - "ServiceUnavailableException"
Cohesion: 0.06
Nodes (27): ServiceUnavailableException, GeminiService, Models sometimes answer in the question's language instead of the requested…, Natural speech for `text`. Returns (16-bit mono PCM, sample rate)., untrusted(), is_in_language(), language_name(), language_rule() (+19 more)

### Community 7 - "insight-text.ts"
Cohesion: 0.20
Nodes (10): AlertView, Fmt, OUTBREAK_SEVERITY, SEVERITY_RANK, T, whenLabel(), Params, Insight (+2 more)

### Community 8 - "diagnose.py"
Cohesion: 0.29
Nodes (11): get_idempotency_result(), set_idempotency_result(), apply_safety_rules(), diagnose_base64(), diagnose_multipart(), process_diagnosis(), Post-validation rules that the model cannot override., safe_log_diagnosis() (+3 more)

### Community 9 - "api.ts"
Cohesion: 0.08
Nodes (39): CropHealthCard(), KvkCard(), SOIL_REASON, SoilProperties(), SoilRegenCard(), triggerText(), UnavailableNote(), AI_TIMEOUT_MS (+31 more)

### Community 10 - "test_kvk.py"
Cohesion: 0.16
Nodes (10): haversine_km(), KvkService, Great-circle distance in kilometres (spherical Earth, R = 6371 km)., KVK for the district nearest to (lat, lng), or None when no listed district is…, KVK lookup: never report a distance to a district reference point as a distance…, test_empty_list_returns_none(), test_haversine_known_distance(), test_haversine_zero_and_symmetry() (+2 more)

### Community 11 - "errors.py"
Cohesion: 0.15
Nodes (16): error_body(), _from_detail(), install_error_handlers(), _api_error(), _http_error(), _service_unavailable(), _validation_error(), FastAPI (+8 more)

### Community 12 - "useI18n"
Cohesion: 0.17
Nodes (21): AboutPage(), NotFound(), Bars(), CropHealthPanel(), KpiRow(), LimitationsPanel(), OutbreaksPanel(), PublishForm() (+13 more)

### Community 13 - "test_advisory.py"
Cohesion: 0.20
Nodes (17): _at(), parse_conditions(), Weather conditions from the Open-Meteo forecast API. Open-Meteo "current"…, weather_condition(), open_meteo_payload(), isolate(), fixture, run() (+9 more)

### Community 14 - "test_diagnosis.py"
Cohesion: 0.29
Nodes (16): ai_diagnosis(), post(), parametrize, test_confident_detection_includes_verified_reference(), test_healthy_has_no_disease_name(), test_low_certainty_never_suggests_chemicals(), test_multipart_png_is_sent_with_correct_mime(), test_no_location_means_no_weather_and_no_fake_coordinates() (+8 more)

### Community 15 - "validate_plantvillage.py"
Cohesion: 0.36
Nodes (7): AsyncClient, download_image(), fetch_image_list(), run_validation_suite(), random, sklearn_metrics, sys

### Community 16 - "mock-api.ts"
Cohesion: 0.14
Nodes (19): frontend_e2e_fixtures_api, leaf, notImage, API, fixtureData, Fixtures, fresh(), json() (+11 more)

### Community 17 - ".save_diagnosis"
Cohesion: 0.14
Nodes (9): _haversine(), normalize_level(), outbreak_eligible(), _public_coord(), Outbreak clusters with coordinates rounded to ~11 km. Stale clusters are…, Aggregated counts from stored records only. No external or estimated figures., Maps legacy 'Medium'/'High' values and new levels onto low | moderate | high., Only confident, located disease detections may contribute to outbreak clusters. (+1 more)

### Community 18 - "Conversation.tsx"
Cohesion: 0.18
Nodes (15): AssistantMessage(), ChatMessage, Conversation(), SourceList(), errorMessage(), ErrorState(), codeForStatus(), transcribeAudio() (+7 more)

### Community 19 - "diagnose/page.tsx"
Cohesion: 0.15
Nodes (28): AdvisorPage(), DiagnosePage(), Phase, FarmProfileForm(), useLocationLabel(), diagnoseCrop(), getAdvisory(), getFollowUpAdvisory() (+20 more)

### Community 20 - "interop.py"
Cohesion: 0.16
Nodes (17): AggregatedStateReport, BaseModel, Interoperability data models for cross-state agricultural data sharing. These…, Strip any personally identifiable information before data flows from a state-…, Standard payload for cross-state agricultural data exchange. Any state system…, Per-state configuration that adapts KrishiSathi to local context. The same…, National-level aggregation of state signals — for the policymaker dashboard., RegionalAgriSignal (+9 more)

### Community 21 - "package.json"
Cohesion: 0.13
Nodes (14): name, private, version, clsx, react-dom, tailwind-merge, tailwindcss, @tailwindcss/postcss (+6 more)

### Community 22 - "gemini_service.py"
Cohesion: 0.22
Nodes (8): All Gemini calls. Model output is treated as untrusted: * every call is async…, Text-to-speech with a native-language voice for every supported language.…, collections, google, google_genai, gtts, hashlib, re

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 24 - "dependencies"
Cohesion: 0.15
Nodes (13): dependencies, clsx, leaflet, lucide-react, next, react, react-dom, react-leaflet (+5 more)

### Community 25 - "env.py"
Cohesion: 0.18
Nodes (10): do_run_migrations(), run_async_migrations(), run_migrations_online(), Connection, logging_config, sqlalchemy_engine, sqlalchemy_ext_asyncio, sqlalchemy_orm (+2 more)

### Community 26 - "utils.ts"
Cohesion: 0.19
Nodes (13): FEATURES, Home(), WorkflowDiagram(), Header(), LanguageSelect(), MobileNav(), isActive(), NAV_ITEMS (+5 more)

### Community 27 - "main.py"
Cohesion: 0.15
Nodes (13): RequestContextMiddleware, ensure_tables(), health_live(), health_ready(), lazy_db_init(), lifespan(), FastAPI, Creates missing tables once per process. Serverless deployments (Vercel) may… (+5 more)

### Community 28 - "persistence_service.py"
Cohesion: 0.29
Nodes (10): AdvisoryRecord, DiagnosisRecord, FederationSignalRecord, OutbreakRecord, PersistenceService, asyncio, test_macro_grid_collision(), asyncio (+2 more)

### Community 29 - "eslint.config.mjs"
Cohesion: 0.50
Nodes (3): eslintConfig, eslint, eslint-config-next

### Community 30 - "rate_limit.py"
Cohesion: 0.50
Nodes (7): ai_rate_limit(), _client_ip(), _local_incr(), rate_limit(), tts_rate_limit(), redis_asyncio, Request

### Community 31 - "cn"
Cohesion: 0.13
Nodes (31): ErrorPage(), SECTIONS, DiagnosisResult(), StepList(), insightView(), outbreakView(), accent, AlertsCard() (+23 more)

### Community 32 - "ApiError"
Cohesion: 0.09
Nodes (26): ApiError, HTTPException carrying an explicit machine-readable code., get_current_user(), Principal, BaseModel, Validates an HS256 JWT signed with settings.JWT_SECRET. Fails closed: when no…, require_system_role(), get_ee_status() (+18 more)

### Community 33 - "test_p03_outbreaks.py"
Cohesion: 0.21
Nodes (15): clear_db(), asyncio, fixture, parametrize, test_diagnoses_without_location_are_recorded_but_not_clustered(), test_ineligible_diagnoses_never_form_outbreaks(), test_insufficient_observations_no_outbreak(), test_outbreak_coordinates_are_coarsened_for_privacy() (+7 more)

### Community 34 - "soil_service.py"
Cohesion: 0.18
Nodes (14): _failure(), _fetch(), parse_soilgrids(), rate_organic_carbon(), rate_ph(), Soil properties from ISRIC SoilGrids 2.0 (modelled, 250 m resolution).…, One SoilGrids query, with one retry for transient failures. Never raises., Returns an availability-tagged dict with a specific `reason` on failure; never… (+6 more)

### Community 35 - "advisory_context.py"
Cohesion: 0.22
Nodes (12): get_conditions(), Current conditions (model estimate), 7-day forecast and rule-based agro…, build_context(), _outbreaks(), Builds the DATA blocks that ground advisory answers. Sources are fetched…, _soil_text(), _weather(), _weather_text() (+4 more)

### Community 36 - "request"
Cohesion: 0.24
Nodes (16): PolicyDashboardPage(), FarmPage(), getCropHealth(), getDashboardReport(), getDashboardStats(), getExchangeSignals(), getFarmConditions(), getNearestKvk() (+8 more)

### Community 37 - "devDependencies"
Cohesion: 0.18
Nodes (11): devDependencies, eslint, eslint-config-next, @playwright/test, tailwindcss, @tailwindcss/postcss, @types/leaflet, @types/node (+3 more)

### Community 38 - "speech.ts"
Cohesion: 0.05
Nodes (40): ZERO, AdvisoryInput, getSpeechVoices(), resetReachabilityProbe(), synthesizeSpeech(), I18nValue, audioPlayer(), BCP47 (+32 more)

### Community 39 - "config.py"
Cohesion: 0.16
Nodes (5): Settings, Public description of every data source the platform uses and whether it is…, test_model_configuration_override(), BaseSettings, pydantic_settings

### Community 40 - "get"
Cohesion: 0.15
Nodes (22): get_crop_health(), get_dashboard_outbreaks(), Regional NDVI is not computed yet; say so rather than returning estimates., list_sources(), get(), fixture, SoilGrids integration: each failure mode is reported with its own reason, never…, reset() (+14 more)

### Community 41 - "manifest.json"
Cohesion: 0.22
Nodes (8): background_color, description, display, icons, name, short_name, start_url, theme_color

### Community 42 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, start, test, test:e2e, typecheck

### Community 43 - "test_earth_engine.py"
Cohesion: 0.08
Nodes (30): CredentialError, EarthEngineService, _iso_day(), parse_service_account_key(), Retry a failed start-up after a cool-down, so a transient outage does not…, Server-side dictionary for one window: median NDVI of clear pixels, scene…, Mean of the cloud-masked median Sentinel-2 NDVI over a geometry and date window., The configured key cannot be used. `code` is safe to show to operators. (+22 more)

### Community 44 - "test_intelligence.py"
Cohesion: 0.23
Nodes (15): conditions(), ids(), asyncio, Weather parsing, agro rules, soil parsing and regenerative recommendations., Regression: soil_moisture_0_to_7cm is not a forecast-API variable and broke…, test_conditions_are_cached(), test_current_values_come_from_current_block_not_midnight_hourly(), test_dry_spell() (+7 more)

### Community 45 - "exports.md"
Cohesion: 0.33
Nodes (5): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag)

### Community 46 - "github-and-merge.md"
Cohesion: 0.33
Nodes (5): Clone each repo, run the full pipeline on each, then merge, graphify reference: GitHub clone and cross-repo merge, Run /graphify on each local path to produce their graph.json files, Step 0 - Clone GitHub repo(s) (only if a GitHub URL was given), Use LOCAL_PATH as the target for all subsequent steps

### Community 47 - "query.md"
Cohesion: 0.33
Nodes (5): Find best-matching start nodes, graphify reference: query, path, explain, or: graphify query "QUESTION" --dfs --budget 3000, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 48 - "update.md"
Cohesion: 0.33
Nodes (5): For --update (incremental re-extraction), graphify reference: incremental update and cluster-only, handled by build_merge's replace-on-re-extract (#1344): every source_file in, Load new extraction and incremental state, prune_sources is ONLY for genuinely DELETED files. Changed/re-extracted files are

### Community 49 - "SKILL.md"
Cohesion: 0.33
Nodes (5): /graphify, Step 0 - GitHub repos and multi-path merge (only if a URL or several paths), Usage, What graphify is for, What You Must Do When Invoked

### Community 50 - "AGENTS.md"
Cohesion: 0.33
Nodes (5): 1. Graph-First Development, 2. Ponytail Anti-Overengineering Rules, 3. Trust, Correctness, and Data Integrity, 4. Security & Privacy, KrishiSathi Engineering Rules

### Community 51 - ".log_diagnosis"
Cohesion: 0.33
Nodes (3): Any, BigQueryService, Logs a diagnosis to BigQuery using batch load jobs to comply with Sandbox…

### Community 52 - "AUDIT.md"
Cohesion: 0.33
Nodes (5): 1. Architecture map (as found), 2. User flows traced, 3. Fallback / fabrication inventory, 4. Security risks, KrishiSathi — Repository Audit (2026-09-26)

### Community 53 - "OutbreakMap.tsx"
Cohesion: 0.33
Nodes (4): COLORS, OutbreakMap, leaflet, react-leaflet

### Community 54 - "README.md"
Cohesion: 0.33
Nodes (5): Architecture, Backend, Real data only, Running locally, What it does

### Community 56 - "transcribe.md"
Cohesion: 0.40
Nodes (4): graphify reference: transcribe video and audio, print progress to stdout, which would otherwise corrupt the JSON file (#1392)., Step 2.5 - Transcribe video / audio files (only if video files detected), Write the JSON from Python (NOT a shell '>' redirect): transcribe_all/Whisper

### Community 57 - "earth_engine_service.py"
Cohesion: 0.13
Nodes (13): asyncio, ASGI middleware: request IDs, access logging, security headers, last-resort…, Operator check: is Sentinel-2 via Earth Engine really working with these…, Sentinel-2 crop health (NDVI) from Google Earth Engine. Dataset:…, Krishi Vigyan Kendra lookup from a small static reference list. The bundled…, base64, binascii, ee (+5 more)

### Community 58 - "add-watch.md"
Cohesion: 0.50
Nodes (3): For --watch, For /graphify add, graphify reference: add a URL and watch a folder

### Community 59 - "hooks.md"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 60 - "next.config.ts"
Cohesion: 0.50
Nodes (3): apiOrigin, nextConfig, securityHeaders

### Community 61 - "frontend/README.md"
Cohesion: 0.50
Nodes (3): Getting Started, Learn More, or

### Community 79 - "datetime"
Cohesion: 0.31
Nodes (9): DiseaseAlert, OutbreakReport, BaseModel, get_alerts(), get_outbreaks(), get_personalized_alerts(), _haversine(), datetime (+1 more)

### Community 80 - "farm.py"
Cohesion: 0.19
Nodes (11): get_crop_health(), get_regenerative(), get_soil(), Farmer-facing intelligence for one location. Each endpoint degrades…, crop_group(), Canonical crop list. Used to allow-list crop inputs before they reach prompts…, Regenerative practice recommendations. Recommendations come from a fixed…, _rec() (+3 more)

### Community 81 - "test_p02_regression.py"
Cohesion: 0.27
Nodes (12): jwt_secret(), asyncio, fixture, _stats(), test_client_cannot_choose_signal_id(), test_dashboard_report_generated_from_real_stats(), test_dashboard_report_insufficient_data_skips_ai(), test_federation_broadcast_signal_round_trip() (+4 more)

### Community 84 - "diagnosis.py"
Cohesion: 0.22
Nodes (11): AIDiagnosis, DiagnosisRequest, DiagnosisResponse, DiseaseReference, BaseModel, field_validator, Shape the vision model must return. Anything else is rejected as an invalid AI…, Curated, human-verified reference entry (English), shown separately from AI… (+3 more)

### Community 85 - "i18n.tsx"
Cohesion: 0.27
Nodes (10): cache, I18nContext, interpolate(), isLanguage(), LanguageProvider(), loaders, loadMessages(), localeTag() (+2 more)

### Community 86 - "normalize_crop"
Cohesion: 0.31
Nodes (4): normalize_crop(), Returns the canonical crop name, or None for unknown/other/empty input., DiseaseReferenceService, Returns a reference entry only if the id exists (and, when a crop is known,…

### Community 88 - "dashboard.py"
Cohesion: 0.50
Nodes (6): cache_get(), cache_set(), Optional shared JSON cache on Redis. Every call degrades to a no-op when Redis…, get_dashboard_report(), get_stats(), logging

### Community 89 - "fastapi_testclient"
Cohesion: 0.25
Nodes (3): Server errors must reach the browser as errors, not as CORS failures that look…, fastapi_testclient, unittest_mock

### Community 90 - "Sentinel-2 crop health via Google Earth Engine"
Cohesion: 0.29
Nodes (6): Error codes, Limits, One-time setup, Sentinel-2 crop health via Google Earth Engine, Verify, What is computed

### Community 91 - "helpers.py"
Cohesion: 0.40
Nodes (4): Server-side image validation (never trust the client's Content-Type)., Shared test fixtures/data (imported by test modules; pytest puts this directory…, io, pil

### Community 92 - "pytest"
Cohesion: 0.33
Nodes (5): asyncio, Prove that hard-coded crop-health values are not returned., test_crop_health_unavailable(), httpx, pytest

## Knowledge Gaps
- **209 isolated node(s):** `builds`, `routes`, `leaf`, `notImage`, `API` (+204 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 472 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ServiceUnavailableException` connect `ServiceUnavailableException` to `test_security.py`, `test_failure_states.py`, `advisory_context.py`, `routers/advisory.py`, `diagnose.py`, `errors.py`, `test_intelligence.py`, `test_advisory.py`, `test_diagnosis.py`, `farm.py`, `gemini_service.py`, `get_weather_risk`, `dashboard.py`, `WeatherService`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `PersistenceService` connect `persistence_service.py` to `.save_diagnosis`, `interop.py`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Why does `react` connect `diagnose/page.tsx` to `speech.ts`, `useI18n`, `Conversation.tsx`, `package.json`, `i18n.tsx`, `utils.ts`, `cn`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `ServiceUnavailableException` (e.g. with `install_error_handlers()` and `get_weather_risk()`) actually correct?**
  _`ServiceUnavailableException` has 13 INFERRED edges - model-reasoned connections that need verification._
- **What connects `builds`, `routes`, `leaf` to the rest of the system?**
  _209 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `en.ts` be split into smaller, more focused modules?**
  _Cohesion score 0.1380952380952381 - nodes in this community are weakly interconnected._
- **Should `test_security.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0743321718931475 - nodes in this community are weakly interconnected._
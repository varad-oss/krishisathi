# Graph Report - krishisathi  (2026-09-29)

## Corpus Check
- 156 files · ~106,924 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 6, .example 2, .ini 1)

## Summary
- 1173 nodes · 2683 edges · 78 communities (59 shown, 19 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 58 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d9726163`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- i18n.tsx
- test_security.py
- test_failure_states.py
- typing
- routers/advisory.py
- layout.tsx
- test_speech_language.py
- types.ts
- diagnose.py
- api.ts
- test_kvk.py
- errors.py
- GeminiService
- farm.py
- test_intelligence.py
- validate_plantvillage.py
- mock-api.ts
- .save_diagnosis
- test_advisory.py
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
- useI18n
- ApiError
- test_p03_outbreaks.py
- advisory_context.py
- test_p02_regression.py
- devDependencies
- speech.ts
- helpers.py
- get
- manifest.json
- scripts
- EarthEngineService
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
- transcribe.md
- ServiceUnavailableException
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
- `test_gemini_speak_without_audio_is_unavailable()` --uses--> `ServiceUnavailableException`  [INFERRED]
  backend/tests/test_speech_language.py → backend/models/exceptions.py
- `get_voice_advisory()` --uses--> `ApiError`  [INFERRED]
  backend/routers/advisory.py → backend/core/errors.py
- `diagnose_multipart()` --uses--> `ApiError`  [INFERRED]
  backend/routers/diagnose.py → backend/core/errors.py

## Import Cycles
- None detected.

## Communities (78 total, 19 thin omitted)

### Community 0 - "i18n.tsx"
Cohesion: 0.11
Nodes (23): cache, I18nContext, I18nValue, interpolate(), isLanguage(), LanguageProvider(), loaders, loadMessages() (+15 more)

### Community 1 - "test_security.py"
Cohesion: 0.07
Nodes (27): ai_down(), create_token(), err(), image_payload(), MockRedis, fixture, Regression: without Redis the limiter used to be silently disabled., Regression: allow_origins used to include '*' together with credentials. (+19 more)

### Community 2 - "test_failure_states.py"
Cohesion: 0.07
Nodes (36): ai_diagnosis(), jpeg_bytes(), Server errors must reach the browser as errors, not as CORS failures that look…, post(), fixture, parametrize, reset_limits(), test_confident_detection_includes_verified_reference() (+28 more)

### Community 3 - "typing"
Cohesion: 0.09
Nodes (10): alembic, DiseaseAlert, OutbreakReport, BaseModel, get_alerts(), get_outbreaks(), get_personalized_alerts(), _haversine() (+2 more)

### Community 4 - "routers/advisory.py"
Cohesion: 0.11
Nodes (35): AdvisoryRequest, AdvisoryResponse, DataSourceUse, _decode_limited(), FollowUpRequest, BaseModel, field_validator, TranscribeRequest (+27 more)

### Community 5 - "layout.tsx"
Cohesion: 0.07
Nodes (28): frontend_src_app_globals, beng, body, deva, display, gujr, guru, knda (+20 more)

### Community 6 - "test_speech_language.py"
Cohesion: 0.07
Nodes (18): is_in_language(), Supported UI/response languages (allow-list). Codes match the frontend., Share of letters written in the language's native script (1.0 for English or…, True when the text is mostly in the native script. Technical terms (pH, NPK)…, script_ratio(), _gtts(), pcm_to_wav(), Drops Markdown symbols that voices would otherwise read out ("asterisk",… (+10 more)

### Community 7 - "types.ts"
Cohesion: 0.10
Nodes (25): AlertView, Fmt, OUTBREAK_SEVERITY, outbreakView(), SEVERITY_RANK, T, SOIL_REASON, SoilProperties() (+17 more)

### Community 8 - "diagnose.py"
Cohesion: 0.14
Nodes (23): get_idempotency_result(), set_idempotency_result(), AIDiagnosis, DiagnosisRequest, DiagnosisResponse, DiseaseReference, BaseModel, field_validator (+15 more)

### Community 9 - "api.ts"
Cohesion: 0.07
Nodes (48): PolicyDashboardPage(), FarmPage(), Bars(), CropHealthPanel(), KpiRow(), LimitationsPanel(), OutbreaksPanel(), PublishForm() (+40 more)

### Community 10 - "test_kvk.py"
Cohesion: 0.14
Nodes (12): haversine_km(), KvkService, Krishi Vigyan Kendra lookup from a small static reference list. The bundled…, Great-circle distance in kilometres (spherical Earth, R = 6371 km)., KVK for the district nearest to (lat, lng), or None when no listed district is…, KVK lookup: never report a distance to a district reference point as a distance…, test_empty_list_returns_none(), test_haversine_known_distance() (+4 more)

### Community 11 - "errors.py"
Cohesion: 0.12
Nodes (19): error_body(), _from_detail(), install_error_handlers(), _api_error(), _http_error(), _service_unavailable(), _validation_error(), FastAPI (+11 more)

### Community 12 - "GeminiService"
Cohesion: 0.29
Nodes (5): GeminiService, Models sometimes answer in the question's language instead of the requested…, Natural speech for `text`. Returns (16-bit mono PCM, sample rate)., untrusted(), language_name()

### Community 13 - "farm.py"
Cohesion: 0.13
Nodes (14): get_crop_health(), get_regenerative(), get_soil(), Farmer-facing intelligence for one location. Each endpoint degrades…, crop_group(), normalize_crop(), Canonical crop list. Used to allow-list crop inputs before they reach prompts…, Returns the canonical crop name, or None for unknown/other/empty input. (+6 more)

### Community 14 - "test_intelligence.py"
Cohesion: 0.18
Nodes (21): parse_soilgrids(), rate_organic_carbon(), rate_ph(), Soil Health Card organic-carbon classes: <0.5 % low, 0.5–0.75 % medium, >0.75 %…, conditions(), ids(), Weather parsing, agro rules, soil parsing and regenerative recommendations., Regression: soil_moisture_0_to_7cm is not a forecast-API variable and broke… (+13 more)

### Community 15 - "validate_plantvillage.py"
Cohesion: 0.22
Nodes (11): AsyncClient, download_image(), fetch_image_list(), run_validation_suite(), Server-side image validation (never trust the client's Content-Type)., Validates the bytes are a real, reasonably sized JPEG/PNG/WebP image; returns…, sniff_image(), io (+3 more)

### Community 16 - "mock-api.ts"
Cohesion: 0.14
Nodes (19): frontend_e2e_fixtures_api, leaf, notImage, API, fixtureData, Fixtures, fresh(), json() (+11 more)

### Community 17 - ".save_diagnosis"
Cohesion: 0.14
Nodes (9): _haversine(), normalize_level(), outbreak_eligible(), _public_coord(), Outbreak clusters with coordinates rounded to ~11 km. Stale clusters are…, Aggregated counts from stored records only. No external or estimated figures., Maps legacy 'Medium'/'High' values and new levels onto low | moderate | high., Only confident, located disease detections may contribute to outbreak clusters. (+1 more)

### Community 18 - "test_advisory.py"
Cohesion: 0.17
Nodes (19): _at(), parse_conditions(), Weather conditions from the Open-Meteo forecast API. Open-Meteo "current"…, weather_condition(), open_meteo_payload(), isolate(), fixture, run() (+11 more)

### Community 19 - "diagnose/page.tsx"
Cohesion: 0.13
Nodes (29): AdvisorPage(), DiagnosePage(), Phase, ErrorPage(), AssistantMessage(), ChatMessage, Conversation(), SourceList() (+21 more)

### Community 20 - "interop.py"
Cohesion: 0.15
Nodes (18): AggregatedStateReport, BaseModel, Interoperability data models for cross-state agricultural data sharing. These…, Strip any personally identifiable information before data flows from a state-…, Standard payload for cross-state agricultural data exchange. Any state system…, Per-state configuration that adapts KrishiSathi to local context. The same…, National-level aggregation of state signals — for the policymaker dashboard., RegionalAgriSignal (+10 more)

### Community 21 - "package.json"
Cohesion: 0.13
Nodes (14): name, private, version, clsx, react-dom, tailwind-merge, tailwindcss, @tailwindcss/postcss (+6 more)

### Community 22 - "gemini_service.py"
Cohesion: 0.10
Nodes (28): asyncio, cache_get(), cache_set(), Optional shared JSON cache on Redis. Every call degrades to a no-op when Redis…, get_dashboard_outbreaks(), get_dashboard_report(), get_stats(), Public description of every data source the platform uses and whether it is… (+20 more)

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
Cohesion: 0.16
Nodes (15): NotFound(), FEATURES, Home(), WorkflowDiagram(), Header(), LanguageSelect(), MobileNav(), isActive() (+7 more)

### Community 27 - "main.py"
Cohesion: 0.18
Nodes (12): ensure_tables(), health_live(), health_ready(), lazy_db_init(), lifespan(), FastAPI, Creates missing tables once per process. Serverless deployments (Vercel) may…, root() (+4 more)

### Community 28 - "persistence_service.py"
Cohesion: 0.23
Nodes (14): AdvisoryRecord, DiagnosisRecord, FederationSignalRecord, OutbreakRecord, PersistenceService, clear_db(), fixture, asyncio (+6 more)

### Community 29 - "eslint.config.mjs"
Cohesion: 0.50
Nodes (3): eslintConfig, eslint, eslint-config-next

### Community 30 - "rate_limit.py"
Cohesion: 0.50
Nodes (7): ai_rate_limit(), _client_ip(), _local_incr(), rate_limit(), tts_rate_limit(), redis_asyncio, Request

### Community 31 - "useI18n"
Cohesion: 0.11
Nodes (44): AboutPage(), SECTIONS, DiagnosisResult(), StepList(), insightView(), whenLabel(), CropHealthCard(), KvkCard() (+36 more)

### Community 32 - "ApiError"
Cohesion: 0.16
Nodes (16): ApiError, HTTPException carrying an explicit machine-readable code., get_current_user(), Principal, BaseModel, Validates an HS256 JWT signed with settings.JWT_SECRET. Fails closed: when no…, require_system_role(), get_nearest_kvk() (+8 more)

### Community 33 - "test_p03_outbreaks.py"
Cohesion: 0.25
Nodes (13): asyncio, parametrize, test_diagnoses_without_location_are_recorded_but_not_clustered(), test_ineligible_diagnoses_never_form_outbreaks(), test_insufficient_observations_no_outbreak(), test_outbreak_coordinates_are_coarsened_for_privacy(), test_outside_radius_separate_cluster(), test_outside_time_window_not_grouped() (+5 more)

### Community 35 - "advisory_context.py"
Cohesion: 0.22
Nodes (12): get_conditions(), Current conditions (model estimate), 7-day forecast and rule-based agro…, build_context(), _outbreaks(), Builds the DATA blocks that ground advisory answers. Sources are fetched…, _soil_text(), _weather(), _weather_text() (+4 more)

### Community 36 - "test_p02_regression.py"
Cohesion: 0.24
Nodes (13): jwt_secret(), asyncio, fixture, _stats(), test_client_cannot_choose_signal_id(), test_dashboard_report_generated_from_real_stats(), test_dashboard_report_insufficient_data_skips_ai(), test_federation_broadcast_signal_round_trip() (+5 more)

### Community 37 - "devDependencies"
Cohesion: 0.18
Nodes (11): devDependencies, eslint, eslint-config-next, @playwright/test, tailwindcss, @tailwindcss/postcss, @types/leaflet, @types/node (+3 more)

### Community 38 - "speech.ts"
Cohesion: 0.06
Nodes (41): ZERO, AdvisoryInput, getSpeechVoices(), synthesizeSpeech(), transcribeAudio(), audioPlayer(), cleanup(), BCP47 (+33 more)

### Community 39 - "helpers.py"
Cohesion: 0.13
Nodes (10): Settings, Shared test fixtures/data (imported by test modules; pytest puts this directory…, asyncio, Prove that hard-coded crop-health values are not returned., test_crop_health_unavailable(), test_model_configuration_override(), BaseSettings, os (+2 more)

### Community 40 - "get"
Cohesion: 0.09
Nodes (31): get_crop_health(), get_weather_risk(), Regional NDVI is not computed yet; say so rather than returning estimates., Rule-based forecast risks at one reference point per state (indicative, not…, get_ee_status(), Authenticated check of the Earth Engine pipeline status., list_sources(), get_exchange_signals() (+23 more)

### Community 41 - "manifest.json"
Cohesion: 0.22
Nodes (8): background_color, description, display, icons, name, short_name, start_url, theme_color

### Community 42 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, start, test, test:e2e, typecheck

### Community 43 - "EarthEngineService"
Cohesion: 0.33
Nodes (3): EarthEngineService, Mean of the median Sentinel-2 NDVI over a geometry and date window., date

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

### Community 57 - "ServiceUnavailableException"
Cohesion: 0.24
Nodes (7): ServiceUnavailableException, Compact current-conditions dict used as AI context and by the legacy…, WeatherService, test_regenerative_endpoint_reports_inputs(), test_all_providers_failing_is_503_not_wrong_voice(), test_gemini_failure_falls_back_to_native_gtts_voice(), Exception

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

## Knowledge Gaps
- **204 isolated node(s):** `builds`, `routes`, `leaf`, `notImage`, `API` (+199 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 449 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ServiceUnavailableException` connect `ServiceUnavailableException` to `test_security.py`, `test_failure_states.py`, `advisory_context.py`, `routers/advisory.py`, `test_speech_language.py`, `get`, `diagnose.py`, `errors.py`, `GeminiService`, `farm.py`, `test_intelligence.py`, `test_advisory.py`, `gemini_service.py`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `react` connect `diagnose/page.tsx` to `i18n.tsx`, `layout.tsx`, `speech.ts`, `api.ts`, `package.json`, `utils.ts`, `useI18n`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Why does `@playwright/test` connect `mock-api.ts` to `package.json`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `ServiceUnavailableException` (e.g. with `install_error_handlers()` and `get_weather_risk()`) actually correct?**
  _`ServiceUnavailableException` has 13 INFERRED edges - model-reasoned connections that need verification._
- **What connects `builds`, `routes`, `leaf` to the rest of the system?**
  _204 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `i18n.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.1051693404634581 - nodes in this community are weakly interconnected._
- **Should `test_security.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0743321718931475 - nodes in this community are weakly interconnected._
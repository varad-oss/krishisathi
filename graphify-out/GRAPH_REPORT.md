# Graph Report - KrishiSathi  (2026-09-29)

## Corpus Check
- 164 files · ~181,018 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 6, .example 2, .ini 1)

## Summary
- 1050 nodes · 2369 edges · 84 communities (61 shown, 23 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 50 edges (avg confidence: 0.94)
- Token cost: 1,000 input · 1,000 output

## Community Hubs (Navigation)
- Frontend Src
- Backend Tests
- Backend Tests
- Backend Migrations
- Backend Models
- Frontend Src
- Frontend Src
- Frontend Src
- Backend Models
- Frontend Src
- Frontend Src
- Backend Core
- Backend Services
- Backend Services
- Backend Tests
- Backend Services
- Frontend E2E
- Backend Services
- Backend Tests
- Frontend Src
- Backend Models
- Ref Types
- Backend Core
- Frontend Tsconfig
- Frontend Package
- Backend Migrations
- Frontend Src
- Backend Main
- Backend Tests
- Frontend Src
- Backend Core
- Frontend Src
- Backend Core
- Backend Tests
- Backend Routers
- Backend Services
- Backend Tests
- Frontend Package
- Frontend Tests
- Backend Tests
- Backend Routers
- Frontend Public
- Frontend Package
- Backend Services
- Frontend Src
-  Agents
-  Agents
-  Agents
-  Agents
-  Agents
- Agents 1
- Backend Services
- Docs Audit
- Frontend Src
- Readme Architecture
- Report P6
-  Agents
- Backend Services
-  Agents
-  Agents
- Frontend Next
- Frontend Readme
- Frontend Src
- Backend Vercel
-  Agents
-  Agents
-  Agents
-  Agents
- Backend Requirements
- Frontend Agents
- Frontend Postcss

## God Nodes (most connected - your core abstractions)
1. `useI18n()` - 64 edges
2. `cn()` - 37 edges
3. `ServiceUnavailableException` - 36 edges
4. `ApiError` - 22 edges
5. `post()` - 21 edges
6. `request()` - 20 edges
7. `MessageKey` - 18 edges
8. `lucide-react` - 16 edges
9. `react` - 16 edges
10. `ApiError` - 16 edges

## Surprising Connections (you probably didn't know these)
- `test_weather_failure_raises_exception()` --uses--> `ServiceUnavailableException`  [INFERRED]
  backend/tests/test_failure_states.py → backend/models/exceptions.py
- `test_weather_timeout_has_specific_message()` --uses--> `ServiceUnavailableException`  [INFERRED]
  backend/tests/test_failure_states.py → backend/models/exceptions.py
- `get_voice_advisory()` --uses--> `ApiError`  [INFERRED]
  backend/routers/advisory.py → backend/core/errors.py
- `diagnose_multipart()` --uses--> `ApiError`  [INFERRED]
  backend/routers/diagnose.py → backend/core/errors.py
- `get_state_config()` --uses--> `ApiError`  [INFERRED]
  backend/routers/states.py → backend/core/errors.py

## Import Cycles
- None detected.

## Communities (84 total, 23 thin omitted)

### Community 0 - "Frontend Src"
Cohesion: 0.08
Nodes (31): AlertView, Fmt, OUTBREAK_SEVERITY, SEVERITY_RANK, T, whenLabel(), cache, I18nContext (+23 more)

### Community 1 - "Backend Tests"
Cohesion: 0.07
Nodes (27): ai_down(), create_token(), err(), image_payload(), MockRedis, fixture, Regression: without Redis the limiter used to be silently disabled., Regression: allow_origins used to include '*' together with credentials. (+19 more)

### Community 2 - "Backend Tests"
Cohesion: 0.09
Nodes (34): ai_diagnosis(), jpeg_bytes(), post(), fixture, parametrize, reset_limits(), test_confident_detection_includes_verified_reference(), test_healthy_has_no_disease_name() (+26 more)

### Community 3 - "Backend Migrations"
Cohesion: 0.09
Nodes (10): alembic, DiseaseAlert, OutbreakReport, BaseModel, get_alerts(), get_outbreaks(), get_personalized_alerts(), _haversine() (+2 more)

### Community 4 - "Backend Models"
Cohesion: 0.13
Nodes (27): AdvisoryRequest, AdvisoryResponse, DataSourceUse, _decode_limited(), FollowUpRequest, BaseModel, field_validator, TranscribeRequest (+19 more)

### Community 5 - "Frontend Src"
Cohesion: 0.10
Nodes (23): frontend_src_app_globals, metadata, outfit, viewport, Providers(), Footer(), Header(), Logo() (+15 more)

### Community 6 - "Frontend Src"
Cohesion: 0.16
Nodes (23): ErrorPage(), NotFound(), insightView(), WeatherMeaning(), Bars(), CropHealthPanel(), KpiRow(), LimitationsPanel() (+15 more)

### Community 7 - "Frontend Src"
Cohesion: 0.09
Nodes (26): SoilProperties(), SoilRegenCard(), triggerText(), UnavailableNote(), AdvisoryResponse, CropHealth, CurrentConditions, DashboardReport (+18 more)

### Community 8 - "Backend Models"
Cohesion: 0.15
Nodes (20): get_idempotency_result(), set_idempotency_result(), DiagnosisRequest, DiagnosisResponse, DiseaseReference, BaseModel, field_validator, Curated, human-verified reference entry (English), shown separately from AI… (+12 more)

### Community 9 - "Frontend Src"
Cohesion: 0.18
Nodes (25): PolicyDashboardPage(), FarmPage(), AI_TIMEOUT_MS, API_BASE, ApiErrorCode, diagnoseCrop(), getAdvisory(), getCropHealth() (+17 more)

### Community 10 - "Frontend Src"
Cohesion: 0.18
Nodes (23): AssistantMessage(), Conversation(), SourceList(), DiagnosisResult(), StepList(), Card(), errorMessage(), ErrorState() (+15 more)

### Community 11 - "Backend Core"
Cohesion: 0.11
Nodes (23): error_body(), _from_detail(), install_error_handlers(), _api_error(), _http_error(), _service_unavailable(), _validation_error(), FastAPI (+15 more)

### Community 12 - "Backend Services"
Cohesion: 0.15
Nodes (12): AIDiagnosis, Shape the vision model must return. Anything else is rejected as an invalid AI…, ServiceUnavailableException, GeminiService, All Gemini calls. Model output is treated as untrusted: * every call is async…, untrusted(), language_name(), Supported UI/response languages (allow-list). Codes match the frontend. (+4 more)

### Community 13 - "Backend Services"
Cohesion: 0.13
Nodes (17): get_conditions(), get_crop_health(), get_regenerative(), get_soil(), get, Farmer-facing intelligence for one location. Each endpoint degrades…, Current conditions (model estimate), 7-day forecast and rule-based agro…, crop_group() (+9 more)

### Community 14 - "Backend Tests"
Cohesion: 0.15
Nodes (23): parse_soilgrids(), rate_organic_carbon(), rate_ph(), Returns an availability-tagged dict; never raises for upstream failures., Soil Health Card organic-carbon classes: <0.5 % low, 0.5–0.75 % medium, >0.75 %…, SoilService, conditions(), ids() (+15 more)

### Community 15 - "Backend Services"
Cohesion: 0.12
Nodes (14): AsyncClient, download_image(), fetch_image_list(), run_validation_suite(), Server-side image validation (never trust the client's Content-Type)., KvkService, Shared test fixtures/data (imported by test modules; pytest puts this directory…, io (+6 more)

### Community 16 - "Frontend E2E"
Cohesion: 0.14
Nodes (18): frontend_e2e_fixtures_api, leaf, notImage, API, fixtureData, Fixtures, fresh(), json() (+10 more)

### Community 17 - "Backend Services"
Cohesion: 0.14
Nodes (13): AdvisoryRecord, FederationSignalRecord, _haversine(), normalize_level(), outbreak_eligible(), PersistenceService, _public_coord(), Outbreak clusters with coordinates rounded to ~11 km. Stale clusters are… (+5 more)

### Community 18 - "Backend Tests"
Cohesion: 0.16
Nodes (20): _at(), parse_conditions(), Weather conditions from the Open-Meteo forecast API. Open-Meteo "current"…, weather_condition(), open_meteo_payload(), isolate(), fixture, run() (+12 more)

### Community 19 - "Frontend Src"
Cohesion: 0.25
Nodes (17): AdvisorPage(), DiagnosePage(), Phase, ChatMessage, FarmProfileForm(), useLocationLabel(), buttonClass, Note() (+9 more)

### Community 20 - "Backend Models"
Cohesion: 0.15
Nodes (18): AggregatedStateReport, BaseModel, Interoperability data models for cross-state agricultural data sharing. These…, Strip any personally identifiable information before data flows from a state-…, Standard payload for cross-state agricultural data exchange. Any state system…, Per-state configuration that adapts KrishiSathi to local context. The same…, National-level aggregation of state signals — for the policymaker dashboard., RegionalAgriSignal (+10 more)

### Community 21 - "Ref Types"
Cohesion: 0.10
Nodes (19): eslintConfig, name, private, version, clsx, eslint, eslint-config-next, react-dom (+11 more)

### Community 22 - "Backend Core"
Cohesion: 0.14
Nodes (11): asyncio, resolve_request_id(), ASGI middleware: request IDs, access logging, security headers, last-resort…, RequestContextMiddleware, Soil properties from ISRIC SoilGrids 2.0 (modelled, 250 m resolution).…, ee, google_cloud, json (+3 more)

### Community 23 - "Frontend Tsconfig"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 24 - "Frontend Package"
Cohesion: 0.11
Nodes (18): dependencies, clsx, leaflet, lucide-react, next, react, react-dom, react-leaflet (+10 more)

### Community 25 - "Backend Migrations"
Cohesion: 0.15
Nodes (11): do_run_migrations(), run_async_migrations(), run_migrations_online(), Connection, logging_config, sqlalchemy, sqlalchemy_engine, sqlalchemy_ext_asyncio (+3 more)

### Community 26 - "Frontend Src"
Cohesion: 0.17
Nodes (12): FEATURES, Home(), HeroSection(), LanguageSelect(), AdvisoryInput, I18nValue, SUPPORTED_LANGUAGES, Language (+4 more)

### Community 27 - "Backend Main"
Cohesion: 0.17
Nodes (14): ensure_tables(), health_live(), health_ready(), lazy_db_init(), lifespan(), FastAPI, get, Creates missing tables once per process. Serverless deployments (Vercel) may… (+6 more)

### Community 28 - "Backend Tests"
Cohesion: 0.21
Nodes (13): DiagnosisRecord, OutbreakRecord, asyncio, Prove that hard-coded crop-health values are not returned., test_crop_health_unavailable(), clear_db(), fixture, asyncio (+5 more)

### Community 29 - "Frontend Src"
Cohesion: 0.23
Nodes (10): Canvas, WheatFieldCanvas(), WheatFieldScene, WheatFieldScene(), WHEAT_CONFIG, createWheatGeometry(), customWheatMaterial, @react-three/drei (+2 more)

### Community 30 - "Backend Core"
Cohesion: 0.22
Nodes (12): ApiError, HTTPException carrying an explicit machine-readable code., ai_rate_limit(), _client_ip(), _local_incr(), rate_limit(), tts_rate_limit(), get_nearest_kvk() (+4 more)

### Community 31 - "Frontend Src"
Cohesion: 0.19
Nodes (12): SECTIONS, outbreakView(), CropHealthCard(), KvkCard(), AlertsCard(), TodayCard(), useAlertViews(), WeatherCard() (+4 more)

### Community 32 - "Backend Core"
Cohesion: 0.18
Nodes (12): get_current_user(), Principal, BaseModel, Validates an HS256 JWT signed with settings.JWT_SECRET. Fails closed: when no…, require_system_role(), get_ee_status(), get, Authenticated check of the Earth Engine pipeline status. (+4 more)

### Community 33 - "Backend Tests"
Cohesion: 0.25
Nodes (13): asyncio, parametrize, test_diagnoses_without_location_are_recorded_but_not_clustered(), test_ineligible_diagnoses_never_form_outbreaks(), test_insufficient_observations_no_outbreak(), test_outbreak_coordinates_are_coarsened_for_privacy(), test_outside_radius_separate_cluster(), test_outside_time_window_not_grouped() (+5 more)

### Community 34 - "Backend Routers"
Cohesion: 0.26
Nodes (10): _cache_get(), _cache_set(), get_crop_health(), get_dashboard_outbreaks(), get_dashboard_report(), get_stats(), get_weather_risk(), get (+2 more)

### Community 35 - "Backend Services"
Cohesion: 0.26
Nodes (11): build_context(), _haversine(), _outbreaks(), Builds the DATA blocks that ground advisory answers. Sources are fetched…, _soil_text(), _weather(), _weather_text(), evaluate() (+3 more)

### Community 36 - "Backend Tests"
Cohesion: 0.27
Nodes (12): jwt_secret(), asyncio, fixture, _stats(), test_client_cannot_choose_signal_id(), test_dashboard_report_generated_from_real_stats(), test_dashboard_report_insufficient_data_skips_ai(), test_federation_broadcast_signal_round_trip() (+4 more)

### Community 37 - "Frontend Package"
Cohesion: 0.18
Nodes (11): devDependencies, eslint, eslint-config-next, @playwright/test, tailwindcss, @tailwindcss/postcss, @types/leaflet, @types/node (+3 more)

### Community 38 - "Frontend Tests"
Cohesion: 0.22
Nodes (6): ZERO, en, ref_node_assert, ref_node_child_process, ref_node_fs, ref_node_test

### Community 39 - "Backend Tests"
Cohesion: 0.22
Nodes (3): Settings, test_model_configuration_override(), BaseSettings

### Community 40 - "Backend Routers"
Cohesion: 0.22
Nodes (7): list_sources(), get, Public description of every data source the platform uses and whether it is…, get_current_weather(), get_forecast(), get, fastapi

### Community 41 - "Frontend Public"
Cohesion: 0.22
Nodes (8): background_color, description, display, icons, name, short_name, start_url, theme_color

### Community 42 - "Frontend Package"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, start, test, test:e2e, typecheck

### Community 43 - "Backend Services"
Cohesion: 0.33
Nodes (3): EarthEngineService, Mean of the median Sentinel-2 NDVI over a geometry and date window., date

### Community 44 - "Frontend Src"
Cohesion: 0.48
Nodes (4): AboutPage(), ApiError, getSources(), useResource()

### Community 45 - " Agents"
Cohesion: 0.33
Nodes (5): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag)

### Community 46 - " Agents"
Cohesion: 0.33
Nodes (5): Clone each repo, run the full pipeline on each, then merge, graphify reference: GitHub clone and cross-repo merge, Run /graphify on each local path to produce their graph.json files, Step 0 - Clone GitHub repo(s) (only if a GitHub URL was given), Use LOCAL_PATH as the target for all subsequent steps

### Community 47 - " Agents"
Cohesion: 0.33
Nodes (5): Find best-matching start nodes, graphify reference: query, path, explain, or: graphify query "QUESTION" --dfs --budget 3000, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 48 - " Agents"
Cohesion: 0.33
Nodes (5): For --update (incremental re-extraction), graphify reference: incremental update and cluster-only, handled by build_merge's replace-on-re-extract (#1344): every source_file in, Load new extraction and incremental state, prune_sources is ONLY for genuinely DELETED files. Changed/re-extracted files are

### Community 49 - " Agents"
Cohesion: 0.33
Nodes (5): /graphify, Step 0 - GitHub repos and multi-path merge (only if a URL or several paths), Usage, What graphify is for, What You Must Do When Invoked

### Community 50 - "Agents 1"
Cohesion: 0.33
Nodes (5): 1. Graph-First Development, 2. Ponytail Anti-Overengineering Rules, 3. Trust, Correctness, and Data Integrity, 4. Security & Privacy, KrishiSathi Engineering Rules

### Community 51 - "Backend Services"
Cohesion: 0.33
Nodes (3): Any, BigQueryService, Logs a diagnosis to BigQuery using batch load jobs to comply with Sandbox…

### Community 52 - "Docs Audit"
Cohesion: 0.33
Nodes (5): 1. Architecture map (as found), 2. User flows traced, 3. Fallback / fabrication inventory, 4. Security risks, KrishiSathi — Repository Audit (2026-09-26)

### Community 53 - "Frontend Src"
Cohesion: 0.33
Nodes (4): COLORS, OutbreakMap, leaflet, react-leaflet

### Community 54 - "Readme Architecture"
Cohesion: 0.33
Nodes (5): Architecture, Backend, Real data only, Running locally, What it does

### Community 55 - "Report P6"
Cohesion: 0.33
Nodes (5): Docker, P6 Verification, PostgreSQL, Remote Reconciliation, Tests

### Community 56 - " Agents"
Cohesion: 0.40
Nodes (4): graphify reference: transcribe video and audio, print progress to stdout, which would otherwise corrupt the JSON file (#1392)., Step 2.5 - Transcribe video / audio files (only if video files detected), Write the JSON from Python (NOT a shell '>' redirect): transcribe_all/Whisper

### Community 58 - " Agents"
Cohesion: 0.50
Nodes (3): For --watch, For /graphify add, graphify reference: add a URL and watch a folder

### Community 59 - " Agents"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 60 - "Frontend Next"
Cohesion: 0.50
Nodes (3): apiOrigin, nextConfig, securityHeaders

### Community 61 - "Frontend Readme"
Cohesion: 0.50
Nodes (3): Getting Started, Learn More, or

## Knowledge Gaps
- **195 isolated node(s):** `builds`, `routes`, `leaf`, `notImage`, `API` (+190 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 397 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `react` connect `Frontend Src` to `Frontend Src`, `Frontend Src`, `Frontend Src`, `Frontend Src`, `Frontend Src`, `Ref Types`, `Frontend Src`, `Frontend Src`, `Frontend Src`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Why does `ServiceUnavailableException` connect `Backend Services` to `Backend Tests`, `Backend Routers`, `Backend Services`, `Backend Tests`, `Backend Models`, `Backend Core`, `Backend Services`, `Backend Tests`, `Backend Tests`, `Backend Services`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Why does `@playwright/test` connect `Frontend E2E` to `Ref Types`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `ServiceUnavailableException` (e.g. with `install_error_handlers()` and `get_weather_risk()`) actually correct?**
  _`ServiceUnavailableException` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `ApiError` (e.g. with `get_voice_advisory()` and `diagnose_multipart()`) actually correct?**
  _`ApiError` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `builds`, `routes`, `leaf` to the rest of the system?**
  _195 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Frontend Src` be split into smaller, more focused modules?**
  _Cohesion score 0.07751937984496124 - nodes in this community are weakly interconnected._
# Graph Report - krishisathi  (2026-09-30)

## Corpus Check
- 189 files · ~149,448 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 6, .example 2, .ini 1)

## Summary
- 1758 nodes · 4342 edges · 100 communities (78 shown, 22 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 179 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `737418f4`
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
- TodayAlertsWeather.tsx
- diagnose.py
- types.ts
- test_kvk.py
- errors.py
- useI18n
- test_advisory.py
- test_farm_intelligence.py
- validate_plantvillage.py
- mock-api.ts
- persistence_service.py
- india.py
- diagnose/page.tsx
- interop.py
- package.json
- gemini_service.py
- compilerOptions
- dependencies
- schema.py
- farm_twin.py
- main.py
- DiagnosisRecord
- eslint.config.mjs
- rate_limit.py
- cn
- ApiError
- test_p03_outbreaks.py
- soil_service.py
- advisory_context.py
- api.ts
- devDependencies
- speech.ts
- config.py
- test_soil.py
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
- EarthEngineService
- transcribe.md
- earth_engine_service.py
- add-watch.md
- hooks.md
- interoperability.py
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
- federation.py
- DiseaseReferenceService
- farms.py
- test_farm_twin.py
- test_interoperability.py
- api.test.mjs
- parse_service_account_key
- classify_error
- ServiceUnavailableException
- _point_with
- measurement.py
- conftest.py
- get_farm_intelligence
- ._cached
- test_live_sentinel2_ndvi_for_a_ludhiana_wheat_field

## God Nodes (most connected - your core abstractions)
1. `useI18n()` - 78 edges
2. `cn()` - 58 edges
3. `ServiceUnavailableException` - 49 edges
4. `post()` - 33 edges
5. `ApiError` - 32 edges
6. `EarthEngineService` - 31 edges
7. `request()` - 31 edges
8. `FarmContext` - 28 edges
9. `ai_diagnosis()` - 24 edges
10. `ctx()` - 24 edges

## Surprising Connections (you probably didn't know these)
- `API (`backend/routers/interoperability.py`)` --references--> `RiskSignalV1`  [INFERRED]
  docs/INTEROPERABILITY.md → backend/models/interop_v1.py
- `Source status` --references--> `unavailable()`  [INFERRED]
  docs/EARTH_ENGINE.md → frontend/e2e/mock-api.ts
- `Inputs and their status` --references--> `unavailable()`  [INFERRED]
  docs/INTELLIGENCE.md → frontend/e2e/mock-api.ts
- `Risks` --references--> `unavailable()`  [INFERRED]
  docs/INTELLIGENCE.md → frontend/e2e/mock-api.ts
- `What matters today` --references--> `unavailable()`  [INFERRED]
  docs/INTELLIGENCE.md → frontend/e2e/mock-api.ts

## Import Cycles
- None detected.

## Communities (100 total, 22 thin omitted)

### Community 0 - "i18n.tsx"
Cohesion: 0.09
Nodes (29): AlertView, Fmt, T, cache, I18nContext, I18nValue, interpolate(), isLanguage() (+21 more)

### Community 1 - "test_security.py"
Cohesion: 0.07
Nodes (27): ai_down(), create_token(), err(), image_payload(), MockRedis, fixture, Regression: without Redis the limiter used to be silently disabled., Regression: allow_origins used to include '*' together with credentials. (+19 more)

### Community 2 - "test_failure_states.py"
Cohesion: 0.09
Nodes (18): jpeg_bytes(), Shared test fixtures/data (imported by test modules; pytest puts this directory…, Server errors must reach the browser as errors, not as CORS failures that look…, test_tiny_image_rejected(), clear_caches(), asyncio, fixture, parametrize (+10 more)

### Community 4 - "routers/advisory.py"
Cohesion: 0.07
Nodes (60): AdvisoryRequest, AdvisoryResponse, DataSourceUse, _decode_limited(), FollowUpRequest, BaseModel, field_validator, TranscribeRequest (+52 more)

### Community 5 - "layout.tsx"
Cohesion: 0.09
Nodes (26): apiOrigin, nextConfig, securityHeaders, frontend_src_app_globals, beng, body, deva, display (+18 more)

### Community 6 - "test_speech_language.py"
Cohesion: 0.06
Nodes (27): GeminiService, Models sometimes answer in the question's language instead of the requested…, Natural speech for `text`. Returns (16-bit mono PCM, sample rate)., untrusted(), is_in_language(), language_name(), language_rule(), Supported UI/response languages (allow-list). Codes match the frontend. (+19 more)

### Community 7 - "TodayAlertsWeather.tsx"
Cohesion: 0.08
Nodes (41): FarmHistoryCard(), whenLabel(), DataQualityStrip(), DQ_ICON, dqTone(), EvidenceList(), RiskRadar(), RiskRow() (+33 more)

### Community 8 - "diagnose.py"
Cohesion: 0.13
Nodes (27): get_idempotency_result(), set_idempotency_result(), diagnose_base64(), diagnose_multipart(), _farm(), _farm_block(), _nearby(), process_diagnosis() (+19 more)

### Community 9 - "types.ts"
Cohesion: 0.07
Nodes (32): CropHealthCard(), KvkCard(), Radar(), SatelliteHistory(), SOIL_REASON, SoilProperties(), SoilRegenCard(), triggerText() (+24 more)

### Community 10 - "test_kvk.py"
Cohesion: 0.09
Nodes (23): DiseaseAlert, OutbreakReport, BaseModel, get_alerts(), get_outbreaks(), get_personalized_alerts(), get, crop_options() (+15 more)

### Community 11 - "errors.py"
Cohesion: 0.15
Nodes (16): error_body(), _from_detail(), install_error_handlers(), _api_error(), _http_error(), _service_unavailable(), _validation_error(), FastAPI (+8 more)

### Community 12 - "useI18n"
Cohesion: 0.10
Nodes (36): AboutPage(), ErrorPage(), NotFound(), ActionFeedback(), Choices(), FOLLOWED, OUTCOMES, insightView() (+28 more)

### Community 13 - "test_advisory.py"
Cohesion: 0.21
Nodes (16): parse_conditions(), open_meteo_payload(), isolate(), fixture, run(), test_advisory_degrades_when_weather_unavailable(), test_advisory_is_grounded_and_lists_sources(), test_ai_failure_is_503() (+8 more)

### Community 14 - "test_farm_intelligence.py"
Cohesion: 0.07
Nodes (79): Evidence, FarmInput, BaseModel, Risk, RuleRef, TopAction, estimate_stage(), date (+71 more)

### Community 15 - "validate_plantvillage.py"
Cohesion: 0.20
Nodes (12): AsyncClient, download_image(), fetch_image_list(), run_validation_suite(), Server-side image validation (never trust the client's Content-Type)., Validates the bytes are a real, reasonably sized JPEG/PNG/WebP image; returns…, sniff_image(), io (+4 more)

### Community 16 - "mock-api.ts"
Cohesion: 0.05
Nodes (43): EscalationSink, NotConnectedSink, Protocol, No extension system is integrated yet: the case is returned to the farmer to…, Where a case goes. A KVK or state extension system implements `submit` and…, Error codes, History series, Limits (+35 more)

### Community 17 - "persistence_service.py"
Cohesion: 0.11
Nodes (17): Standard payload for cross-state agricultural data exchange. Any state system…, RegionalAgriSignal, AdvisoryRecord, FederationSignalRecord, _haversine(), normalize_level(), outbreak_eligible(), PersistenceService (+9 more)

### Community 18 - "india.py"
Cohesion: 0.06
Nodes (55): AdvisoryV1, CropV1, DiseaseV1, FarmerRefV1, FarmV1, GeoRefV1, GridCellV1, json_schemas() (+47 more)

### Community 19 - "diagnose/page.tsx"
Cohesion: 0.11
Nodes (37): AdvisorPage(), DiagnosePage(), Phase, FarmProfileForm(), useLocationLabel(), inputClass, createFarm(), diagnoseCrop() (+29 more)

### Community 20 - "interop.py"
Cohesion: 0.18
Nodes (15): AggregatedStateReport, BaseModel, Interoperability data models for cross-state agricultural data sharing. These…, Strip any personally identifiable information before data flows from a state-…, Per-state configuration that adapts KrishiSathi to local context. The same…, National-level aggregation of state signals — for the policymaker dashboard., SeverityLevel, SignalType (+7 more)

### Community 21 - "package.json"
Cohesion: 0.12
Nodes (16): name, private, version, clsx, react-dom, react-markdown, remark-gfm, tailwind-merge (+8 more)

### Community 22 - "gemini_service.py"
Cohesion: 0.13
Nodes (12): list_sources(), get, Public description of every data source the platform uses and whether it is…, All Gemini calls. Model output is treated as untrusted: * every call is async…, Text-to-speech with a native-language voice for every supported language.…, collections, google, google_genai (+4 more)

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 24 - "dependencies"
Cohesion: 0.15
Nodes (13): dependencies, clsx, leaflet, lucide-react, next, react, react-dom, react-leaflet (+5 more)

### Community 25 - "schema.py"
Cohesion: 0.15
Nodes (11): do_run_migrations(), run_async_migrations(), run_migrations_online(), Connection, logging_config, sqlalchemy, sqlalchemy_engine, sqlalchemy_ext_asyncio (+3 more)

### Community 26 - "farm_twin.py"
Cohesion: 0.15
Nodes (27): AdvisoryActionRecord, FarmRecord, A recommendation given to a farm and the farmer's self-reported follow-through…, Farm digital twin: a farmer's field. Access is by a bearer farm token whose…, farm_access(), normalize_crop(), Returns the canonical crop name, or None for unknown/other/empty input., action_view() (+19 more)

### Community 27 - "main.py"
Cohesion: 0.12
Nodes (17): RequestContextMiddleware, ensure_tables(), health_live(), health_ready(), lazy_db_init(), lifespan(), FastAPI, get (+9 more)

### Community 28 - "DiagnosisRecord"
Cohesion: 0.23
Nodes (10): DiagnosisRecord, asyncio, Prove that hard-coded crop-health values are not returned., test_crop_health_unavailable(), asyncio, test_macro_grid_collision(), asyncio, test_concurrent_outbreak_creation_count() (+2 more)

### Community 29 - "eslint.config.mjs"
Cohesion: 0.50
Nodes (3): eslintConfig, eslint, eslint-config-next

### Community 30 - "rate_limit.py"
Cohesion: 0.27
Nodes (11): ai_rate_limit(), _client_ip(), _local_incr(), Request, rate_limit(), tts_rate_limit(), create_limit(), Request (+3 more)

### Community 31 - "cn"
Cohesion: 0.11
Nodes (33): FEATURES, Home(), WorkflowDiagram(), AssistantMessage(), ChatMessage, Conversation(), SourceList(), DiagnosisResult() (+25 more)

### Community 32 - "ApiError"
Cohesion: 0.10
Nodes (27): ApiError, HTTPException carrying an explicit machine-readable code., get_current_user(), Principal, BaseModel, Validates an HS256 JWT signed with settings.JWT_SECRET. Fails closed: when no…, Interoperability partners (another country's or state's system) may read…, require_partner_role() (+19 more)

### Community 33 - "test_p03_outbreaks.py"
Cohesion: 0.22
Nodes (16): OutbreakRecord, clear_db(), asyncio, fixture, parametrize, test_daily_diagnoses_are_zero_filled_for_days_without_records(), test_diagnoses_without_location_are_recorded_but_not_clustered(), test_ineligible_diagnoses_never_form_outbreaks() (+8 more)

### Community 34 - "soil_service.py"
Cohesion: 0.13
Nodes (22): cache_get(), cache_set(), Optional shared JSON cache on Redis. Every call degrades to a no-op when Redis…, get_crop_health(), get_dashboard_outbreaks(), get_dashboard_report(), get_feedback_metrics(), get_stats() (+14 more)

### Community 35 - "advisory_context.py"
Cohesion: 0.27
Nodes (10): build_context(), _outbreaks(), Builds the DATA blocks that ground advisory answers. Sources are fetched…, _soil_text(), _weather(), _weather_text(), evaluate(), _insight() (+2 more)

### Community 36 - "api.ts"
Cohesion: 0.12
Nodes (35): PolicyDashboardPage(), FarmPage(), SECTIONS, AI_TIMEOUT_MS, API_BASE, ApiErrorCode, apiMisconfigured(), apiReachable() (+27 more)

### Community 37 - "devDependencies"
Cohesion: 0.18
Nodes (11): devDependencies, eslint, eslint-config-next, @playwright/test, tailwindcss, @tailwindcss/postcss, @types/leaflet, @types/node (+3 more)

### Community 38 - "speech.ts"
Cohesion: 0.07
Nodes (35): AdvisoryInput, getSpeechVoices(), transcribeAudio(), audioPlayer(), cleanup(), BCP47, BlockedError, cleanForSpeech() (+27 more)

### Community 39 - "config.py"
Cohesion: 0.20
Nodes (4): Settings, test_model_configuration_override(), BaseSettings, pydantic_settings

### Community 40 - "test_soil.py"
Cohesion: 0.21
Nodes (18): get(), fixture, SoilGrids integration: each failure mode is reported with its own reason, never…, reset(), resp(), test_concurrent_requests_share_one_upstream_call(), slow(), test_endpoint_exposes_reason() (+10 more)

### Community 41 - "manifest.json"
Cohesion: 0.22
Nodes (8): background_color, description, display, icons, name, short_name, start_url, theme_color

### Community 42 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, start, test, test:e2e, typecheck

### Community 43 - "test_earth_engine.py"
Cohesion: 0.15
Nodes (23): _point_result(), Sentinel-2 / Earth Engine: credential handling, honest status reporting and…, _service(), _sources_and_ready(), _state(), test_bad_key_is_unavailable_not_a_silent_not_set_up(), test_cloudy_month_is_no_suitable_observation_not_a_number(), test_crop_health_reason_distinguishes_missing_from_broken_configuration() (+15 more)

### Community 44 - "test_intelligence.py"
Cohesion: 0.14
Nodes (23): parse_soilgrids(), rate_organic_carbon(), rate_ph(), Soil Health Card organic-carbon classes: <0.5 % low, 0.5–0.75 % medium, >0.75 %…, conditions(), ids(), Weather parsing, agro rules, soil parsing and regenerative recommendations., Regression: soil_moisture_0_to_7cm is not a forecast-API variable and broke… (+15 more)

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
Nodes (3): BigQueryService, Any, Logs a diagnosis to BigQuery using batch load jobs to comply with Sandbox…

### Community 52 - "AUDIT.md"
Cohesion: 0.33
Nodes (5): 1. Architecture map (as found), 2. User flows traced, 3. Fallback / fabrication inventory, 4. Security risks, KrishiSathi — Repository Audit (2026-09-26)

### Community 53 - "OutbreakMap.tsx"
Cohesion: 0.29
Nodes (5): COLORS, OutbreakMap, Outbreak, leaflet, react-leaflet

### Community 54 - "README.md"
Cohesion: 0.33
Nodes (5): Architecture, Backend, Real data only, Running locally, What it does

### Community 55 - "EarthEngineService"
Cohesion: 0.13
Nodes (12): EarthEngineService, _first(), _iso_day(), date, Server-side dictionary for one window: median NDVI of clear pixels, scene…, NDVI of a window only when enough of the circle had clear pixels; None…, Metadata of the newest scene in the window that passed the scene-cloud…, Mean of the cloud-masked median Sentinel-2 NDVI over a geometry and date window. (+4 more)

### Community 56 - "transcribe.md"
Cohesion: 0.40
Nodes (4): graphify reference: transcribe video and audio, print progress to stdout, which would otherwise corrupt the JSON file (#1392)., Step 2.5 - Transcribe video / audio files (only if video files detected), Write the JSON from Python (NOT a shell '>' redirect): transcribe_all/Whisper

### Community 57 - "earth_engine_service.py"
Cohesion: 0.13
Nodes (15): asyncio, Structured domain events (one JSON log line each) for intelligence, diagnosis,…, ASGI middleware: request IDs, access logging, security headers, last-resort…, Operator check: is Sentinel-2 via Earth Engine really working with these…, Sentinel-2 crop health (NDVI) from Google Earth Engine. Dataset:…, Krishi Vigyan Kendra lookup from a small static reference list. The bundled…, binascii, ee (+7 more)

### Community 58 - "add-watch.md"
Cohesion: 0.50
Nodes (3): For --watch, For /graphify add, graphify reference: add a URL and watch a folder

### Community 59 - "hooks.md"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 60 - "interoperability.py"
Cohesion: 0.18
Nodes (22): PageV1, BaseModel, _adapter(), get_adapters(), get_crops(), get_diseases(), get_models(), get_observations() (+14 more)

### Community 61 - "frontend/README.md"
Cohesion: 0.50
Nodes (3): Getting Started, Learn More, or

### Community 79 - "datetime"
Cohesion: 0.26
Nodes (13): DataQuality, FarmIntelligence, Farm intelligence contract: the fused view of one farm that GET…, assemble(), _crop_health_summary(), data_quality(), farm_intelligence(), date (+5 more)

### Community 80 - "farm.py"
Cohesion: 0.12
Nodes (22): get_conditions(), get_crop_health(), get_crop_health_history(), get_crop_options(), get_farm_intelligence(), get_regenerative(), get_soil(), date (+14 more)

### Community 81 - "test_p02_regression.py"
Cohesion: 0.24
Nodes (13): jwt_secret(), asyncio, fixture, _stats(), test_client_cannot_choose_signal_id(), test_dashboard_report_generated_from_real_stats(), test_dashboard_report_insufficient_data_skips_ai(), test_federation_broadcast_signal_round_trip() (+5 more)

### Community 84 - "diagnosis.py"
Cohesion: 0.17
Nodes (14): AIDiagnosis, DiagnosisRequest, DiagnosisResponse, Differential, DiseaseReference, BaseModel, field_validator, One possible cause in a differential diagnosis. (+6 more)

### Community 85 - "federation.py"
Cohesion: 0.16
Nodes (16): AggregateResult, Aggregator, FedAvg, models_in_use(), ModelUpdate, ModelVersion, datetime, Protocol (+8 more)

### Community 87 - "farms.py"
Cohesion: 0.19
Nodes (14): log_event(), action_feedback(), create_farm(), FarmProfileIn, FeedbackIn, PracticeIn, BaseModel, Farm digital twin API. A farm is created without any personal data and accessed… (+6 more)

### Community 88 - "test_farm_twin.py"
Cohesion: 0.29
Nodes (16): FarmSnapshotRecord, What the intelligence engine concluded for a farm at one time: the twin's…, api(), clean(), create(), asyncio, fixture, Farm digital twin: creation, token access, snapshots, recommendation feedback… (+8 more)

### Community 89 - "test_interoperability.py"
Cohesion: 0.16
Nodes (12): auth(), clean_db(), asyncio, fixture, parametrize, BRICS interoperability: schema v1.0, country adapters, privacy-aware signal API…, secret(), test_observations_are_aggregated_to_grid_cells_with_small_groups_suppressed() (+4 more)

### Community 90 - "api.test.mjs"
Cohesion: 0.14
Nodes (8): ZERO, resetReachabilityProbe(), realNavigator, en, ref_node_assert, ref_node_child_process, ref_node_fs, ref_node_test

### Community 91 - "parse_service_account_key"
Cohesion: 0.17
Nodes (13): CredentialError, parse_service_account_key(), The configured key cannot be used. `code` is safe to show to operators., Accept the service-account JSON as-is or base64-encoded (easier to paste into…, parametrize, _ready_service(), test_escaped_newlines_in_private_key_are_repaired(), test_initialization_failures_are_classified() (+5 more)

### Community 92 - "classify_error"
Cohesion: 0.20
Nodes (5): classify_error(), Map an Earth Engine / google-auth exception to a failure code. Order matters:…, Retry a failed start-up after a cool-down, so a transient outage does not…, test_unknown_query_failure_is_a_dataset_query_failure(), BaseException

### Community 93 - "ServiceUnavailableException"
Cohesion: 0.17
Nodes (10): ServiceUnavailableException, Regions configured in this deployment, and forecast risks at their reference…, _at(), Weather conditions from the Open-Meteo forecast API. Open-Meteo "current"…, Compact current-conditions dict used as AI context and by the legacy…, weather_condition(), WeatherService, test_intelligence_endpoint_when_weather_is_down() (+2 more)

### Community 94 - "_point_with"
Cohesion: 0.38
Nodes (10): _pass(), _point_with(), test_baseline_compares_with_the_same_weeks_of_previous_years(), test_baseline_needs_two_usable_years(), test_history_series_keeps_gaps_as_null(), test_no_radar_scene_and_radar_dataset_unavailable(), test_radar_compares_only_the_same_orbit_direction(), test_radar_is_reported_even_when_clouds_hide_the_field() (+2 more)

### Community 95 - "measurement.py"
Cohesion: 0.39
Nodes (7): _cell(), feedback_metrics(), _grouped(), App-derived feedback signals: how often recommendations are followed and what…, rows: (followed, outcome). Rates are over answered questions only., _summary(), math

### Community 96 - "conftest.py"
Cohesion: 0.33
Nodes (5): alembic_config, migrated_test_db(), fixture, Test database isolation. Tests delete rows, so they never touch the database in…, tempfile

### Community 97 - "get_farm_intelligence"
Cohesion: 0.33
Nodes (6): FarmTwinIntelligence, get_farm(), get_farm_intelligence(), get, The farm's record and history: intelligence snapshots, recommendations with…, Farm intelligence for the stored profile, using the farm's own recent…

### Community 98 - "._cached"
Cohesion: 0.33
Nodes (3): Crop health at a point: NDVI now and 30 days earlier, the same-season baseline…, NDVI for the last HISTORY_WINDOWS consecutive 30-day windows (null where no…, Successful and no-imagery answers are cached for POINT_CACHE_TTL_S (a new pass…

## Knowledge Gaps
- **228 isolated node(s):** `builds`, `routes`, `leaf`, `notImage`, `API` (+223 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 614 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Are the 15 inferred relationships involving `ServiceUnavailableException` (e.g. with `install_error_handlers()` and `_weather()`) actually correct?**
  _`ServiceUnavailableException` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `builds`, `routes`, `leaf` to the rest of the system?**
  _228 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `i18n.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.08658536585365853 - nodes in this community are weakly interconnected._
- **Should `test_security.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0743321718931475 - nodes in this community are weakly interconnected._
- **Should `test_failure_states.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08620689655172414 - nodes in this community are weakly interconnected._
- **Should `typing` be split into smaller, more focused modules?**
  _Cohesion score 0.09846153846153846 - nodes in this community are weakly interconnected._
- **Should `routers/advisory.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07086247086247087 - nodes in this community are weakly interconnected._
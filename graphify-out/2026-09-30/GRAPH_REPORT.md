# Graph Report - krishisathi  (2026-09-30)

## Corpus Check
- 197 files · ~166,283 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 6, .example 2, .ini 1)

## Summary
- 1849 nodes · 4640 edges · 97 communities (76 shown, 21 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 183 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4dae2dff`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- i18n.tsx
- test_security.py
- test_intelligence.py
- alembic
- test_diagnosis.py
- cn
- test_speech_language.py
- test_failure_states.py
- diagnose.py
- TodayAlertsWeather.tsx
- offline.ts
- errors.py
- useI18n
- farms.py
- test_farm_intelligence.py
- database.py
- mock-api.ts
- .get_dashboard_stats
- india.py
- advisor/page.tsx
- interop.py
- package.json
- gemini_service.py
- compilerOptions
- dependencies
- soil_service.py
- farm_twin.py
- main.py
- persistence_service.py
- eslint.config.mjs
- rate_limit.py
- types.ts
- ApiError
- test_p03_outbreaks.py
- dashboard.py
- advisory_context.py
- api.ts
- devDependencies
- speech.ts
- ._cached
- test_soil.py
- manifest.json
- scripts
- _service
- routers/advisory.py
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
- test_kvk.py
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
- tts_service.py
- normalize_crop
- test_p02_regression.py
- federation.py
- typing
- test_interoperability.py
- parse_service_account_key
- classify_error
- ServiceUnavailableException
- test_earth_engine.py
- pytest
- test_live_sentinel2_ndvi_for_a_ludhiana_wheat_field
- GeminiService
- datetime
- helpers.py
- next.config.ts

## God Nodes (most connected - your core abstractions)
1. `useI18n()` - 93 edges
2. `cn()` - 64 edges
3. `ServiceUnavailableException` - 49 edges
4. `request()` - 34 edges
5. `post()` - 33 edges
6. `ApiError` - 31 edges
7. `EarthEngineService` - 31 edges
8. `FarmContext` - 28 edges
9. `ai_diagnosis()` - 24 edges
10. `ctx()` - 24 edges

## Surprising Connections (you probably didn't know these)
- `API (`backend/routers/interoperability.py`)` --references--> `RiskSignalV1`  [INFERRED]
  docs/INTEROPERABILITY.md → backend/models/interop_v1.py
- `Voice, offline use and the "something is wrong" entry point` --references--> `farm_intelligence()`  [INFERRED]
  docs/INTELLIGENCE.md → backend/services/intelligence_service.py
- `Source status` --references--> `unavailable()`  [INFERRED]
  docs/EARTH_ENGINE.md → frontend/e2e/mock-api.ts
- `Inputs and their status` --references--> `unavailable()`  [INFERRED]
  docs/INTELLIGENCE.md → frontend/e2e/mock-api.ts
- `Policymaker early warning` --references--> `unavailable()`  [INFERRED]
  docs/INTELLIGENCE.md → frontend/e2e/mock-api.ts

## Import Cycles
- None detected.

## Communities (97 total, 21 thin omitted)

### Community 0 - "i18n.tsx"
Cohesion: 0.10
Nodes (24): AdvisoryInput, cache, I18nContext, I18nValue, interpolate(), isLanguage(), LanguageProvider(), loaders (+16 more)

### Community 1 - "test_security.py"
Cohesion: 0.07
Nodes (27): ai_down(), create_token(), err(), image_payload(), MockRedis, fixture, Regression: without Redis the limiter used to be silently disabled., Regression: allow_origins used to include '*' together with credentials. (+19 more)

### Community 2 - "test_intelligence.py"
Cohesion: 0.07
Nodes (49): evaluate(), _insight(), _num(), Deterministic agro-meteorological rules. Each insight is derived only from…, parse_soilgrids(), rate_organic_carbon(), rate_ph(), Soil Health Card organic-carbon classes: <0.5 % low, 0.5–0.75 % medium, >0.75 %… (+41 more)

### Community 4 - "test_diagnosis.py"
Cohesion: 0.19
Nodes (25): ai_diagnosis(), post(), fixture, parametrize, reset_limits(), test_chemical_threshold_is_configurable_but_never_below_moderate(), test_confident_detection_includes_verified_reference(), test_differential_is_returned_and_malformed_entries_dropped() (+17 more)

### Community 5 - "cn"
Cohesion: 0.07
Nodes (42): frontend_src_app_globals, beng, body, deva, display, gujr, guru, knda (+34 more)

### Community 6 - "test_speech_language.py"
Cohesion: 0.08
Nodes (12): is_in_language(), Supported UI/response languages (allow-list). Codes match the frontend., Share of letters written in the language's script (Latin for English); 1.0 for…, True when the text is mostly in the native script. Technical terms (pH, NPK)…, script_ratio(), isolate(), fixture, Read-aloud voices and answer language: native voice per language, no English… (+4 more)

### Community 7 - "test_failure_states.py"
Cohesion: 0.13
Nodes (15): jpeg_bytes(), test_tiny_image_rejected(), clear_caches(), asyncio, fixture, parametrize, Every upstream failure must surface as an explicit, retryable error, never as…, test_ai_not_configured_is_explicit() (+7 more)

### Community 8 - "diagnose.py"
Cohesion: 0.08
Nodes (44): get_idempotency_result(), set_idempotency_result(), AIDiagnosis, DiagnosisRequest, DiagnosisResponse, Differential, DiseaseReference, BaseModel (+36 more)

### Community 9 - "TodayAlertsWeather.tsx"
Cohesion: 0.10
Nodes (41): ActionFeedback(), FarmHistoryCard(), FOLLOWED, OUTCOMES, AlertView, Fmt, T, whenLabel() (+33 more)

### Community 10 - "offline.ts"
Cohesion: 0.14
Nodes (25): AboutPage(), LastAnswer(), PracticeAdoption(), SatelliteHistory(), deliver(), OfflineStatus(), getSources(), recordPractice() (+17 more)

### Community 11 - "errors.py"
Cohesion: 0.15
Nodes (16): error_body(), _from_detail(), install_error_handlers(), _api_error(), _http_error(), _service_unavailable(), _validation_error(), FastAPI (+8 more)

### Community 12 - "useI18n"
Cohesion: 0.09
Nodes (48): ErrorPage(), NotFound(), AssistantMessage(), Conversation(), SourceList(), insightView(), WeatherMeaning(), DiseaseItem() (+40 more)

### Community 13 - "farms.py"
Cohesion: 0.18
Nodes (13): log_event(), Structured domain events (one JSON log line each) for intelligence, diagnosis,…, action_feedback(), create_farm(), FarmProfileIn, FeedbackIn, PracticeIn, BaseModel (+5 more)

### Community 14 - "test_farm_intelligence.py"
Cohesion: 0.06
Nodes (83): DataQuality, Evidence, FarmInput, BaseModel, Farm intelligence contract: the fused view of one farm that GET…, Risk, RuleRef, TopAction (+75 more)

### Community 15 - "database.py"
Cohesion: 0.18
Nodes (10): do_run_migrations(), run_async_migrations(), run_migrations_online(), Connection, logging_config, sqlalchemy_engine, sqlalchemy_ext_asyncio, sqlalchemy_orm (+2 more)

### Community 16 - "mock-api.ts"
Cohesion: 0.05
Nodes (45): EscalationSink, NotConnectedSink, Protocol, No extension system is integrated yet: the case is returned to the farmer to…, Where a case goes. A KVK or state extension system implements `submit` and…, Error codes, History series, Limits (+37 more)

### Community 17 - ".get_dashboard_stats"
Cohesion: 0.17
Nodes (6): normalize_level(), _public_coord(), Outbreak clusters with coordinates rounded to ~11 km. Stale clusters are…, Located, confident disease detections of the last `days` days (for early-…, Maps legacy 'Medium'/'High' values and new levels onto low | moderate | high., Aggregated counts from stored records only. No external or estimated figures.

### Community 18 - "india.py"
Cohesion: 0.07
Nodes (54): AdvisoryV1, CropV1, DiseaseV1, FarmerRefV1, FarmV1, GeoRefV1, GridCellV1, json_schemas() (+46 more)

### Community 19 - "advisor/page.tsx"
Cohesion: 0.10
Nodes (39): AdvisorPage(), SavedAnswer, TOPICS, DiagnosePage(), Phase, ChatMessage, FarmProfileForm(), useLocationLabel() (+31 more)

### Community 20 - "interop.py"
Cohesion: 0.16
Nodes (17): AggregatedStateReport, BaseModel, Interoperability data models for cross-state agricultural data sharing. These…, Strip any personally identifiable information before data flows from a state-…, Standard payload for cross-state agricultural data exchange. Any state system…, Per-state configuration that adapts KrishiSathi to local context. The same…, National-level aggregation of state signals — for the policymaker dashboard., RegionalAgriSignal (+9 more)

### Community 21 - "package.json"
Cohesion: 0.13
Nodes (14): name, private, version, clsx, react-dom, tailwind-merge, tailwindcss, @tailwindcss/postcss (+6 more)

### Community 22 - "gemini_service.py"
Cohesion: 0.07
Nodes (24): AsyncClient, Settings, ASGI middleware: request IDs, access logging, security headers, last-resort…, list_sources(), get, Public description of every data source the platform uses and whether it is…, Operator check: is Sentinel-2 via Earth Engine really working with these…, download_image() (+16 more)

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 24 - "dependencies"
Cohesion: 0.15
Nodes (13): dependencies, clsx, leaflet, lucide-react, next, react, react-dom, react-leaflet (+5 more)

### Community 25 - "soil_service.py"
Cohesion: 0.31
Nodes (7): _failure(), _fetch(), Soil properties from ISRIC SoilGrids 2.0 (modelled, 250 m resolution).…, One SoilGrids query, with one retry for transient failures. Never raises., Returns an availability-tagged dict with a specific `reason` on failure; never…, _remember(), SoilService

### Community 26 - "farm_twin.py"
Cohesion: 0.09
Nodes (50): FarmIntelligence, AdvisoryActionRecord, FarmRecord, FarmSnapshotRecord, What the intelligence engine concluded for a farm at one time: the twin's…, A recommendation given to a farm and the farmer's self-reported follow-through…, Farm digital twin: a farmer's field. Access is by a bearer farm token whose…, farm_access() (+42 more)

### Community 27 - "main.py"
Cohesion: 0.12
Nodes (17): RequestContextMiddleware, ensure_tables(), health_live(), health_ready(), lazy_db_init(), lifespan(), FastAPI, get (+9 more)

### Community 28 - "persistence_service.py"
Cohesion: 0.16
Nodes (20): AdvisoryRecord, DiagnosisRecord, FederationSignalRecord, OutbreakRecord, _haversine(), outbreak_eligible(), PersistenceService, datetime (+12 more)

### Community 29 - "eslint.config.mjs"
Cohesion: 0.50
Nodes (3): eslintConfig, eslint, eslint-config-next

### Community 30 - "rate_limit.py"
Cohesion: 0.27
Nodes (11): ai_rate_limit(), _client_ip(), _local_incr(), Request, rate_limit(), tts_rate_limit(), create_limit(), Request (+3 more)

### Community 31 - "types.ts"
Cohesion: 0.05
Nodes (50): Choices(), ADOPTION, CropOptionsCard(), HORIZONS, PracticeItem(), PracticePlan(), TriggerText, CropHealthCard() (+42 more)

### Community 32 - "ApiError"
Cohesion: 0.10
Nodes (27): ApiError, HTTPException carrying an explicit machine-readable code., get_current_user(), Principal, BaseModel, Validates an HS256 JWT signed with settings.JWT_SECRET. Fails closed: when no…, Interoperability partners (another country's or state's system) may read…, require_partner_role() (+19 more)

### Community 33 - "test_p03_outbreaks.py"
Cohesion: 0.26
Nodes (13): asyncio, parametrize, test_daily_diagnoses_are_zero_filled_for_days_without_records(), test_diagnoses_without_location_are_recorded_but_not_clustered(), test_ineligible_diagnoses_never_form_outbreaks(), test_insufficient_observations_no_outbreak(), test_outbreak_coordinates_are_coarsened_for_privacy(), test_outside_radius_separate_cluster() (+5 more)

### Community 34 - "dashboard.py"
Cohesion: 0.07
Nodes (44): cache_get(), cache_set(), Optional shared JSON cache on Redis. Every call degrades to a no-op when Redis…, get_crop_health(), get_dashboard_outbreaks(), get_dashboard_report(), get_early_warning(), get_feedback_metrics() (+36 more)

### Community 35 - "advisory_context.py"
Cohesion: 0.21
Nodes (13): get_farm_intelligence(), date, What matters for this farm right now: weather, soil, satellite, crop stage and…, build_context(), _intelligence_text(), _outbreaks(), Builds the DATA blocks that ground advisory answers. Sources are fetched…, _soil_text() (+5 more)

### Community 36 - "api.ts"
Cohesion: 0.08
Nodes (46): PolicyDashboardPage(), FarmPage(), SECTIONS, RiskRadar(), AI_TIMEOUT_MS, API_BASE, ApiErrorCode, apiMisconfigured() (+38 more)

### Community 37 - "devDependencies"
Cohesion: 0.18
Nodes (11): devDependencies, eslint, eslint-config-next, @playwright/test, tailwindcss, @tailwindcss/postcss, @types/leaflet, @types/node (+3 more)

### Community 38 - "speech.ts"
Cohesion: 0.05
Nodes (41): ZERO, getSpeechVoices(), synthesizeSpeech(), transcribeAudio(), audioPlayer(), cleanup(), BCP47, BlockedError (+33 more)

### Community 39 - "._cached"
Cohesion: 0.33
Nodes (3): Crop health at a point: NDVI now and 30 days earlier, the same-season baseline…, NDVI for the last HISTORY_WINDOWS consecutive 30-day windows (null where no…, Successful and no-imagery answers are cached for POINT_CACHE_TTL_S (a new pass…

### Community 40 - "test_soil.py"
Cohesion: 0.21
Nodes (18): get(), fixture, SoilGrids integration: each failure mode is reported with its own reason, never…, reset(), resp(), test_concurrent_requests_share_one_upstream_call(), slow(), test_endpoint_exposes_reason() (+10 more)

### Community 41 - "manifest.json"
Cohesion: 0.22
Nodes (8): background_color, description, display, icons, name, short_name, start_url, theme_color

### Community 42 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, start, test, test:e2e, typecheck

### Community 43 - "_service"
Cohesion: 0.21
Nodes (13): _service(), _state(), test_bad_key_is_unavailable_not_a_silent_not_set_up(), test_crop_health_reason_distinguishes_missing_from_broken_configuration(), test_dataset_not_readable_is_authenticated_but_unavailable(), test_ee_project_overrides_the_keys_project(), test_missing_key_is_not_configured(), test_project_without_key_uses_application_default_credentials() (+5 more)

### Community 44 - "routers/advisory.py"
Cohesion: 0.14
Nodes (28): AdvisoryRequest, AdvisoryResponse, DataSourceUse, _decode_limited(), FollowUpRequest, BaseModel, field_validator, TranscribeRequest (+20 more)

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

### Community 57 - "test_kvk.py"
Cohesion: 0.11
Nodes (17): crop_options(), _nearest_state(), Crop trade-offs from verified sources only. Shown per crop: typical seasonal…, haversine_km(), KvkService, Krishi Vigyan Kendra lookup from a small static reference list. The bundled…, Great-circle distance in kilometres (spherical Earth, R = 6371 km)., KVK for the district nearest to (lat, lng), or None when no listed district is… (+9 more)

### Community 58 - "add-watch.md"
Cohesion: 0.50
Nodes (3): For --watch, For /graphify add, graphify reference: add a URL and watch a folder

### Community 59 - "hooks.md"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 60 - "interoperability.py"
Cohesion: 0.17
Nodes (23): PageV1, BaseModel, _adapter(), get_adapters(), get_crops(), get_diseases(), get_models(), get_observations() (+15 more)

### Community 61 - "frontend/README.md"
Cohesion: 0.50
Nodes (3): Getting Started, Learn More, or

### Community 79 - "tts_service.py"
Cohesion: 0.11
Nodes (18): get, Which server voice each language gets, so clients can prefer a better on-device…, tts_voices(), gemini_languages(), _gtts(), pcm_to_wav(), Text-to-speech with a native-language voice for every supported language.…, Drops Markdown symbols that voices would otherwise read out ("asterisk",… (+10 more)

### Community 80 - "normalize_crop"
Cohesion: 0.14
Nodes (14): get_regenerative(), crop_group(), normalize_crop(), Canonical crop list. Used to allow-list crop inputs before they reach prompts…, Returns the canonical crop name, or None for unknown/other/empty input., DiseaseReferenceService, Returns a reference entry only if the id exists (and, when a crop is known,…, plan() (+6 more)

### Community 81 - "test_p02_regression.py"
Cohesion: 0.27
Nodes (12): jwt_secret(), asyncio, fixture, _stats(), test_client_cannot_choose_signal_id(), test_dashboard_report_generated_from_real_stats(), test_dashboard_report_insufficient_data_skips_ai(), test_federation_broadcast_signal_round_trip() (+4 more)

### Community 85 - "federation.py"
Cohesion: 0.16
Nodes (16): AggregateResult, Aggregator, FedAvg, models_in_use(), ModelUpdate, ModelVersion, datetime, Protocol (+8 more)

### Community 87 - "typing"
Cohesion: 0.38
Nodes (8): DiseaseAlert, OutbreakReport, BaseModel, get_alerts(), get_outbreaks(), get_personalized_alerts(), get, typing

### Community 89 - "test_interoperability.py"
Cohesion: 0.15
Nodes (12): auth(), asyncio, fixture, parametrize, BRICS interoperability: schema v1.0, country adapters, privacy-aware signal API…, secret(), test_observations_are_aggregated_to_grid_cells_with_small_groups_suppressed(), test_risk_signals_from_clusters_and_regional_federation() (+4 more)

### Community 91 - "parse_service_account_key"
Cohesion: 0.17
Nodes (13): CredentialError, parse_service_account_key(), The configured key cannot be used. `code` is safe to show to operators., Accept the service-account JSON as-is or base64-encoded (easier to paste into…, parametrize, _ready_service(), test_escaped_newlines_in_private_key_are_repaired(), test_initialization_failures_are_classified() (+5 more)

### Community 92 - "classify_error"
Cohesion: 0.20
Nodes (5): classify_error(), Map an Earth Engine / google-auth exception to a failure code. Order matters:…, Retry a failed start-up after a cool-down, so a transient outage does not…, test_unknown_query_failure_is_a_dataset_query_failure(), BaseException

### Community 93 - "ServiceUnavailableException"
Cohesion: 0.21
Nodes (8): ServiceUnavailableException, Compact current-conditions dict used as AI context and by the legacy…, WeatherService, test_intelligence_endpoint_when_weather_is_down(), test_regenerative_endpoint_reports_inputs(), test_all_providers_failing_is_503_not_wrong_voice(), test_gemini_failure_falls_back_to_native_gtts_voice(), Exception

### Community 94 - "test_earth_engine.py"
Cohesion: 0.17
Nodes (22): _pass(), _point_result(), _point_with(), Sentinel-2 / Earth Engine: credential handling, honest status reporting and…, _sources_and_ready(), test_baseline_compares_with_the_same_weeks_of_previous_years(), test_baseline_needs_two_usable_years(), test_cloudy_month_is_no_suitable_observation_not_a_number() (+14 more)

### Community 96 - "pytest"
Cohesion: 0.17
Nodes (10): alembic_config, migrated_test_db(), fixture, Test database isolation. Tests delete rows, so they never touch the database in…, asyncio, Prove that hard-coded crop-health values are not returned., test_crop_health_unavailable(), httpx (+2 more)

### Community 100 - "GeminiService"
Cohesion: 0.25
Nodes (7): GeminiService, Models sometimes answer in the question's language instead of the requested…, Natural speech for `text`. Returns (16-bit mono PCM, sample rate)., untrusted(), language_name(), language_rule(), Prompt sentence pinning the reply language. "Native script" is only said for…

### Community 103 - "datetime"
Cohesion: 0.12
Nodes (21): asyncio, get_conditions(), get_crop_health(), get_crop_health_history(), get_crop_options(), get_soil(), get, Farmer-facing intelligence for one location. Each endpoint degrades… (+13 more)

### Community 105 - "helpers.py"
Cohesion: 0.15
Nodes (7): Server-side image validation (never trust the client's Content-Type)., Shared test fixtures/data (imported by test modules; pytest puts this directory…, Server errors must reach the browser as errors, not as CORS failures that look…, fastapi_testclient, io, pil, unittest_mock

### Community 107 - "next.config.ts"
Cohesion: 0.50
Nodes (3): apiOrigin, nextConfig, securityHeaders

## Knowledge Gaps
- **238 isolated node(s):** `builds`, `routes`, `leaf`, `notImage`, `API` (+233 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 636 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Farm Intelligence Engine` connect `mock-api.ts` to `advisory_context.py`?**
  _High betweenness centrality (0.374) - this node is a cross-community bridge._
- **Why does `@playwright/test` connect `mock-api.ts` to `package.json`?**
  _High betweenness centrality (0.358) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `ServiceUnavailableException` (e.g. with `install_error_handlers()` and `_weather()`) actually correct?**
  _`ServiceUnavailableException` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `builds`, `routes`, `leaf` to the rest of the system?**
  _238 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `i18n.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.09915966386554621 - nodes in this community are weakly interconnected._
- **Should `test_security.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0743321718931475 - nodes in this community are weakly interconnected._
- **Should `test_intelligence.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07127882599580712 - nodes in this community are weakly interconnected._
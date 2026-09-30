# Graph Report - krishisathi  (2026-09-30)

## Corpus Check
- 190 files · ~153,624 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 6, .example 2, .ini 1)

## Summary
- 1775 nodes · 4409 edges · 110 communities (86 shown, 24 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 180 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `cedfd6ef`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- i18n.tsx
- test_security.py
- test_failure_states.py
- typing
- test_diagnosis.py
- layout.tsx
- test_speech_language.py
- intelligence-text.ts
- diagnose.py
- types.ts
- test_kvk.py
- errors.py
- useI18n
- risk_engine.py
- test_farm_intelligence.py
- asyncio
- mock-api.ts
- .save_diagnosis
- india.py
- diagnose/page.tsx
- states.py
- package.json
- gemini_service.py
- compilerOptions
- dependencies
- database.py
- farm_twin.py
- main.py
- persistence_service.py
- eslint.config.mjs
- rate_limit.py
- cn
- ApiError
- test_p03_outbreaks.py
- test_intelligence.py
- advisory_context.py
- api.ts
- devDependencies
- speech-core.ts
- test_soil.py
- manifest.json
- scripts
- test_earth_engine.py
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
- logging
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
- datetime
- test_p02_regression.py
- diagnosis.py
- federation.py
- DiseaseReferenceService
- farms.py
- test_farm_twin.py
- test_interoperability.py
- app/page.tsx
- parse_service_account_key
- classify_error
- ServiceUnavailableException
- _point_with
- measurement.py
- pytest
- Conversation.tsx
- farm_context.py
- test_live_sentinel2_ndvi_for_a_ludhiana_wheat_field
- GeminiService
- image_payload
- text_to_speech
- earth_engine_service.py
- EscalationSink
- unittest_mock
- _decode_limited
- next.config.ts
- Settings
- reset_limits

## God Nodes (most connected - your core abstractions)
1. `useI18n()` - 83 edges
2. `cn()` - 60 edges
3. `ServiceUnavailableException` - 49 edges
4. `post()` - 33 edges
5. `request()` - 33 edges
6. `ApiError` - 32 edges
7. `EarthEngineService` - 31 edges
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
- `Regenerative plan and crop options` --references--> `unavailable()`  [INFERRED]
  docs/INTELLIGENCE.md → frontend/e2e/mock-api.ts
- `Risks` --references--> `unavailable()`  [INFERRED]
  docs/INTELLIGENCE.md → frontend/e2e/mock-api.ts

## Import Cycles
- None detected.

## Communities (110 total, 24 thin omitted)

### Community 0 - "i18n.tsx"
Cohesion: 0.09
Nodes (28): AlertView, Fmt, T, cache, I18nContext, I18nValue, interpolate(), isLanguage() (+20 more)

### Community 1 - "test_security.py"
Cohesion: 0.09
Nodes (20): ai_down(), create_token(), err(), fixture, Regression: allow_origins used to include '*' together with credentials., Regression: without JWT_SECRET any token (incl. the old hardcoded demo token)…, setup_env(), test_auth_fails_closed_without_secret() (+12 more)

### Community 2 - "test_failure_states.py"
Cohesion: 0.12
Nodes (16): jpeg_bytes(), Shared test fixtures/data (imported by test modules; pytest puts this directory…, test_tiny_image_rejected(), clear_caches(), asyncio, fixture, parametrize, Every upstream failure must surface as an explicit, retryable error, never as… (+8 more)

### Community 3 - "typing"
Cohesion: 0.08
Nodes (9): alembic, DiseaseAlert, OutbreakReport, BaseModel, get_alerts(), get_outbreaks(), get_personalized_alerts(), get (+1 more)

### Community 4 - "test_diagnosis.py"
Cohesion: 0.22
Nodes (23): ai_diagnosis(), post(), parametrize, test_chemical_threshold_is_configurable_but_never_below_moderate(), test_confident_detection_includes_verified_reference(), test_differential_is_returned_and_malformed_entries_dropped(), test_farm_context_reaches_the_prompt_as_supporting_information(), test_healthy_has_no_disease_name() (+15 more)

### Community 5 - "layout.tsx"
Cohesion: 0.12
Nodes (15): frontend_src_app_globals, beng, body, deva, display, gujr, guru, knda (+7 more)

### Community 6 - "test_speech_language.py"
Cohesion: 0.10
Nodes (11): is_in_language(), Supported UI/response languages (allow-list). Codes match the frontend., Share of letters written in the language's script (Latin for English); 1.0 for…, True when the text is mostly in the native script. Technical terms (pH, NPK)…, script_ratio(), isolate(), fixture, Read-aloud voices and answer language: native voice per language, no English… (+3 more)

### Community 7 - "intelligence-text.ts"
Cohesion: 0.12
Nodes (24): FarmHistoryCard(), EvidenceList(), RiskRow(), ACTION_WHAT, actionTitle(), actionWhat(), BASIS_KIND, basisKind() (+16 more)

### Community 8 - "diagnose.py"
Cohesion: 0.17
Nodes (20): get_idempotency_result(), set_idempotency_result(), DiagnosisResponse, diagnose_base64(), diagnose_multipart(), _farm(), _farm_block(), _nearby() (+12 more)

### Community 9 - "types.ts"
Cohesion: 0.05
Nodes (47): ADOPTION, CropOptionsCard(), HORIZONS, PracticeItem(), PracticePlan(), TriggerText, CropHealthCard(), KvkCard() (+39 more)

### Community 10 - "test_kvk.py"
Cohesion: 0.16
Nodes (10): haversine_km(), KvkService, Great-circle distance in kilometres (spherical Earth, R = 6371 km)., KVK for the district nearest to (lat, lng), or None when no listed district is…, KVK lookup: never report a distance to a district reference point as a distance…, test_empty_list_returns_none(), test_haversine_known_distance(), test_haversine_zero_and_symmetry() (+2 more)

### Community 11 - "errors.py"
Cohesion: 0.15
Nodes (16): error_body(), _from_detail(), install_error_handlers(), _api_error(), _http_error(), _service_unavailable(), _validation_error(), FastAPI (+8 more)

### Community 12 - "useI18n"
Cohesion: 0.12
Nodes (29): PolicyDashboardPage(), ErrorPage(), insightView(), whenLabel(), WeatherMeaning(), Bars(), CropHealthPanel(), KpiRow() (+21 more)

### Community 13 - "risk_engine.py"
Cohesion: 0.24
Nodes (29): Evidence, BaseModel, Risk, RuleRef, TopAction, FarmContext, assess(), crop_health() (+21 more)

### Community 14 - "test_farm_intelligence.py"
Cohesion: 0.11
Nodes (35): estimate_stage(), date, Stage estimate with `status`: estimated | not_provided | no_calendar |…, Topsoil water status: modelled soil moisture read against modelled soil…, (wilting point, field capacity) in m³/m³ from Saxton & Rawls (2006), equations…, {"status": dry | adequate | wet | unavailable, "available_water_fraction",…, topsoil_water(), water_limits() (+27 more)

### Community 15 - "asyncio"
Cohesion: 0.23
Nodes (9): AsyncClient, asyncio, Operator check: is Sentinel-2 via Earth Engine really working with these…, download_image(), fetch_image_list(), run_validation_suite(), random, sklearn_metrics (+1 more)

### Community 16 - "mock-api.ts"
Cohesion: 0.06
Nodes (38): Error codes, History series, Limits, One-time setup, Same-season baseline (temporal context), Sentinel-1 radar (cloud-resilient), Sentinel-2 crop health via Google Earth Engine, Source status (+30 more)

### Community 17 - ".save_diagnosis"
Cohesion: 0.14
Nodes (9): _haversine(), normalize_level(), outbreak_eligible(), _public_coord(), Outbreak clusters with coordinates rounded to ~11 km. Stale clusters are…, Aggregated counts from stored records only. No external or estimated figures., Maps legacy 'Medium'/'High' values and new levels onto low | moderate | high., Only confident, located disease detections may contribute to outbreak clusters. (+1 more)

### Community 18 - "india.py"
Cohesion: 0.07
Nodes (53): AdvisoryV1, CropV1, DiseaseV1, FarmerRefV1, FarmV1, GeoRefV1, GridCellV1, json_schemas() (+45 more)

### Community 19 - "diagnose/page.tsx"
Cohesion: 0.11
Nodes (36): AdvisorPage(), DiagnosePage(), Phase, FarmProfileForm(), useLocationLabel(), inputClass, ApiError, createFarm() (+28 more)

### Community 20 - "states.py"
Cohesion: 0.13
Nodes (23): AggregatedStateReport, BaseModel, Interoperability data models for cross-state agricultural data sharing. These…, Strip any personally identifiable information before data flows from a state-…, Per-state configuration that adapts KrishiSathi to local context. The same…, National-level aggregation of state signals — for the policymaker dashboard., SeverityLevel, SignalType (+15 more)

### Community 21 - "package.json"
Cohesion: 0.13
Nodes (14): name, private, version, clsx, react-dom, tailwind-merge, tailwindcss, @tailwindcss/postcss (+6 more)

### Community 22 - "gemini_service.py"
Cohesion: 0.17
Nodes (9): list_sources(), get, Public description of every data source the platform uses and whether it is…, All Gemini calls. Model output is treated as untrusted: * every call is async…, untrusted(), google, google_genai, pydantic_settings (+1 more)

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 24 - "dependencies"
Cohesion: 0.15
Nodes (13): dependencies, clsx, leaflet, lucide-react, next, react, react-dom, react-leaflet (+5 more)

### Community 25 - "database.py"
Cohesion: 0.18
Nodes (10): do_run_migrations(), run_async_migrations(), run_migrations_online(), Connection, logging_config, sqlalchemy_engine, sqlalchemy_ext_asyncio, sqlalchemy_orm (+2 more)

### Community 26 - "farm_twin.py"
Cohesion: 0.15
Nodes (28): AdvisoryActionRecord, FarmRecord, FarmSnapshotRecord, What the intelligence engine concluded for a farm at one time: the twin's…, A recommendation given to a farm and the farmer's self-reported follow-through…, Farm digital twin: a farmer's field. Access is by a bearer farm token whose…, action_view(), authorize() (+20 more)

### Community 27 - "main.py"
Cohesion: 0.12
Nodes (17): RequestContextMiddleware, ensure_tables(), health_live(), health_ready(), lazy_db_init(), lifespan(), FastAPI, get (+9 more)

### Community 28 - "persistence_service.py"
Cohesion: 0.16
Nodes (19): Standard payload for cross-state agricultural data exchange. Any state system…, RegionalAgriSignal, AdvisoryRecord, DiagnosisRecord, FederationSignalRecord, OutbreakRecord, PersistenceService, datetime (+11 more)

### Community 29 - "eslint.config.mjs"
Cohesion: 0.50
Nodes (3): eslintConfig, eslint, eslint-config-next

### Community 30 - "rate_limit.py"
Cohesion: 0.27
Nodes (11): ai_rate_limit(), _client_ip(), _local_incr(), Request, rate_limit(), tts_rate_limit(), create_limit(), Request (+3 more)

### Community 31 - "cn"
Cohesion: 0.09
Nodes (49): AboutPage(), NotFound(), DiagnosisResult(), EscalationCard(), StepList(), ActionFeedback(), Choices(), FOLLOWED (+41 more)

### Community 32 - "ApiError"
Cohesion: 0.13
Nodes (16): ApiError, HTTPException carrying an explicit machine-readable code., get_current_user(), Validates an HS256 JWT signed with settings.JWT_SECRET. Fails closed: when no…, require_system_role(), get_ee_status(), get, Authenticated check of the Earth Engine pipeline status. (+8 more)

### Community 33 - "test_p03_outbreaks.py"
Cohesion: 0.26
Nodes (13): asyncio, parametrize, test_daily_diagnoses_are_zero_filled_for_days_without_records(), test_diagnoses_without_location_are_recorded_but_not_clustered(), test_ineligible_diagnoses_never_form_outbreaks(), test_insufficient_observations_no_outbreak(), test_outbreak_coordinates_are_coarsened_for_privacy(), test_outside_radius_separate_cluster() (+5 more)

### Community 34 - "test_intelligence.py"
Cohesion: 0.05
Nodes (63): cache_get(), cache_set(), Optional shared JSON cache on Redis. Every call degrades to a no-op when Redis…, get_crop_health(), get_dashboard_outbreaks(), get_dashboard_report(), get_feedback_metrics(), get_stats() (+55 more)

### Community 35 - "advisory_context.py"
Cohesion: 0.48
Nodes (6): build_context(), _outbreaks(), Builds the DATA blocks that ground advisory answers. Sources are fetched…, _soil_text(), _weather(), _weather_text()

### Community 36 - "api.ts"
Cohesion: 0.13
Nodes (34): FarmPage(), SECTIONS, RiskRadar(), PracticeAdoption(), AdvisoryInput, AI_TIMEOUT_MS, API_BASE, ApiErrorCode (+26 more)

### Community 37 - "devDependencies"
Cohesion: 0.18
Nodes (11): devDependencies, eslint, eslint-config-next, @playwright/test, tailwindcss, @tailwindcss/postcss, @types/leaflet, @types/node (+3 more)

### Community 38 - "speech-core.ts"
Cohesion: 0.05
Nodes (34): ZERO, resetReachabilityProbe(), synthesizeSpeech(), audioPlayer(), BCP47, BlockedError, cleanForSpeech(), createSpeechController() (+26 more)

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
Nodes (24): _point_result(), Sentinel-2 / Earth Engine: credential handling, honest status reporting and…, _service(), _sources_and_ready(), _state(), test_bad_key_is_unavailable_not_a_silent_not_set_up(), test_cloudy_month_is_no_suitable_observation_not_a_number(), test_crop_health_reason_distinguishes_missing_from_broken_configuration() (+16 more)

### Community 44 - "routers/advisory.py"
Cohesion: 0.19
Nodes (23): AdvisoryRequest, AdvisoryResponse, DataSourceUse, FollowUpRequest, BaseModel, TranscribeRequest, TtsRequest, VoiceAdvisoryRequest (+15 more)

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
Cohesion: 0.14
Nodes (11): EarthEngineService, _iso_day(), date, Retry a failed start-up after a cool-down, so a transient outage does not…, Server-side dictionary for one window: median NDVI of clear pixels, scene…, NDVI of a window only when enough of the circle had clear pixels; None…, Mean of the cloud-masked median Sentinel-2 NDVI over a geometry and date window., Mean VV/VH backscatter (dB) per orbit direction; ascending and descending… (+3 more)

### Community 56 - "transcribe.md"
Cohesion: 0.40
Nodes (4): graphify reference: transcribe video and audio, print progress to stdout, which would otherwise corrupt the JSON file (#1392)., Step 2.5 - Transcribe video / audio files (only if video files detected), Write the JSON from Python (NOT a shell '>' redirect): transcribe_all/Whisper

### Community 57 - "logging"
Cohesion: 0.23
Nodes (8): Structured domain events (one JSON log line each) for intelligence, diagnosis,…, ASGI middleware: request IDs, access logging, security headers, last-resort…, Krishi Vigyan Kendra lookup from a small static reference list. The bundled…, google_cloud, json, logging, os, time

### Community 58 - "add-watch.md"
Cohesion: 0.50
Nodes (3): For --watch, For /graphify add, graphify reference: add a URL and watch a folder

### Community 59 - "hooks.md"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 60 - "interoperability.py"
Cohesion: 0.16
Nodes (26): Principal, BaseModel, Interoperability partners (another country's or state's system) may read…, require_partner_role(), PageV1, BaseModel, _adapter(), get_adapters() (+18 more)

### Community 61 - "frontend/README.md"
Cohesion: 0.50
Nodes (3): Getting Started, Learn More, or

### Community 79 - "tts_service.py"
Cohesion: 0.10
Nodes (20): Server-side image validation (never trust the client's Content-Type)., gemini_languages(), _gtts(), pcm_to_wav(), Text-to-speech with a native-language voice for every supported language.…, Drops Markdown symbols that voices would otherwise read out ("asterisk",…, Server voice per language: "gemini" (natural) or "gtts" (native but plainer)., Returns (audio bytes, MIME type, provider id). (+12 more)

### Community 80 - "datetime"
Cohesion: 0.08
Nodes (36): get_conditions(), get_crop_health(), get_crop_health_history(), get_crop_options(), get_farm_intelligence(), get_regenerative(), get_soil(), date (+28 more)

### Community 81 - "test_p02_regression.py"
Cohesion: 0.27
Nodes (12): jwt_secret(), asyncio, fixture, _stats(), test_client_cannot_choose_signal_id(), test_dashboard_report_generated_from_real_stats(), test_dashboard_report_insufficient_data_skips_ai(), test_federation_broadcast_signal_round_trip() (+4 more)

### Community 84 - "diagnosis.py"
Cohesion: 0.13
Nodes (19): AIDiagnosis, DiagnosisRequest, Differential, DiseaseReference, BaseModel, field_validator, One possible cause in a differential diagnosis., Keeps up to 3 well-formed entries; malformed model output is dropped, not… (+11 more)

### Community 85 - "federation.py"
Cohesion: 0.16
Nodes (16): AggregateResult, Aggregator, FedAvg, models_in_use(), ModelUpdate, ModelVersion, datetime, Protocol (+8 more)

### Community 87 - "farms.py"
Cohesion: 0.09
Nodes (35): log_event(), DataQuality, FarmInput, FarmIntelligence, Farm intelligence contract: the fused view of one farm that GET…, action_feedback(), create_farm(), farm_access() (+27 more)

### Community 88 - "test_farm_twin.py"
Cohesion: 0.44
Nodes (12): api(), create(), asyncio, Farm digital twin: creation, token access, snapshots, recommendation feedback…, sources(), test_create_farm_stores_no_personal_data_and_coarse_location(), test_diagnosis_linked_to_farm_supports_diagnosis_feedback_and_feeds_the_engine(), test_farm_requires_its_own_token() (+4 more)

### Community 89 - "test_interoperability.py"
Cohesion: 0.16
Nodes (12): auth(), asyncio, fixture, parametrize, BRICS interoperability: schema v1.0, country adapters, privacy-aware signal API…, secret(), test_another_country_plugs_in_through_an_adapter(), test_observations_are_aggregated_to_grid_cells_with_small_groups_suppressed() (+4 more)

### Community 90 - "app/page.tsx"
Cohesion: 0.16
Nodes (13): FEATURES, Home(), WorkflowDiagram(), Footer(), Header(), LanguageSelect(), Logo(), MobileNav() (+5 more)

### Community 91 - "parse_service_account_key"
Cohesion: 0.18
Nodes (12): CredentialError, parse_service_account_key(), The configured key cannot be used. `code` is safe to show to operators., Accept the service-account JSON as-is or base64-encoded (easier to paste into…, parametrize, _ready_service(), test_escaped_newlines_in_private_key_are_repaired(), test_key_accepted_raw_or_base64() (+4 more)

### Community 92 - "classify_error"
Cohesion: 0.14
Nodes (7): classify_error(), Map an Earth Engine / google-auth exception to a failure code. Order matters:…, Crop health at a point: NDVI now and 30 days earlier, the same-season baseline…, NDVI for the last HISTORY_WINDOWS consecutive 30-day windows (null where no…, Successful and no-imagery answers are cached for POINT_CACHE_TTL_S (a new pass…, test_unknown_query_failure_is_a_dataset_query_failure(), BaseException

### Community 93 - "ServiceUnavailableException"
Cohesion: 0.21
Nodes (8): ServiceUnavailableException, Compact current-conditions dict used as AI context and by the legacy…, WeatherService, test_intelligence_endpoint_when_weather_is_down(), test_regenerative_endpoint_reports_inputs(), test_all_providers_failing_is_503_not_wrong_voice(), test_gemini_failure_falls_back_to_native_gtts_voice(), Exception

### Community 94 - "_point_with"
Cohesion: 0.38
Nodes (10): _pass(), _point_with(), test_baseline_compares_with_the_same_weeks_of_previous_years(), test_baseline_needs_two_usable_years(), test_history_series_keeps_gaps_as_null(), test_no_radar_scene_and_radar_dataset_unavailable(), test_radar_compares_only_the_same_orbit_direction(), test_radar_is_reported_even_when_clouds_hide_the_field() (+2 more)

### Community 95 - "measurement.py"
Cohesion: 0.39
Nodes (7): _cell(), feedback_metrics(), _grouped(), App-derived feedback signals: how often recommendations are followed and what…, rows: (followed, outcome). Rates are over answered questions only., _summary(), math

### Community 96 - "pytest"
Cohesion: 0.18
Nodes (9): alembic_config, migrated_test_db(), fixture, Test database isolation. Tests delete rows, so they never touch the database in…, asyncio, Prove that hard-coded crop-health values are not returned., test_crop_health_unavailable(), pytest (+1 more)

### Community 97 - "Conversation.tsx"
Cohesion: 0.18
Nodes (17): AssistantMessage(), ChatMessage, Conversation(), SourceList(), errorMessage(), codeForStatus(), getSpeechVoices(), transcribeAudio() (+9 more)

### Community 98 - "farm_context.py"
Cohesion: 0.23
Nodes (14): build_farm_context(), _outbreaks(), Any, date, Builds the normalized FarmContext: every signal the intelligence engine reasons…, One input to the engine. status: available | unavailable | not_configured |…, (result, latency_ms, timed_out). The underlying task is shielded so a timeout…, _satellite() (+6 more)

### Community 100 - "GeminiService"
Cohesion: 0.28
Nodes (6): GeminiService, Models sometimes answer in the question's language instead of the requested…, Natural speech for `text`. Returns (16-bit mono PCM, sample rate)., language_name(), language_rule(), Prompt sentence pinning the reply language. "Native script" is only said for…

### Community 101 - "image_payload"
Cohesion: 0.22
Nodes (7): image_payload(), MockRedis, Regression: without Redis the limiter used to be silently disabled., test_rate_limit_falls_back_to_in_process_without_redis(), test_rate_limiting_flow(), test_trusted_proxy(), test_unsupported_language_rejected()

### Community 102 - "text_to_speech"
Cohesion: 0.22
Nodes (9): _audio_response(), get, Which server voice each language gets, so clients can prefer a better on-device…, Speech audio in the requested language. X-TTS-Provider says which voice was…, Deprecated: long non-Latin text makes very long URLs. Use POST…, text_to_speech(), text_to_speech_get(), tts_voices() (+1 more)

### Community 103 - "earth_engine_service.py"
Cohesion: 0.22
Nodes (7): _first(), Sentinel-2 crop health (NDVI) from Google Earth Engine. Dataset:…, Metadata of the newest scene in the window that passed the scene-cloud…, binascii, ee, google_auth_exceptions, threading

### Community 104 - "EscalationSink"
Cohesion: 0.25
Nodes (6): EscalationSink, NotConnectedSink, Protocol, No extension system is integrated yet: the case is returned to the farmer to…, Where a case goes. A KVK or state extension system implements `submit` and…, Contextual diagnosis, safety tiers and escalation

### Community 105 - "unittest_mock"
Cohesion: 0.25
Nodes (3): Server errors must reach the browser as errors, not as CORS failures that look…, fastapi_testclient, unittest_mock

### Community 107 - "next.config.ts"
Cohesion: 0.50
Nodes (3): apiOrigin, nextConfig, securityHeaders

### Community 108 - "Settings"
Cohesion: 0.67
Nodes (3): Settings, test_model_configuration_override(), BaseSettings

## Knowledge Gaps
- **232 isolated node(s):** `builds`, `routes`, `leaf`, `notImage`, `API` (+227 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 618 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Farm Intelligence Engine` connect `mock-api.ts` to `EscalationSink`?**
  _High betweenness centrality (0.390) - this node is a cross-community bridge._
- **Why does `Contextual diagnosis, safety tiers and escalation` connect `EscalationSink` to `mock-api.ts`?**
  _High betweenness centrality (0.389) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `ServiceUnavailableException` (e.g. with `install_error_handlers()` and `_weather()`) actually correct?**
  _`ServiceUnavailableException` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `builds`, `routes`, `leaf` to the rest of the system?**
  _232 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `i18n.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.08974358974358974 - nodes in this community are weakly interconnected._
- **Should `test_security.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09475806451612903 - nodes in this community are weakly interconnected._
- **Should `test_failure_states.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11688311688311688 - nodes in this community are weakly interconnected._
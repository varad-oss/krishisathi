# Graph Report - krishisathi  (2026-09-30)

## Corpus Check
- 194 files · ~159,357 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 6, .example 2, .ini 1)

## Summary
- 1810 nodes · 4525 edges · 110 communities (84 shown, 26 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 182 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `333e9a17`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- i18n.tsx
- test_security.py
- test_intelligence.py
- typing
- test_diagnosis.py
- layout.tsx
- test_speech_language.py
- test_advisory.py
- diagnose.py
- types.ts
- offline.ts
- errors.py
- useI18n
- api.test.mjs
- test_farm_intelligence.py
- datetime
- mock-api.ts
- .save_diagnosis
- india.py
- advisor/page.tsx
- interop.py
- package.json
- config.py
- compilerOptions
- dependencies
- diagnosis_policy.py
- farm_twin.py
- weather.py
- main.py
- eslint.config.mjs
- rate_limit.py
- cn
- states.py
- test_p03_outbreaks.py
- soil_service.py
- advisory_context.py
- api.ts
- devDependencies
- speech-core.ts
- createSpeechController
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
- gemini_service.py
- farm.py
- test_p02_regression.py
- diagnosis.py
- federation.py
- DiseaseReferenceService
- alerts.py
- test_farm_twin.py
- test_interoperability.py
- i18n.test.mjs
- parse_service_account_key
- classify_error
- ServiceUnavailableException
- _point_with
- measurement.py
- helpers.py
- speech.ts
- ApiError
- test_live_sentinel2_ndvi_for_a_ludhiana_wheat_field
- GeminiService
- images.py
- text_to_speech
- earth_engine_service.py
- EscalationSink
- unittest_mock
- _decode_limited
- next.config.ts
- _gtts
- Player

## God Nodes (most connected - your core abstractions)
1. `useI18n()` - 88 edges
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
- `Voice, offline use and the "something is wrong" entry point` --references--> `farm_intelligence()`  [INFERRED]
  docs/INTELLIGENCE.md → backend/services/intelligence_service.py
- `API (`backend/routers/interoperability.py`)` --references--> `RiskSignalV1`  [INFERRED]
  docs/INTEROPERABILITY.md → backend/models/interop_v1.py
- `Source status` --references--> `unavailable()`  [INFERRED]
  docs/EARTH_ENGINE.md → frontend/e2e/mock-api.ts
- `Inputs and their status` --references--> `unavailable()`  [INFERRED]
  docs/INTELLIGENCE.md → frontend/e2e/mock-api.ts
- `Regenerative plan and crop options` --references--> `unavailable()`  [INFERRED]
  docs/INTELLIGENCE.md → frontend/e2e/mock-api.ts

## Import Cycles
- None detected.

## Communities (110 total, 26 thin omitted)

### Community 0 - "i18n.tsx"
Cohesion: 0.08
Nodes (29): ProblemPage(), PROBLEMS, LanguageSelect(), AdvisoryInput, cache, I18nContext, I18nValue, interpolate() (+21 more)

### Community 1 - "test_security.py"
Cohesion: 0.07
Nodes (27): ai_down(), create_token(), err(), image_payload(), MockRedis, fixture, Regression: without Redis the limiter used to be silently disabled., Regression: allow_origins used to include '*' together with credentials. (+19 more)

### Community 2 - "test_intelligence.py"
Cohesion: 0.14
Nodes (23): parse_soilgrids(), rate_organic_carbon(), rate_ph(), Soil Health Card organic-carbon classes: <0.5 % low, 0.5–0.75 % medium, >0.75 %…, conditions(), ids(), asyncio, Weather parsing, agro rules, soil parsing and regenerative recommendations. (+15 more)

### Community 4 - "test_diagnosis.py"
Cohesion: 0.09
Nodes (40): ai_diagnosis(), jpeg_bytes(), post(), fixture, parametrize, reset_limits(), test_chemical_threshold_is_configurable_but_never_below_moderate(), test_confident_detection_includes_verified_reference() (+32 more)

### Community 5 - "layout.tsx"
Cohesion: 0.11
Nodes (22): frontend_src_app_globals, beng, body, deva, display, gujr, guru, knda (+14 more)

### Community 6 - "test_speech_language.py"
Cohesion: 0.09
Nodes (12): is_in_language(), Supported UI/response languages (allow-list). Codes match the frontend., Share of letters written in the language's script (Latin for English); 1.0 for…, True when the text is mostly in the native script. Technical terms (pH, NPK)…, script_ratio(), isolate(), fixture, Read-aloud voices and answer language: native voice per language, no English… (+4 more)

### Community 7 - "test_advisory.py"
Cohesion: 0.15
Nodes (23): _at(), parse_conditions(), Weather conditions from the Open-Meteo forecast API. Open-Meteo "current"…, weather_condition(), open_meteo_payload(), isolate(), fixture, run() (+15 more)

### Community 8 - "diagnose.py"
Cohesion: 0.20
Nodes (17): get_idempotency_result(), set_idempotency_result(), diagnose_base64(), diagnose_multipart(), _farm(), _farm_block(), _nearby(), process_diagnosis() (+9 more)

### Community 9 - "types.ts"
Cohesion: 0.04
Nodes (73): FarmHistoryCard(), AlertView, Fmt, insightView(), T, whenLabel(), DataQualityStrip(), DQ_ICON (+65 more)

### Community 10 - "offline.ts"
Cohesion: 0.26
Nodes (13): deliver(), OfflineStatus(), Cached, enqueue(), flushOutbox(), OutboxItem, readOutbox(), useOnline() (+5 more)

### Community 11 - "errors.py"
Cohesion: 0.13
Nodes (17): error_body(), _from_detail(), install_error_handlers(), _api_error(), _http_error(), _service_unavailable(), _validation_error(), FastAPI (+9 more)

### Community 12 - "useI18n"
Cohesion: 0.10
Nodes (30): ErrorPage(), NotFound(), AssistantMessage(), Conversation(), SourceList(), EscalationCard(), RiskRadar(), KvkCard() (+22 more)

### Community 13 - "api.test.mjs"
Cohesion: 0.15
Nodes (6): resetReachabilityProbe(), realNavigator, events, store, ref_node_assert, ref_node_test

### Community 14 - "test_farm_intelligence.py"
Cohesion: 0.06
Nodes (86): DataQuality, Evidence, FarmInput, BaseModel, Farm intelligence contract: the fused view of one farm that GET…, Risk, RuleRef, TopAction (+78 more)

### Community 15 - "datetime"
Cohesion: 0.36
Nodes (7): AsyncClient, download_image(), fetch_image_list(), run_validation_suite(), datetime, random, sklearn_metrics

### Community 16 - "mock-api.ts"
Cohesion: 0.06
Nodes (39): Error codes, History series, Limits, One-time setup, Same-season baseline (temporal context), Sentinel-1 radar (cloud-resilient), Sentinel-2 crop health via Google Earth Engine, Source status (+31 more)

### Community 17 - ".save_diagnosis"
Cohesion: 0.14
Nodes (9): _haversine(), normalize_level(), outbreak_eligible(), _public_coord(), Outbreak clusters with coordinates rounded to ~11 km. Stale clusters are…, Aggregated counts from stored records only. No external or estimated figures., Maps legacy 'Medium'/'High' values and new levels onto low | moderate | high., Only confident, located disease detections may contribute to outbreak clusters. (+1 more)

### Community 18 - "india.py"
Cohesion: 0.06
Nodes (55): AdvisoryV1, CropV1, DiseaseV1, FarmerRefV1, FarmV1, GeoRefV1, GridCellV1, json_schemas() (+47 more)

### Community 19 - "advisor/page.tsx"
Cohesion: 0.10
Nodes (41): AdvisorPage(), LastAnswer(), SavedAnswer, TOPICS, DiagnosePage(), Phase, ChatMessage, FarmProfileForm() (+33 more)

### Community 20 - "interop.py"
Cohesion: 0.16
Nodes (17): AggregatedStateReport, BaseModel, Interoperability data models for cross-state agricultural data sharing. These…, Strip any personally identifiable information before data flows from a state-…, Standard payload for cross-state agricultural data exchange. Any state system…, Per-state configuration that adapts KrishiSathi to local context. The same…, National-level aggregation of state signals — for the policymaker dashboard., RegionalAgriSignal (+9 more)

### Community 21 - "package.json"
Cohesion: 0.13
Nodes (14): name, private, version, clsx, react-dom, tailwind-merge, tailwindcss, @tailwindcss/postcss (+6 more)

### Community 22 - "config.py"
Cohesion: 0.13
Nodes (7): Settings, list_sources(), get, Public description of every data source the platform uses and whether it is…, test_model_configuration_override(), BaseSettings, pydantic_settings

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 24 - "dependencies"
Cohesion: 0.15
Nodes (13): dependencies, clsx, leaflet, lucide-react, next, react, react-dom, react-leaflet (+5 more)

### Community 25 - "diagnosis_policy.py"
Cohesion: 0.27
Nodes (10): AIDiagnosis, Shape the vision model must return. Anything else is rejected as an invalid AI…, apply_safety_rules(), _at_least(), build_case(), guidance(), Rules the diagnosis model cannot override: treatment gating, guidance level and…, Post-validation rules. Chemical options survive only with a verified reference… (+2 more)

### Community 26 - "farm_twin.py"
Cohesion: 0.07
Nodes (54): log_event(), FarmIntelligence, AdvisoryActionRecord, FarmRecord, FarmSnapshotRecord, What the intelligence engine concluded for a farm at one time: the twin's…, A recommendation given to a farm and the farmer's self-reported follow-through…, Farm digital twin: a farmer's field. Access is by a bearer farm token whose… (+46 more)

### Community 27 - "weather.py"
Cohesion: 0.67
Nodes (3): get_current_weather(), get_forecast(), get

### Community 28 - "main.py"
Cohesion: 0.10
Nodes (29): ensure_tables(), health_live(), health_ready(), lazy_db_init(), lifespan(), FastAPI, get, Creates missing tables once per process. Serverless deployments (Vercel) may… (+21 more)

### Community 29 - "eslint.config.mjs"
Cohesion: 0.50
Nodes (3): eslintConfig, eslint, eslint-config-next

### Community 30 - "rate_limit.py"
Cohesion: 0.36
Nodes (9): ai_rate_limit(), _client_ip(), _local_incr(), Request, rate_limit(), tts_rate_limit(), interop_limit(), Request (+1 more)

### Community 31 - "cn"
Cohesion: 0.09
Nodes (48): FEATURES, Home(), WorkflowDiagram(), DiagnosisResult(), StepList(), ActionFeedback(), Choices(), FOLLOWED (+40 more)

### Community 32 - "states.py"
Cohesion: 0.12
Nodes (21): get_current_user(), Principal, BaseModel, Validates an HS256 JWT signed with settings.JWT_SECRET. Fails closed: when no…, Interoperability partners (another country's or state's system) may read…, require_partner_role(), require_system_role(), get_ee_status() (+13 more)

### Community 33 - "test_p03_outbreaks.py"
Cohesion: 0.22
Nodes (15): clear_db(), asyncio, fixture, parametrize, test_daily_diagnoses_are_zero_filled_for_days_without_records(), test_diagnoses_without_location_are_recorded_but_not_clustered(), test_ineligible_diagnoses_never_form_outbreaks(), test_insufficient_observations_no_outbreak() (+7 more)

### Community 34 - "soil_service.py"
Cohesion: 0.13
Nodes (22): cache_get(), cache_set(), Optional shared JSON cache on Redis. Every call degrades to a no-op when Redis…, get_crop_health(), get_dashboard_outbreaks(), get_dashboard_report(), get_feedback_metrics(), get_stats() (+14 more)

### Community 35 - "advisory_context.py"
Cohesion: 0.19
Nodes (12): build_context(), _intelligence_text(), _outbreaks(), Builds the DATA blocks that ground advisory answers. Sources are fetched…, _soil_text(), _weather(), _weather_text(), evaluate() (+4 more)

### Community 36 - "api.ts"
Cohesion: 0.10
Nodes (48): AboutPage(), PolicyDashboardPage(), FarmPage(), SECTIONS, PracticeAdoption(), SatelliteHistory(), PublishForm(), AI_TIMEOUT_MS (+40 more)

### Community 37 - "devDependencies"
Cohesion: 0.18
Nodes (11): devDependencies, eslint, eslint-config-next, @playwright/test, tailwindcss, @tailwindcss/postcss, @types/leaflet, @types/node (+3 more)

### Community 38 - "speech-core.ts"
Cohesion: 0.16
Nodes (12): BCP47, isHighQualityVoice(), normLang(), pickVoice(), SpeechController, SpeechEngine, SpeechErrorCode, SpeechState (+4 more)

### Community 39 - "createSpeechController"
Cohesion: 0.29
Nodes (7): cleanForSpeech(), createSpeechController(), play(), playDevice(), playServer(), stop(), SpeechDeps

### Community 40 - "test_soil.py"
Cohesion: 0.09
Nodes (29): haversine_km(), KvkService, Great-circle distance in kilometres (spherical Earth, R = 6371 km)., KVK for the district nearest to (lat, lng), or None when no listed district is…, KVK lookup: never report a distance to a district reference point as a distance…, test_empty_list_returns_none(), test_haversine_known_distance(), test_haversine_zero_and_symmetry() (+21 more)

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
Cohesion: 0.21
Nodes (21): AdvisoryRequest, AdvisoryResponse, DataSourceUse, FollowUpRequest, BaseModel, TranscribeRequest, TtsRequest, VoiceAdvisoryRequest (+13 more)

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
Nodes (7): Structured domain events (one JSON log line each) for intelligence, diagnosis,…, ASGI middleware: request IDs, access logging, security headers, last-resort…, Krishi Vigyan Kendra lookup from a small static reference list. The bundled…, google_cloud, json, logging, time

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

### Community 79 - "gemini_service.py"
Cohesion: 0.11
Nodes (20): All Gemini calls. Model output is treated as untrusted: * every call is async…, untrusted(), gemini_languages(), pcm_to_wav(), Text-to-speech with a native-language voice for every supported language.…, Drops Markdown symbols that voices would otherwise read out ("asterisk",…, Server voice per language: "gemini" (natural) or "gtts" (native but plainer)., Returns (audio bytes, MIME type, provider id). (+12 more)

### Community 80 - "farm.py"
Cohesion: 0.10
Nodes (31): get_conditions(), get_crop_health(), get_crop_health_history(), get_crop_options(), get_farm_intelligence(), get_regenerative(), get_soil(), date (+23 more)

### Community 81 - "test_p02_regression.py"
Cohesion: 0.27
Nodes (12): jwt_secret(), asyncio, fixture, _stats(), test_client_cannot_choose_signal_id(), test_dashboard_report_generated_from_real_stats(), test_dashboard_report_insufficient_data_skips_ai(), test_federation_broadcast_signal_round_trip() (+4 more)

### Community 84 - "diagnosis.py"
Cohesion: 0.18
Nodes (12): DiagnosisRequest, DiagnosisResponse, Differential, DiseaseReference, BaseModel, field_validator, One possible cause in a differential diagnosis., Keeps up to 3 well-formed entries; malformed model output is dropped, not… (+4 more)

### Community 85 - "federation.py"
Cohesion: 0.16
Nodes (16): AggregateResult, Aggregator, FedAvg, models_in_use(), ModelUpdate, ModelVersion, datetime, Protocol (+8 more)

### Community 87 - "alerts.py"
Cohesion: 0.42
Nodes (7): DiseaseAlert, OutbreakReport, BaseModel, get_alerts(), get_outbreaks(), get_personalized_alerts(), get

### Community 88 - "test_farm_twin.py"
Cohesion: 0.44
Nodes (12): api(), create(), asyncio, Farm digital twin: creation, token access, snapshots, recommendation feedback…, sources(), test_create_farm_stores_no_personal_data_and_coarse_location(), test_diagnosis_linked_to_farm_supports_diagnosis_feedback_and_feeds_the_engine(), test_farm_requires_its_own_token() (+4 more)

### Community 89 - "test_interoperability.py"
Cohesion: 0.15
Nodes (13): auth(), clean_db(), asyncio, fixture, parametrize, BRICS interoperability: schema v1.0, country adapters, privacy-aware signal API…, secret(), test_observations_are_aggregated_to_grid_cells_with_small_groups_suppressed() (+5 more)

### Community 90 - "i18n.test.mjs"
Cohesion: 0.28
Nodes (4): ZERO, en, ref_node_child_process, ref_node_fs

### Community 91 - "parse_service_account_key"
Cohesion: 0.18
Nodes (12): CredentialError, parse_service_account_key(), The configured key cannot be used. `code` is safe to show to operators., Accept the service-account JSON as-is or base64-encoded (easier to paste into…, parametrize, _ready_service(), test_escaped_newlines_in_private_key_are_repaired(), test_key_accepted_raw_or_base64() (+4 more)

### Community 92 - "classify_error"
Cohesion: 0.14
Nodes (7): classify_error(), Map an Earth Engine / google-auth exception to a failure code. Order matters:…, Crop health at a point: NDVI now and 30 days earlier, the same-season baseline…, NDVI for the last HISTORY_WINDOWS consecutive 30-day windows (null where no…, Successful and no-imagery answers are cached for POINT_CACHE_TTL_S (a new pass…, test_unknown_query_failure_is_a_dataset_query_failure(), BaseException

### Community 93 - "ServiceUnavailableException"
Cohesion: 0.24
Nodes (7): ServiceUnavailableException, Compact current-conditions dict used as AI context and by the legacy…, WeatherService, test_intelligence_endpoint_when_weather_is_down(), test_regenerative_endpoint_reports_inputs(), test_all_providers_failing_is_503_not_wrong_voice(), Exception

### Community 94 - "_point_with"
Cohesion: 0.38
Nodes (10): _pass(), _point_with(), test_baseline_compares_with_the_same_weeks_of_previous_years(), test_baseline_needs_two_usable_years(), test_history_series_keeps_gaps_as_null(), test_no_radar_scene_and_radar_dataset_unavailable(), test_radar_compares_only_the_same_orbit_direction(), test_radar_is_reported_even_when_clouds_hide_the_field() (+2 more)

### Community 95 - "measurement.py"
Cohesion: 0.39
Nodes (7): _cell(), feedback_metrics(), _grouped(), App-derived feedback signals: how often recommendations are followed and what…, rows: (followed, outcome). Rates are over answered questions only., _summary(), math

### Community 96 - "helpers.py"
Cohesion: 0.09
Nodes (22): alembic_config, asyncio, do_run_migrations(), run_async_migrations(), run_migrations_online(), Operator check: is Sentinel-2 via Earth Engine really working with these…, migrated_test_db(), fixture (+14 more)

### Community 97 - "speech.ts"
Cohesion: 0.23
Nodes (13): getSpeechVoices(), synthesizeSpeech(), transcribeAudio(), audioPlayer(), cleanup(), BlockedError, devicePlayer(), IDLE (+5 more)

### Community 98 - "ApiError"
Cohesion: 0.29
Nodes (6): ApiError, HTTPException carrying an explicit machine-readable code., get_nearest_kvk(), get, KVK for the district nearest the location. `distance_km` is null unless the KVK…, HTTPException

### Community 100 - "GeminiService"
Cohesion: 0.28
Nodes (6): GeminiService, Models sometimes answer in the question's language instead of the requested…, Natural speech for `text`. Returns (16-bit mono PCM, sample rate)., language_name(), language_rule(), Prompt sentence pinning the reply language. "Native script" is only said for…

### Community 101 - "images.py"
Cohesion: 0.33
Nodes (5): Server-side image validation (never trust the client's Content-Type)., Validates the bytes are a real, reasonably sized JPEG/PNG/WebP image; returns…, sniff_image(), io, pil

### Community 102 - "text_to_speech"
Cohesion: 0.22
Nodes (9): _audio_response(), get, Which server voice each language gets, so clients can prefer a better on-device…, Speech audio in the requested language. X-TTS-Provider says which voice was…, Deprecated: long non-Latin text makes very long URLs. Use POST…, text_to_speech(), text_to_speech_get(), tts_voices() (+1 more)

### Community 103 - "earth_engine_service.py"
Cohesion: 0.22
Nodes (7): _first(), Sentinel-2 crop health (NDVI) from Google Earth Engine. Dataset:…, Metadata of the newest scene in the window that passed the scene-cloud…, binascii, ee, google_auth_exceptions, threading

### Community 104 - "EscalationSink"
Cohesion: 0.25
Nodes (6): EscalationSink, NotConnectedSink, Protocol, No extension system is integrated yet: the case is returned to the farmer to…, Where a case goes. A KVK or state extension system implements `submit` and…, Contextual diagnosis, safety tiers and escalation

### Community 107 - "next.config.ts"
Cohesion: 0.50
Nodes (3): apiOrigin, nextConfig, securityHeaders

## Knowledge Gaps
- **237 isolated node(s):** `builds`, `routes`, `leaf`, `notImage`, `API` (+232 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 627 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Farm Intelligence Engine` connect `mock-api.ts` to `EscalationSink`?**
  _High betweenness centrality (0.409) - this node is a cross-community bridge._
- **Why does `@playwright/test` connect `mock-api.ts` to `package.json`?**
  _High betweenness centrality (0.385) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `ServiceUnavailableException` (e.g. with `install_error_handlers()` and `_weather()`) actually correct?**
  _`ServiceUnavailableException` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `builds`, `routes`, `leaf` to the rest of the system?**
  _237 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `i18n.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.07973421926910298 - nodes in this community are weakly interconnected._
- **Should `test_security.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0743321718931475 - nodes in this community are weakly interconnected._
- **Should `test_intelligence.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13846153846153847 - nodes in this community are weakly interconnected._
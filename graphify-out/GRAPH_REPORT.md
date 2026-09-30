# Graph Report - krishisathi  (2026-09-30)

## Corpus Check
- 213 files · ~199,497 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 6, .example 2, .ini 1)

## Summary
- 2162 nodes · 5586 edges · 119 communities (95 shown, 24 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 263 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d00e872a`
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
- test_failure_states.py
- diagnose.py
- TodayAlertsWeather.tsx
- offline.ts
- errors.py
- useI18n
- farms.py
- risk_engine.py
- database.py
- mock-api.ts
- .get_dashboard_stats
- test_interop_schemas.py
- advisor/page.tsx
- test_p02_regression.py
- package.json
- asyncio
- compilerOptions
- dependencies
- cn
- farm_twin.py
- main.py
- persistence_service.py
- test_farm_intelligence.py
- rate_limit.py
- types.ts
- ApiError
- test_p03_outbreaks.py
- dashboard.py
- advisory_context.py
- api.ts
- devDependencies
- speech-core.ts
- ._cached
- test_soil.py
- manifest.json
- scripts
- test_plots.py
- routers/advisory.py
- exports.md
- github-and-merge.md
- query.md
- update.md
- SKILL.md
- AGENTS.md
- .log_diagnosis
- AUDIT.md
- PlotMap.tsx
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
- measurement.py
- farm.py
- datetime
- brazil.py
- federation.py
- test_brazil_adapter.py
- interop_v1.py
- validate_polygon
- test_interoperability.py
- CountryAdapter
- api.test.mjs
- earth_engine_service.py
- ServiceUnavailableException
- test_earth_engine.py
- FarmContext
- generate_e2e_fixtures.py
- BrazilAdapter
- speech.ts
- test_evaluation.py
- gemini_service.py
- test_farm_twin.py
- Farm Intelligence Engine
- weather_service.py
- journeys.spec.ts
- LanguageCode
- Sentinel-2 / Sentinel-1 field signals via Google Earth Engine
- next.config.ts
- geo.ts
- test_disease_reference.py
- i18n.test.mjs
- EscalationSink
- _grade
- PartnerAdapter
- DiseaseReferenceService
- crop_code
- Player
- screenshots.spec.ts
- Farm digital twin and the action → outcome loop

## God Nodes (most connected - your core abstractions)
1. `useI18n()` - 106 edges
2. `cn()` - 72 edges
3. `EarthEngineService` - 50 edges
4. `ServiceUnavailableException` - 49 edges
5. `request()` - 41 edges
6. `ctx()` - 37 edges
7. `ApiError` - 34 edges
8. `post()` - 33 edges
9. `FarmContext` - 31 edges
10. `FarmRecord` - 29 edges

## Surprising Connections (you probably didn't know these)
- `Voice, offline use and the "something is wrong" entry point` --references--> `farm_intelligence()`  [INFERRED]
  docs/INTELLIGENCE.md → backend/services/intelligence_service.py
- `Field outline (plots)` --references--> `area_ha()`  [INFERRED]
  docs/INTELLIGENCE.md → backend/services/plots.py
- `Risk level vs evidence confidence (engine 1.1)` --references--> `_grade()`  [INFERRED]
  docs/INTELLIGENCE.md → backend/services/risk_engine.py
- `Field outline, pixels and mixed land (data quality)` --references--> `unavailable()`  [INFERRED]
  docs/EARTH_ENGINE.md → frontend/e2e/mock-api.ts
- `Source status` --references--> `unavailable()`  [INFERRED]
  docs/EARTH_ENGINE.md → frontend/e2e/mock-api.ts

## Import Cycles
- None detected.

## Communities (119 total, 24 thin omitted)

### Community 0 - "i18n.tsx"
Cohesion: 0.09
Nodes (28): AlertView, Fmt, T, cache, I18nContext, I18nValue, interpolate(), isLanguage() (+20 more)

### Community 1 - "test_security.py"
Cohesion: 0.07
Nodes (27): ai_down(), create_token(), err(), image_payload(), MockRedis, fixture, Regression: without Redis the limiter used to be silently disabled., Regression: allow_origins used to include '*' together with credentials. (+19 more)

### Community 2 - "test_intelligence.py"
Cohesion: 0.14
Nodes (23): parse_soilgrids(), rate_organic_carbon(), rate_ph(), Soil Health Card organic-carbon classes: <0.5 % low, 0.5–0.75 % medium, >0.75 %…, conditions(), ids(), asyncio, Weather parsing, agro rules, soil parsing and regenerative recommendations. (+15 more)

### Community 3 - "typing"
Cohesion: 0.08
Nodes (10): alembic, DiseaseAlert, OutbreakReport, BaseModel, get_alerts(), get_outbreaks(), get_personalized_alerts(), get (+2 more)

### Community 4 - "test_diagnosis.py"
Cohesion: 0.19
Nodes (25): ai_diagnosis(), post(), fixture, parametrize, reset_limits(), test_chemical_threshold_is_configurable_but_never_below_moderate(), test_confident_detection_includes_verified_reference(), test_differential_is_returned_and_malformed_entries_dropped() (+17 more)

### Community 5 - "layout.tsx"
Cohesion: 0.10
Nodes (22): frontend_src_app_globals, beng, body, deva, display, gujr, guru, knda (+14 more)

### Community 6 - "test_speech_language.py"
Cohesion: 0.06
Nodes (21): Server-side image validation (never trust the client's Content-Type)., _gtts(), pcm_to_wav(), Text-to-speech with a native-language voice for every supported language.…, Drops Markdown symbols that voices would otherwise read out ("asterisk",…, speech_text(), Shared test fixtures/data (imported by test modules; pytest puts this directory…, isolate() (+13 more)

### Community 7 - "test_failure_states.py"
Cohesion: 0.08
Nodes (19): jpeg_bytes(), Server errors must reach the browser as errors, not as CORS failures that look…, test_tiny_image_rejected(), clear_caches(), asyncio, fixture, parametrize, Every upstream failure must surface as an explicit, retryable error, never as… (+11 more)

### Community 8 - "diagnose.py"
Cohesion: 0.09
Nodes (39): get_idempotency_result(), set_idempotency_result(), AIDiagnosis, DiagnosisRequest, DiagnosisResponse, Differential, DiseaseReference, BaseModel (+31 more)

### Community 9 - "TodayAlertsWeather.tsx"
Cohesion: 0.09
Nodes (41): Choices(), FarmHistoryCard(), FOLLOWED, OUTCOMES, whenLabel(), ConfidenceChip(), ConfidenceWhy(), DataQualityStrip() (+33 more)

### Community 10 - "offline.ts"
Cohesion: 0.23
Nodes (15): deliver(), OfflineStatus(), recordPractice(), sendFeedback(), Cached, enqueue(), flushOutbox(), OutboxItem (+7 more)

### Community 11 - "errors.py"
Cohesion: 0.12
Nodes (19): error_body(), _from_detail(), install_error_handlers(), _api_error(), _http_error(), _service_unavailable(), _validation_error(), FastAPI (+11 more)

### Community 12 - "useI18n"
Cohesion: 0.09
Nodes (44): AboutPage(), NotFound(), ActionFeedback(), insightView(), PracticeAdoption(), WeatherMeaning(), CATEGORIES, Country() (+36 more)

### Community 13 - "farms.py"
Cohesion: 0.08
Nodes (33): log_event(), Structured domain events (one JSON log line each) for intelligence, diagnosis,…, action_feedback(), create_farm(), delete_plot(), FarmProfileIn, FarmTwinIntelligence, FeedbackIn (+25 more)

### Community 14 - "risk_engine.py"
Cohesion: 0.18
Nodes (37): Evidence, FarmInput, BaseModel, Farm intelligence contract: the fused view of one farm that GET…, `severity` is the risk level: how concerning the condition would be if the…, Risk, RuleRef, TopAction (+29 more)

### Community 15 - "database.py"
Cohesion: 0.18
Nodes (10): do_run_migrations(), run_async_migrations(), run_migrations_online(), Connection, logging_config, sqlalchemy_engine, sqlalchemy_ext_asyncio, sqlalchemy_orm (+2 more)

### Community 16 - "mock-api.ts"
Cohesion: 0.25
Nodes (10): frontend_e2e_fixtures_api, API, Fixtures, fresh(), json(), minutesAgo(), mockApi(), Override (+2 more)

### Community 18 - "test_interop_schemas.py"
Cohesion: 0.19
Nodes (17): GeoRefV1, json_schemas(), PeriodV1, ProvenanceV1, Any, cell(), _grid_geo(), IndiaAdapter (+9 more)

### Community 19 - "advisor/page.tsx"
Cohesion: 0.10
Nodes (40): AdvisorPage(), LastAnswer(), SavedAnswer, TOPICS, DiagnosePage(), Phase, ErrorPage(), FarmProfileForm() (+32 more)

### Community 20 - "test_p02_regression.py"
Cohesion: 0.10
Nodes (30): AggregatedStateReport, BaseModel, Interoperability data models for cross-state agricultural data sharing. These…, Strip any personally identifiable information before data flows from a state-…, Standard payload for cross-state agricultural data exchange. Any state system…, Per-state configuration that adapts KrishiSathi to local context. The same…, National-level aggregation of state signals — for the policymaker dashboard., RegionalAgriSignal (+22 more)

### Community 21 - "package.json"
Cohesion: 0.11
Nodes (17): eslintConfig, name, private, version, clsx, eslint, eslint-config-next, react-dom (+9 more)

### Community 22 - "asyncio"
Cohesion: 0.13
Nodes (16): AsyncClient, asyncio, Operator check: is Sentinel-2 via Earth Engine really working with these…, download_image(), fetch_image_list(), run_validation_suite(), Krishi Vigyan Kendra lookup from a small static reference list. The bundled…, asyncio (+8 more)

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 24 - "dependencies"
Cohesion: 0.15
Nodes (13): dependencies, clsx, leaflet, lucide-react, next, react, react-dom, react-leaflet (+5 more)

### Community 25 - "cn"
Cohesion: 0.09
Nodes (36): FEATURES, Home(), WorkflowDiagram(), ProblemPage(), PROBLEMS, AssistantMessage(), ChatMessage, Conversation() (+28 more)

### Community 26 - "farm_twin.py"
Cohesion: 0.09
Nodes (43): AdvisoryActionRecord, FarmPlotRecord, FarmRecord, FarmSnapshotRecord, What the intelligence engine concluded for a farm at one time: the twin's…, A recommendation given to a farm and the farmer's self-reported follow-through…, The farmer's optional field outline (one per farm). GeoJSON Polygon, private to…, Farm digital twin: a farmer's field. Access is by a bearer farm token whose… (+35 more)

### Community 27 - "main.py"
Cohesion: 0.11
Nodes (19): ensure_tables(), health_live(), health_ready(), lazy_db_init(), lifespan(), FastAPI, get, Creates missing tables once per process. Serverless deployments (Vercel) may… (+11 more)

### Community 28 - "persistence_service.py"
Cohesion: 0.11
Nodes (27): AdvisoryRecord, DiagnosisRecord, FederationSignalRecord, OutbreakRecord, _haversine(), nearby_outbreaks(), normalize_level(), outbreak_eligible() (+19 more)

### Community 29 - "test_farm_intelligence.py"
Cohesion: 0.12
Nodes (37): One input to the engine. status: available | unavailable | not_configured |…, Signal, ctx(), Farm intelligence: crop stage, soil water, risk engine, prioritization and the…, The documented example: rain likely and soil already wet -> delay irrigation,…, risks_by_category(), test_assembled_intelligence_reports_data_quality(), test_disease_combines_weather_reports_and_farm_history() (+29 more)

### Community 30 - "rate_limit.py"
Cohesion: 0.21
Nodes (13): ai_rate_limit(), _client_ip(), _local_incr(), Request, rate_limit(), tts_rate_limit(), create_limit(), Request (+5 more)

### Community 31 - "types.ts"
Cohesion: 0.04
Nodes (62): ADOPTION, CropOptionsCard(), HORIZONS, PracticeItem(), PracticePlan(), TriggerText, CropHealthCard(), KvkCard() (+54 more)

### Community 32 - "ApiError"
Cohesion: 0.09
Nodes (28): ApiError, HTTPException carrying an explicit machine-readable code., get_current_user(), Validates an HS256 JWT signed with settings.JWT_SECRET. Fails closed: when no…, Record-level evaluation exports: operators only., require_admin_role(), require_system_role(), get_ee_status() (+20 more)

### Community 33 - "test_p03_outbreaks.py"
Cohesion: 0.26
Nodes (13): asyncio, parametrize, test_daily_diagnoses_are_zero_filled_for_days_without_records(), test_diagnoses_without_location_are_recorded_but_not_clustered(), test_ineligible_diagnoses_never_form_outbreaks(), test_insufficient_observations_no_outbreak(), test_outbreak_coordinates_are_coarsened_for_privacy(), test_outside_radius_separate_cluster() (+5 more)

### Community 34 - "dashboard.py"
Cohesion: 0.07
Nodes (49): cache_get(), cache_set(), Optional shared JSON cache on Redis. Every call degrades to a no-op when Redis…, get_crop_health(), get_dashboard_outbreaks(), get_dashboard_report(), get_early_warning(), get_evaluation() (+41 more)

### Community 35 - "advisory_context.py"
Cohesion: 0.26
Nodes (11): build_context(), _intelligence_text(), _outbreaks(), Builds the DATA blocks that ground advisory answers. Sources are fetched…, _soil_text(), _weather(), _weather_text(), evaluate() (+3 more)

### Community 36 - "api.ts"
Cohesion: 0.08
Nodes (58): PolicyDashboardPage(), FarmPage(), SECTIONS, FieldOutline(), RiskRadar(), SatelliteHistory(), Skeleton(), AI_TIMEOUT_MS (+50 more)

### Community 37 - "devDependencies"
Cohesion: 0.18
Nodes (11): devDependencies, eslint, eslint-config-next, @playwright/test, tailwindcss, @tailwindcss/postcss, @types/leaflet, @types/node (+3 more)

### Community 38 - "speech-core.ts"
Cohesion: 0.17
Nodes (12): BCP47, cleanForSpeech(), isHighQualityVoice(), normLang(), pickVoice(), SpeechController, SpeechEngine, SpeechErrorCode (+4 more)

### Community 39 - "._cached"
Cohesion: 0.22
Nodes (5): Crop health at a point: NDVI now and 30 days earlier, the same-season baseline…, The same analysis over the farmer's drawn field (plot: {"geometry", "area_ha"})., Prefers the drawn field; falls back to the 250 m circle around the farm point., NDVI for the last HISTORY_WINDOWS consecutive 30-day windows (null where no…, Successful and no-imagery answers are cached for POINT_CACHE_TTL_S (a new pass…

### Community 40 - "test_soil.py"
Cohesion: 0.21
Nodes (18): get(), fixture, SoilGrids integration: each failure mode is reported with its own reason, never…, reset(), resp(), test_concurrent_requests_share_one_upstream_call(), slow(), test_endpoint_exposes_reason() (+10 more)

### Community 41 - "manifest.json"
Cohesion: 0.22
Nodes (8): background_color, description, display, icons, name, short_name, start_url, theme_color

### Community 42 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, start, test, test:e2e, typecheck

### Community 43 - "test_plots.py"
Cohesion: 0.13
Nodes (35): point_field(), polygon_field(), plot: a stored, validated plot ({"geometry": GeoJSON Polygon, "area_ha":…, geometry_key(), Stable, non-reversible cache key for a geometry (coordinates never appear in…, api(), clean(), create() (+27 more)

### Community 44 - "routers/advisory.py"
Cohesion: 0.10
Nodes (38): AdvisoryRequest, AdvisoryResponse, DataSourceUse, _decode_limited(), FollowUpRequest, BaseModel, field_validator, TranscribeRequest (+30 more)

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

### Community 53 - "PlotMap.tsx"
Cohesion: 0.18
Nodes (7): PlotMap, COLORS, OutbreakMap, Position, Outbreak, leaflet, react-leaflet

### Community 54 - "README.md"
Cohesion: 0.33
Nodes (5): Architecture, Backend, Real data only, Running locally, What it does

### Community 55 - "EarthEngineService"
Cohesion: 0.09
Nodes (17): EarthEngineService, _first(), _iso_day(), date, Retry a failed start-up after a cool-down, so a transient outage does not…, Server-side dictionary for one window: median NDVI of clear pixels, scene…, Pixel count of the region (polygon only; the point circle is a constant) and…, NDVI of a window only when enough of the region had clear pixels; None… (+9 more)

### Community 56 - "transcribe.md"
Cohesion: 0.40
Nodes (4): graphify reference: transcribe video and audio, print progress to stdout, which would otherwise corrupt the JSON file (#1392)., Step 2.5 - Transcribe video / audio files (only if video files detected), Write the JSON from Python (NOT a shell '>' redirect): transcribe_all/Whisper

### Community 57 - "test_kvk.py"
Cohesion: 0.16
Nodes (10): haversine_km(), KvkService, Great-circle distance in kilometres (spherical Earth, R = 6371 km)., KVK for the district nearest to (lat, lng), or None when no listed district is…, KVK lookup: never report a distance to a district reference point as a distance…, test_empty_list_returns_none(), test_haversine_known_distance(), test_haversine_zero_and_symmetry() (+2 more)

### Community 58 - "add-watch.md"
Cohesion: 0.50
Nodes (3): For --watch, For /graphify add, graphify reference: add a URL and watch a folder

### Community 59 - "hooks.md"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 60 - "interoperability.py"
Cohesion: 0.15
Nodes (29): Principal, BaseModel, Interoperability partners (another country's or state's system) may read…, require_partner_role(), _adapter(), compare(), get_adapters(), get_crops() (+21 more)

### Community 61 - "frontend/README.md"
Cohesion: 0.50
Nodes (3): Getting Started, Learn More, or

### Community 79 - "measurement.py"
Cohesion: 0.13
Nodes (23): _advisory_feedback(), _cell(), _diagnosis_feedback(), _diagnosis_rows(), evaluation_metrics(), by_tier(), evaluation_records(), feedback_metrics() (+15 more)

### Community 80 - "farm.py"
Cohesion: 0.10
Nodes (29): get_conditions(), get_crop_health(), get_crop_health_history(), get_crop_options(), get_farm_intelligence(), get_regenerative(), get_soil(), date (+21 more)

### Community 81 - "datetime"
Cohesion: 0.10
Nodes (27): estimate_stage(), date, Stage estimate with `status`: estimated | not_provided | no_calendar |…, build_farm_context(), _outbreaks(), Any, date, Builds the normalized FarmContext: every signal the intelligence engine reasons… (+19 more)

### Community 84 - "brazil.py"
Cohesion: 0.12
Nodes (24): ObservationV1, One aggregated observation, e.g. the number of AI-classified disease detections…, Exception, The national source exists but could not be read now. `code` is safe to show., SourceUnavailable, _dimensions(), _fetch(), _normalize() (+16 more)

### Community 85 - "federation.py"
Cohesion: 0.16
Nodes (16): AggregateResult, Aggregator, FedAvg, models_in_use(), ModelUpdate, ModelVersion, datetime, Protocol (+8 more)

### Community 86 - "test_brazil_adapter.py"
Cohesion: 0.13
Nodes (19): auth(), _keys(), asyncio, fixture, parametrize, Brazil adapter (IBGE PAM via SIDRA) and India/Brazil cross-country schema…, Patches the HTTP call to SIDRA only; everything after it is the real adapter…, reset() (+11 more)

### Community 87 - "interop_v1.py"
Cohesion: 0.18
Nodes (19): AdvisoryV1, DiseaseV1, FarmerRefV1, FarmV1, GridCellV1, OutcomeSummaryV1, PageV1, PlotV1 (+11 more)

### Community 88 - "validate_polygon"
Cohesion: 0.16
Nodes (18): area_ha(), _cross(), _number(), PlotError, _project(), ValueError, Field plots: an optional polygon the farmer draws around their field. A plot is…, Invalid plot geometry. `code` is safe to show to the client. (+10 more)

### Community 89 - "test_interoperability.py"
Cohesion: 0.16
Nodes (12): auth(), asyncio, fixture, parametrize, BRICS interoperability: schema v1.0, country adapters, privacy-aware signal API…, secret(), test_another_country_plugs_in_through_an_adapter(), test_observations_are_aggregated_to_grid_cells_with_small_groups_suppressed() (+4 more)

### Community 90 - "CountryAdapter"
Cohesion: 0.17
Nodes (10): A risk or early-warning signal. `source_region` is where the evidence is;…, RiskSignalV1, CountryAdapter, get(), date, Protocol, Country adapter contract. national data sources -> CountryAdapter -> schema…, Sources, coverage and limitations, for partners deciding how to use the signals. (+2 more)

### Community 91 - "api.test.mjs"
Cohesion: 0.14
Nodes (6): resetReachabilityProbe(), realNavigator, events, store, ref_node_assert, ref_node_test

### Community 92 - "earth_engine_service.py"
Cohesion: 0.11
Nodes (16): classify_error(), CredentialError, parse_service_account_key(), ValueError, Sentinel-2 crop health (NDVI) from Google Earth Engine. Dataset:…, Map an Earth Engine / google-auth exception to a failure code. Order matters:…, The configured key cannot be used. `code` is safe to show to operators., Accept the service-account JSON as-is or base64-encoded (easier to paste into… (+8 more)

### Community 93 - "ServiceUnavailableException"
Cohesion: 0.21
Nodes (8): Exception, ServiceUnavailableException, Compact current-conditions dict used as AI context and by the legacy…, WeatherService, test_intelligence_endpoint_when_weather_is_down(), test_regenerative_endpoint_reports_inputs(), test_all_providers_failing_is_503_not_wrong_voice(), test_gemini_failure_falls_back_to_native_gtts_voice()

### Community 94 - "test_earth_engine.py"
Cohesion: 0.10
Nodes (41): _pass(), _point_result(), _point_with(), parametrize, Sentinel-2 / Earth Engine: credential handling, honest status reporting and…, _ready_service(), _service(), _sources_and_ready() (+33 more)

### Community 95 - "FarmContext"
Cohesion: 0.28
Nodes (12): DataQuality, FarmIntelligence, FarmContext, assemble(), _crop_health_summary(), data_quality(), farm_intelligence(), date (+4 more)

### Community 96 - "generate_e2e_fixtures.py"
Cohesion: 0.17
Nodes (9): alembic_config, ee_result(), intel(), Regenerates the Milestone 11 E2E fixtures (field crop health, field…, migrated_test_db(), fixture, Test database isolation. Tests delete rows, so they never touch the database in…, shutil (+1 more)

### Community 97 - "BrazilAdapter"
Cohesion: 0.19
Nodes (6): CropV1, The country has no legitimate source for this category., UnsupportedCategory, BrazilAdapter, test_brazil_adapter_implements_the_same_contract_without_changing_it(), test_unsupported_categories_raise_instead_of_returning_placeholders()

### Community 98 - "speech.ts"
Cohesion: 0.23
Nodes (13): getSpeechVoices(), synthesizeSpeech(), transcribeAudio(), audioPlayer(), cleanup(), BlockedError, devicePlayer(), IDLE (+5 more)

### Community 99 - "test_evaluation.py"
Cohesion: 0.30
Nodes (13): seed(), _admin(), asyncio, Evaluation layer: diagnosis feedback by model confidence, advisory follow-…, n farms, each with one diagnosis and its recommendation; `wrong` of them report…, seed_advisories(), seed_diagnoses(), test_advisory_follow_through_partial_and_outcomes() (+5 more)

### Community 100 - "gemini_service.py"
Cohesion: 0.14
Nodes (16): GeminiService, All Gemini calls. Model output is treated as untrusted: * every call is async…, Models sometimes answer in the question's language instead of the requested…, Natural speech for `text`. Returns (16-bit mono PCM, sample rate)., untrusted(), is_in_language(), language_name(), language_rule() (+8 more)

### Community 101 - "test_farm_twin.py"
Cohesion: 0.44
Nodes (12): api(), create(), asyncio, Farm digital twin: creation, token access, snapshots, recommendation feedback…, sources(), test_create_farm_stores_no_personal_data_and_coarse_location(), test_diagnosis_linked_to_farm_supports_diagnosis_feedback_and_feeds_the_engine(), test_farm_requires_its_own_token() (+4 more)

### Community 102 - "Farm Intelligence Engine"
Cohesion: 0.21
Nodes (12): Derived signals, Farm Intelligence Engine, Field outline (plots), Inputs and their status, Limitations, Policymaker early warning, Regenerative plan and crop options, Risk level vs evidence confidence (engine 1.1) (+4 more)

### Community 103 - "weather_service.py"
Cohesion: 0.13
Nodes (24): Regions configured in this deployment, and forecast risks at their reference…, _at(), parse_conditions(), Weather conditions from the Open-Meteo forecast API. Open-Meteo "current"…, weather_condition(), open_meteo_payload(), isolate(), fixture (+16 more)

### Community 104 - "journeys.spec.ts"
Cohesion: 0.24
Nodes (6): leaf, notImage, fixtureData, withFarmProfile(), MOCK_API, @playwright/test

### Community 105 - "LanguageCode"
Cohesion: 0.26
Nodes (9): AdvisoryInput, createSpeechController(), play(), playDevice(), playServer(), stop(), SpeechDeps, LanguageCode (+1 more)

### Community 106 - "Sentinel-2 / Sentinel-1 field signals via Google Earth Engine"
Cohesion: 0.17
Nodes (11): Error codes, Field outline, pixels and mixed land (data quality), History series, Limits, One-time setup, Same-season baseline (temporal context), Sentinel-1 radar (cloud-resilient), Sentinel-2 / Sentinel-1 field signals via Google Earth Engine (+3 more)

### Community 107 - "next.config.ts"
Cohesion: 0.50
Nodes (3): apiOrigin, nextConfig, securityHeaders

### Community 108 - "geo.ts"
Cohesion: 0.32
Nodes (11): Editor(), areaHa(), closeRing(), cross(), MAX_AREA_HA, MAX_VERTICES, MIN_AREA_HA, outlineProblem (+3 more)

### Community 109 - "test_disease_reference.py"
Cohesion: 0.22
Nodes (3): Settings, test_model_configuration_override(), BaseSettings

### Community 110 - "i18n.test.mjs"
Cohesion: 0.28
Nodes (4): ZERO, en, ref_node_child_process, ref_node_fs

### Community 111 - "EscalationSink"
Cohesion: 0.25
Nodes (6): EscalationSink, NotConnectedSink, Protocol, No extension system is integrated yet: the case is returned to the farmer to…, Where a case goes. A KVK or state extension system implements `submit` and…, Contextual diagnosis, safety tiers and escalation

### Community 112 - "_grade"
Cohesion: 0.29
Nodes (8): _forecast_reliability(), _grade(), _lead_days(), _outbreak_role(), Date, Sets the evidence's independence group, reliability and role…, A cluster raises the risk only when it is within the clustering radius and…, _satellite_quality()

### Community 115 - "crop_code"
Cohesion: 0.40
Nodes (5): crop_code(), Brazil adapter (`backend/services/interop/brazil.py`), BRICS interoperability, How another BRICS country integrates, India vs Brazil (`GET /api/interoperability/compare?crop=soybean`)

### Community 118 - "Farm digital twin and the action → outcome loop"
Cohesion: 0.67
Nodes (3): Evaluation (`GET /api/dashboard/evaluation`, `GET /api/dashboard/evaluation/records`), Farm digital twin and the action → outcome loop, Measurement (`GET /api/dashboard/feedback-metrics`)

## Knowledge Gaps
- **253 isolated node(s):** `builds`, `routes`, `leaf`, `notImage`, `API` (+248 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 733 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `unavailable()` connect `Farm Intelligence Engine` to `journeys.spec.ts`, `mock-api.ts`, `Sentinel-2 / Sentinel-1 field signals via Google Earth Engine`?**
  _High betweenness centrality (0.359) - this node is a cross-community bridge._
- **Why does `@playwright/test` connect `journeys.spec.ts` to `mock-api.ts`, `package.json`, `screenshots.spec.ts`?**
  _High betweenness centrality (0.349) - this node is a cross-community bridge._
- **Why does `area_ha()` connect `validate_polygon` to `Sentinel-2 / Sentinel-1 field signals via Google Earth Engine`, `test_plots.py`, `Farm Intelligence Engine`?**
  _High betweenness centrality (0.251) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `EarthEngineService` (e.g. with `ee_result()` and `intel()`) actually correct?**
  _`EarthEngineService` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `ServiceUnavailableException` (e.g. with `install_error_handlers()` and `_weather()`) actually correct?**
  _`ServiceUnavailableException` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `builds`, `routes`, `leaf` to the rest of the system?**
  _253 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `i18n.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.08974358974358974 - nodes in this community are weakly interconnected._
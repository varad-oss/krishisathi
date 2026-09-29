# Graph Report - krishisathi  (2026-09-29)

## Corpus Check
- 156 files · ~107,161 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 6, .example 2, .ini 1)

## Summary
- 1178 nodes · 2694 edges · 95 communities (62 shown, 33 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 58 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `72837a03`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- i18n.tsx
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
- test_intelligence.py
- api.test.mjs
- validate_plantvillage.py
- mock-api.ts
- .save_diagnosis
- speech.ts
- diagnose/page.tsx
- test_p02_regression.py
- package.json
- gemini_service.py
- compilerOptions
- dependencies
- env.py
- Conversation.tsx
- main.py
- persistence_service.py
- eslint.config.mjs
- ApiError
- cn
- kvk.py
- test_p03_outbreaks.py
- dashboard.py
- weather_service.py
- request
- devDependencies
- speech-core.ts
- test_disease_reference.py
- get
- manifest.json
- scripts
- EarthEngineService
- synthesize
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
- Header.tsx
- transcribe.md
- logging
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
- typing
- RequestContextMiddleware
- _decode_limited
- ._bound
- voice_plan
- Player
- get_weather_risk
- weather.py
- test_concurrent_requests_share_one_upstream_call
- get_crop_health
- get_ee_status
- list_sources
- list_states
- reset

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
- `get_nearest_kvk()` --uses--> `ApiError`  [INFERRED]
  backend/routers/kvk.py → backend/core/errors.py

## Import Cycles
- None detected.

## Communities (95 total, 33 thin omitted)

### Community 0 - "i18n.tsx"
Cohesion: 0.11
Nodes (23): cache, I18nContext, I18nValue, interpolate(), isLanguage(), LanguageProvider(), loaders, loadMessages() (+15 more)

### Community 1 - "test_security.py"
Cohesion: 0.07
Nodes (27): ai_down(), create_token(), err(), image_payload(), MockRedis, fixture, Regression: without Redis the limiter used to be silently disabled., Regression: allow_origins used to include '*' together with credentials. (+19 more)

### Community 2 - "test_failure_states.py"
Cohesion: 0.07
Nodes (40): Server-side image validation (never trust the client's Content-Type)., ai_diagnosis(), jpeg_bytes(), Shared test fixtures/data (imported by test modules; pytest puts this directory…, Server errors must reach the browser as errors, not as CORS failures that look…, post(), fixture, parametrize (+32 more)

### Community 4 - "routers/advisory.py"
Cohesion: 0.20
Nodes (22): AdvisoryRequest, AdvisoryResponse, DataSourceUse, FollowUpRequest, BaseModel, TranscribeRequest, TtsRequest, VoiceAdvisoryRequest (+14 more)

### Community 5 - "layout.tsx"
Cohesion: 0.08
Nodes (27): frontend_src_app_globals, beng, body, deva, display, gujr, guru, knda (+19 more)

### Community 6 - "ServiceUnavailableException"
Cohesion: 0.06
Nodes (28): ServiceUnavailableException, GeminiService, Models sometimes answer in the question's language instead of the requested…, Natural speech for `text`. Returns (16-bit mono PCM, sample rate)., untrusted(), is_in_language(), language_name(), language_rule() (+20 more)

### Community 7 - "insight-text.ts"
Cohesion: 0.16
Nodes (14): AlertView, Fmt, insightView(), OUTBREAK_SEVERITY, outbreakView(), SEVERITY_RANK, T, whenLabel() (+6 more)

### Community 8 - "diagnose.py"
Cohesion: 0.17
Nodes (21): get_idempotency_result(), set_idempotency_result(), AIDiagnosis, DiagnosisRequest, DiagnosisResponse, DiseaseReference, BaseModel, Shape the vision model must return. Anything else is rejected as an invalid AI… (+13 more)

### Community 9 - "api.ts"
Cohesion: 0.08
Nodes (35): AI_TIMEOUT_MS, API_BASE, ApiErrorCode, apiMisconfigured(), apiReachable(), classifyNetworkFailure(), RequestOptions, SpeechAudio (+27 more)

### Community 10 - "test_kvk.py"
Cohesion: 0.16
Nodes (10): haversine_km(), KvkService, Great-circle distance in kilometres (spherical Earth, R = 6371 km)., KVK for the district nearest to (lat, lng), or None when no listed district is…, KVK lookup: never report a distance to a district reference point as a distance…, test_empty_list_returns_none(), test_haversine_known_distance(), test_haversine_zero_and_symmetry() (+2 more)

### Community 11 - "errors.py"
Cohesion: 0.17
Nodes (15): error_body(), _from_detail(), install_error_handlers(), _api_error(), _http_error(), _service_unavailable(), _validation_error(), FastAPI (+7 more)

### Community 12 - "useI18n"
Cohesion: 0.20
Nodes (17): ErrorPage(), NotFound(), Bars(), CropHealthPanel(), KpiRow(), LimitationsPanel(), OutbreaksPanel(), PublishForm() (+9 more)

### Community 13 - "test_intelligence.py"
Cohesion: 0.05
Nodes (59): get_conditions(), get_crop_health(), get_regenerative(), get_soil(), Farmer-facing intelligence for one location. Each endpoint degrades…, Current conditions (model estimate), 7-day forecast and rule-based agro…, evaluate(), _insight() (+51 more)

### Community 14 - "api.test.mjs"
Cohesion: 0.14
Nodes (8): ZERO, resetReachabilityProbe(), realNavigator, en, ref_node_assert, ref_node_child_process, ref_node_fs, ref_node_test

### Community 15 - "validate_plantvillage.py"
Cohesion: 0.21
Nodes (11): AsyncClient, download_image(), fetch_image_list(), run_validation_suite(), asyncio, Prove that hard-coded crop-health values are not returned., test_crop_health_unavailable(), httpx (+3 more)

### Community 16 - "mock-api.ts"
Cohesion: 0.14
Nodes (19): frontend_e2e_fixtures_api, leaf, notImage, API, fixtureData, Fixtures, fresh(), json() (+11 more)

### Community 17 - ".save_diagnosis"
Cohesion: 0.14
Nodes (9): _haversine(), normalize_level(), outbreak_eligible(), _public_coord(), Outbreak clusters with coordinates rounded to ~11 km. Stale clusters are…, Aggregated counts from stored records only. No external or estimated figures., Maps legacy 'Medium'/'High' values and new levels onto low | moderate | high., Only confident, located disease detections may contribute to outbreak clusters. (+1 more)

### Community 18 - "speech.ts"
Cohesion: 0.21
Nodes (15): Conversation(), getSpeechVoices(), synthesizeSpeech(), transcribeAudio(), audioPlayer(), cleanup(), BlockedError, devicePlayer() (+7 more)

### Community 19 - "diagnose/page.tsx"
Cohesion: 0.19
Nodes (22): AdvisorPage(), DiagnosePage(), Phase, ChatMessage, FarmProfileForm(), useLocationLabel(), buttonClass, Note() (+14 more)

### Community 20 - "test_p02_regression.py"
Cohesion: 0.07
Nodes (44): get_current_user(), Principal, BaseModel, Validates an HS256 JWT signed with settings.JWT_SECRET. Fails closed: when no…, require_system_role(), AggregatedStateReport, BaseModel, Interoperability data models for cross-state agricultural data sharing. These… (+36 more)

### Community 21 - "package.json"
Cohesion: 0.13
Nodes (14): name, private, version, clsx, react-dom, tailwind-merge, tailwindcss, @tailwindcss/postcss (+6 more)

### Community 22 - "gemini_service.py"
Cohesion: 0.16
Nodes (12): asyncio, Public description of every data source the platform uses and whether it is…, All Gemini calls. Model output is treated as untrusted: * every call is async…, Text-to-speech with a native-language voice for every supported language.…, collections, ee, google, google_genai (+4 more)

### Community 23 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 24 - "dependencies"
Cohesion: 0.15
Nodes (13): dependencies, clsx, leaflet, lucide-react, next, react, react-dom, react-leaflet (+5 more)

### Community 25 - "env.py"
Cohesion: 0.18
Nodes (10): do_run_migrations(), run_async_migrations(), run_migrations_online(), Connection, logging_config, sqlalchemy_engine, sqlalchemy_ext_asyncio, sqlalchemy_orm (+2 more)

### Community 26 - "Conversation.tsx"
Cohesion: 0.20
Nodes (11): FEATURES, Home(), WorkflowDiagram(), AssistantMessage(), SourceList(), ReadAloud(), SUPPORTED_LANGUAGES, useSpeech() (+3 more)

### Community 27 - "main.py"
Cohesion: 0.18
Nodes (12): ensure_tables(), health_live(), health_ready(), lazy_db_init(), lifespan(), FastAPI, Creates missing tables once per process. Serverless deployments (Vercel) may…, root() (+4 more)

### Community 28 - "persistence_service.py"
Cohesion: 0.27
Nodes (11): AdvisoryRecord, DiagnosisRecord, FederationSignalRecord, OutbreakRecord, PersistenceService, asyncio, test_macro_grid_collision(), asyncio (+3 more)

### Community 29 - "eslint.config.mjs"
Cohesion: 0.50
Nodes (3): eslintConfig, eslint, eslint-config-next

### Community 30 - "ApiError"
Cohesion: 0.29
Nodes (10): ApiError, HTTPException carrying an explicit machine-readable code., ai_rate_limit(), _client_ip(), _local_incr(), rate_limit(), tts_rate_limit(), HTTPException (+2 more)

### Community 31 - "cn"
Cohesion: 0.12
Nodes (35): AboutPage(), SECTIONS, DiagnosisResult(), StepList(), CropHealthCard(), KvkCard(), SOIL_REASON, SoilProperties() (+27 more)

### Community 33 - "test_p03_outbreaks.py"
Cohesion: 0.21
Nodes (15): clear_db(), asyncio, fixture, parametrize, test_diagnoses_without_location_are_recorded_but_not_clustered(), test_ineligible_diagnoses_never_form_outbreaks(), test_insufficient_observations_no_outbreak(), test_outbreak_coordinates_are_coarsened_for_privacy() (+7 more)

### Community 34 - "dashboard.py"
Cohesion: 0.23
Nodes (12): cache_get(), cache_set(), Optional shared JSON cache on Redis. Every call degrades to a no-op when Redis…, get_dashboard_report(), get_stats(), _failure(), _fetch(), Soil properties from ISRIC SoilGrids 2.0 (modelled, 250 m resolution).… (+4 more)

### Community 35 - "weather_service.py"
Cohesion: 0.31
Nodes (7): build_context(), _outbreaks(), Builds the DATA blocks that ground advisory answers. Sources are fetched…, _soil_text(), _weather(), _weather_text(), Weather conditions from the Open-Meteo forecast API. Open-Meteo "current"…

### Community 36 - "request"
Cohesion: 0.24
Nodes (16): PolicyDashboardPage(), FarmPage(), getCropHealth(), getDashboardReport(), getDashboardStats(), getExchangeSignals(), getFarmConditions(), getNearestKvk() (+8 more)

### Community 37 - "devDependencies"
Cohesion: 0.18
Nodes (11): devDependencies, eslint, eslint-config-next, @playwright/test, tailwindcss, @tailwindcss/postcss, @types/leaflet, @types/node (+3 more)

### Community 38 - "speech-core.ts"
Cohesion: 0.11
Nodes (21): AdvisoryInput, BCP47, cleanForSpeech(), createSpeechController(), play(), playDevice(), playServer(), stop() (+13 more)

### Community 39 - "test_disease_reference.py"
Cohesion: 0.22
Nodes (3): Settings, test_model_configuration_override(), BaseSettings

### Community 40 - "get"
Cohesion: 0.28
Nodes (15): get_dashboard_outbreaks(), get(), SoilGrids integration: each failure mode is reported with its own reason, never…, resp(), test_endpoint_exposes_reason(), test_failures_are_not_cached(), test_malformed_response_reason(), test_network_error_reason() (+7 more)

### Community 41 - "manifest.json"
Cohesion: 0.22
Nodes (8): background_color, description, display, icons, name, short_name, start_url, theme_color

### Community 42 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, start, test, test:e2e, typecheck

### Community 43 - "EarthEngineService"
Cohesion: 0.33
Nodes (3): EarthEngineService, Mean of the median Sentinel-2 NDVI over a geometry and date window., date

### Community 44 - "synthesize"
Cohesion: 0.17
Nodes (13): _audio_response(), Speech audio in the requested language. X-TTS-Provider says which voice was…, Deprecated: long non-Latin text makes very long URLs. Use POST…, text_to_speech(), text_to_speech_get(), pcm_to_wav(), Drops Markdown symbols that voices would otherwise read out ("asterisk",…, Returns (audio bytes, MIME type, provider id). (+5 more)

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

### Community 55 - "Header.tsx"
Cohesion: 0.28
Nodes (8): Footer(), Header(), LanguageSelect(), Logo(), MobileNav(), isActive(), NAV_ITEMS, next

### Community 56 - "transcribe.md"
Cohesion: 0.40
Nodes (4): graphify reference: transcribe video and audio, print progress to stdout, which would otherwise corrupt the JSON file (#1392)., Step 2.5 - Transcribe video / audio files (only if video files detected), Write the JSON from Python (NOT a shell '>' redirect): transcribe_all/Whisper

### Community 57 - "logging"
Cohesion: 0.24
Nodes (8): ASGI middleware: request IDs, access logging, security headers, last-resort…, Krishi Vigyan Kendra lookup from a small static reference list. The bundled…, datetime, google_cloud, json, logging, os, time

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

### Community 79 - "typing"
Cohesion: 0.31
Nodes (9): DiseaseAlert, OutbreakReport, BaseModel, get_alerts(), get_outbreaks(), get_personalized_alerts(), _haversine(), math (+1 more)

### Community 85 - "voice_plan"
Cohesion: 0.40
Nodes (5): Which server voice each language gets, so clients can prefer a better on-device…, tts_voices(), gemini_languages(), Server voice per language: "gemini" (natural) or "gtts" (native but plainer)., voice_plan()

## Knowledge Gaps
- **204 isolated node(s):** `builds`, `routes`, `leaf`, `notImage`, `API` (+199 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 452 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **33 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ServiceUnavailableException` connect `ServiceUnavailableException` to `test_security.py`, `dashboard.py`, `weather_service.py`, `test_failure_states.py`, `diagnose.py`, `errors.py`, `synthesize`, `test_intelligence.py`, `gemini_service.py`, `get_weather_risk`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Why does `RegionalAgriSignal` connect `test_p02_regression.py` to `persistence_service.py`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Why does `react` connect `diagnose/page.tsx` to `i18n.tsx`, `layout.tsx`, `useI18n`, `speech.ts`, `package.json`, `Conversation.tsx`, `cn`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `ServiceUnavailableException` (e.g. with `install_error_handlers()` and `get_weather_risk()`) actually correct?**
  _`ServiceUnavailableException` has 13 INFERRED edges - model-reasoned connections that need verification._
- **What connects `builds`, `routes`, `leaf` to the rest of the system?**
  _204 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `i18n.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.1051693404634581 - nodes in this community are weakly interconnected._
- **Should `test_security.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0743321718931475 - nodes in this community are weakly interconnected._
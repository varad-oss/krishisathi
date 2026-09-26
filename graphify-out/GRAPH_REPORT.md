# Graph Report - krishisathi  (2026-09-26)

## Corpus Check
- 147 files · ~156,023 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 6, .example 2, .ini 1)

## Summary
- 1035 nodes · 2342 edges · 74 communities (55 shown, 19 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 55 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6a3c97a6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- OutbreakMap.tsx
- cn
- GeminiService
- package.json
- interop.py
- compilerOptions
- What You Must Do When Invoked
- main.py
- gemini_service.py
- dependencies
- README.md
- routers/advisory.py
- graphify reference: extra exports and benchmark
- KrishiSathi Engineering Rules
- manifest.json
- .log_diagnosis
- EarthEngineService
- diagnose.py
- graphify reference: query, path, explain
- typing
- errors.py
- graphify reference: add a URL and watch a folder
- vercel.json
- postcss.config.mjs
- graphify reference: commit hook and native CLAUDE.md integration
- advisory_context.py
- graphify reference: incremental update and cluster-only
- frontend/README.md
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- rules/graphify.md
- ponytail.md
- extraction-spec.md
- workflows/graphify.md
- frontend/AGENTS.md
- test_disease_reference.py
- diagnose/page.tsx
- devDependencies
- mock-api.ts
- get_weather_risk
- test_security.py
- types.ts
- test_failure_states.py
- scripts
- i18n.tsx
- eslint.config.mjs
- useI18n
- layout.tsx
- ApiError
- api.ts
- test_p02_regression.py
- .save_diagnosis
- test_intelligence.py
- test_advisory.py
- ServiceUnavailableException
- persistence_service.py
- farm.py
- test_p03_outbreaks.py
- env.py
- i18n.test.mjs
- rate_limit.py
- validate_plantvillage.py
- agro_rules.py
- KvkService
- next.config.ts
- TrendChart.tsx
- list_sources
- .get_soil
- binascii
- functools
- handler

## God Nodes (most connected - your core abstractions)
1. `useI18n()` - 63 edges
2. `cn()` - 37 edges
3. `ServiceUnavailableException` - 36 edges
4. `ApiError` - 22 edges
5. `post()` - 21 edges
6. `request()` - 20 edges
7. `MessageKey` - 18 edges
8. `ApiError` - 16 edges
9. `compilerOptions` - 16 edges
10. `ai_diagnosis()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `2. User flows traced` --references--> `test_crop_health_unavailable()`  [INFERRED]
  docs/AUDIT.md → backend/tests/test_dashboard_crop_health.py
- `7. Build and test status at HEAD` --references--> `test_crop_health_unavailable()`  [INFERRED]
  docs/AUDIT.md → backend/tests/test_dashboard_crop_health.py
- `9. What was done` --references--> `unavailable()`  [INFERRED]
  docs/AUDIT.md → frontend/e2e/mock-api.ts
- `3. Fallback / fabrication inventory` --references--> `get_crop_health()`  [EXTRACTED]
  docs/AUDIT.md → backend/routers/dashboard.py
- `test_weather_failure_raises_exception()` --uses--> `ServiceUnavailableException`  [INFERRED]
  backend/tests/test_failure_states.py → backend/models/exceptions.py

## Import Cycles
- None detected.

## Communities (74 total, 19 thin omitted)

### Community 0 - "OutbreakMap.tsx"
Cohesion: 0.33
Nodes (4): COLORS, OutbreakMap, leaflet, react-leaflet

### Community 1 - "cn"
Cohesion: 0.13
Nodes (29): FEATURES, Home(), WorkflowDiagram(), AssistantMessage(), Conversation(), SourceList(), DiagnosisResult(), StepList() (+21 more)

### Community 2 - "GeminiService"
Cohesion: 0.25
Nodes (4): GeminiService, untrusted(), language_name(), Supported UI/response languages (allow-list). Codes match the frontend.

### Community 3 - "package.json"
Cohesion: 0.12
Nodes (16): name, private, version, clsx, react-dom, react-markdown, remark-gfm, tailwind-merge (+8 more)

### Community 4 - "interop.py"
Cohesion: 0.16
Nodes (17): AggregatedStateReport, BaseModel, Interoperability data models for cross-state agricultural data sharing. These…, Strip any personally identifiable information before data flows from a state-…, Standard payload for cross-state agricultural data exchange. Any state system…, Per-state configuration that adapts KrishiSathi to local context. The same…, National-level aggregation of state signals — for the policymaker dashboard., RegionalAgriSignal (+9 more)

### Community 5 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 6 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 7 - "main.py"
Cohesion: 0.12
Nodes (17): RequestContextMiddleware, ensure_tables(), health_live(), health_ready(), lazy_db_init(), lifespan(), FastAPI, get (+9 more)

### Community 8 - "gemini_service.py"
Cohesion: 0.14
Nodes (16): asyncio, ASGI middleware: request IDs, access logging, security headers, last-resort…, Public description of every data source the platform uses and whether it is…, All Gemini calls. Model output is treated as untrusted: * every call is async…, Soil properties from ISRIC SoilGrids 2.0 (modelled, 250 m resolution).…, Weather conditions from the Open-Meteo forecast API. Open-Meteo "current"…, datetime, ee (+8 more)

### Community 9 - "dependencies"
Cohesion: 0.15
Nodes (13): dependencies, clsx, leaflet, lucide-react, next, react, react-dom, react-leaflet (+5 more)

### Community 10 - "README.md"
Cohesion: 0.22
Nodes (8): Architecture, Data sources, License, Limitations, Real data only, Running locally, Validation, What it does

### Community 11 - "routers/advisory.py"
Cohesion: 0.10
Nodes (29): AdvisoryRequest, AdvisoryResponse, DataSourceUse, _decode_limited(), FollowUpRequest, BaseModel, field_validator, TranscribeRequest (+21 more)

### Community 12 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 13 - "KrishiSathi Engineering Rules"
Cohesion: 0.29
Nodes (6): 1. Graph-First Development, 2. Ponytail Anti-Overengineering Rules, 3. Trust, Correctness, and Data Integrity, 4. Security & Privacy, 5. Engineering Quality, KrishiSathi Engineering Rules

### Community 14 - "manifest.json"
Cohesion: 0.22
Nodes (8): background_color, description, display, icons, name, short_name, start_url, theme_color

### Community 15 - ".log_diagnosis"
Cohesion: 0.33
Nodes (3): Any, BigQueryService, Logs a diagnosis to BigQuery using batch load jobs to comply with Sandbox…

### Community 16 - "EarthEngineService"
Cohesion: 0.33
Nodes (3): EarthEngineService, Mean of the median Sentinel-2 NDVI over a geometry and date window., date

### Community 17 - "diagnose.py"
Cohesion: 0.12
Nodes (25): get_idempotency_result(), set_idempotency_result(), AIDiagnosis, DiagnosisRequest, DiagnosisResponse, DiseaseReference, BaseModel, field_validator (+17 more)

### Community 18 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 19 - "typing"
Cohesion: 0.09
Nodes (10): alembic, DiseaseAlert, OutbreakReport, BaseModel, get_alerts(), get_outbreaks(), get_personalized_alerts(), _haversine() (+2 more)

### Community 20 - "errors.py"
Cohesion: 0.14
Nodes (17): error_body(), _from_detail(), install_error_handlers(), _api_error(), _http_error(), _service_unavailable(), _validation_error(), FastAPI (+9 more)

### Community 21 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 25 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 26 - "advisory_context.py"
Cohesion: 0.36
Nodes (7): build_context(), _haversine(), _outbreaks(), Builds the DATA blocks that ground advisory answers. Sources are fetched…, _soil_text(), _weather(), _weather_text()

### Community 27 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 28 - "frontend/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 36 - "test_disease_reference.py"
Cohesion: 0.14
Nodes (7): Settings, test_model_configuration_override(), BaseSettings, math, os, pytest, sys

### Community 37 - "diagnose/page.tsx"
Cohesion: 0.14
Nodes (30): AdvisorPage(), DiagnosePage(), Phase, ChatMessage, FarmProfileForm(), useLocationLabel(), Card(), Note() (+22 more)

### Community 39 - "devDependencies"
Cohesion: 0.18
Nodes (11): devDependencies, eslint, eslint-config-next, @playwright/test, tailwindcss, @tailwindcss/postcss, @types/leaflet, @types/node (+3 more)

### Community 40 - "mock-api.ts"
Cohesion: 0.08
Nodes (31): asyncio, Prove that hard-coded crop-health values are not returned., test_crop_health_unavailable(), 10. What remains, 1. Architecture map (as found), 2. User flows traced, 4. Security risks, 5. Reliability and performance risks (+23 more)

### Community 41 - "get_weather_risk"
Cohesion: 0.28
Nodes (8): _cache_get(), _cache_set(), get_dashboard_outbreaks(), get_dashboard_report(), get_stats(), get_weather_risk(), get, Rule-based forecast risks at one reference point per state (indicative, not…

### Community 42 - "test_security.py"
Cohesion: 0.07
Nodes (27): ai_down(), create_token(), err(), image_payload(), MockRedis, fixture, Regression: without Redis the limiter used to be silently disabled., Regression: allow_origins used to include '*' together with credentials. (+19 more)

### Community 43 - "types.ts"
Cohesion: 0.06
Nodes (49): SECTIONS, AlertView, Fmt, insightView(), OUTBREAK_SEVERITY, outbreakView(), SEVERITY_RANK, T (+41 more)

### Community 44 - "test_failure_states.py"
Cohesion: 0.08
Nodes (37): ai_diagnosis(), jpeg_bytes(), Shared test fixtures/data (imported by test modules; pytest puts this directory…, post(), fixture, parametrize, reset_limits(), test_confident_detection_includes_verified_reference() (+29 more)

### Community 45 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, lint, start, test, test:e2e, typecheck

### Community 46 - "i18n.tsx"
Cohesion: 0.10
Nodes (25): AdvisoryInput, cache, I18nContext, I18nValue, interpolate(), isLanguage(), LanguageProvider(), loaders (+17 more)

### Community 47 - "eslint.config.mjs"
Cohesion: 0.50
Nodes (3): eslintConfig, eslint, eslint-config-next

### Community 48 - "useI18n"
Cohesion: 0.14
Nodes (27): AboutPage(), ErrorPage(), NotFound(), Bars(), CropHealthPanel(), KpiRow(), LimitationsPanel(), OutbreaksPanel() (+19 more)

### Community 49 - "layout.tsx"
Cohesion: 0.21
Nodes (8): frontend_src_app_globals, inter, metadata, viewport, Providers(), Footer(), Logo(), next

### Community 50 - "ApiError"
Cohesion: 0.11
Nodes (24): ApiError, HTTPException carrying an explicit machine-readable code., get_current_user(), Principal, BaseModel, Validates an HS256 JWT signed with settings.JWT_SECRET. Fails closed: when no…, require_system_role(), get_ee_status() (+16 more)

### Community 51 - "api.ts"
Cohesion: 0.17
Nodes (26): PolicyDashboardPage(), FarmPage(), AI_TIMEOUT_MS, API_BASE, ApiErrorCode, diagnoseCrop(), getAdvisory(), getCropHealth() (+18 more)

### Community 52 - "test_p02_regression.py"
Cohesion: 0.24
Nodes (13): jwt_secret(), asyncio, fixture, _stats(), test_client_cannot_choose_signal_id(), test_dashboard_report_generated_from_real_stats(), test_dashboard_report_insufficient_data_skips_ai(), test_federation_broadcast_signal_round_trip() (+5 more)

### Community 53 - ".save_diagnosis"
Cohesion: 0.12
Nodes (12): get_crop_health(), Regional NDVI is not computed yet; say so rather than returning estimates., _haversine(), normalize_level(), outbreak_eligible(), _public_coord(), Outbreak clusters with coordinates rounded to ~11 km. Stale clusters are…, Aggregated counts from stored records only. No external or estimated figures. (+4 more)

### Community 54 - "test_intelligence.py"
Cohesion: 0.18
Nodes (21): parse_soilgrids(), rate_organic_carbon(), rate_ph(), Soil Health Card organic-carbon classes: <0.5 % low, 0.5–0.75 % medium, >0.75 %…, conditions(), ids(), Weather parsing, agro rules, soil parsing and regenerative recommendations., Regression: soil_moisture_0_to_7cm is not a forecast-API variable and broke… (+13 more)

### Community 55 - "test_advisory.py"
Cohesion: 0.17
Nodes (19): _at(), parse_conditions(), weather_condition(), open_meteo_payload(), isolate(), fixture, run(), test_advisory_degrades_when_weather_unavailable() (+11 more)

### Community 56 - "ServiceUnavailableException"
Cohesion: 0.31
Nodes (5): ServiceUnavailableException, Compact current-conditions dict used as AI context and by the legacy…, WeatherService, test_regenerative_endpoint_reports_inputs(), Exception

### Community 57 - "persistence_service.py"
Cohesion: 0.27
Nodes (12): AdvisoryRecord, DiagnosisRecord, FederationSignalRecord, OutbreakRecord, PersistenceService, asyncio, test_macro_grid_collision(), asyncio (+4 more)

### Community 59 - "farm.py"
Cohesion: 0.20
Nodes (13): get_conditions(), get_crop_health(), get_regenerative(), get_soil(), get, Farmer-facing intelligence for one location. Each endpoint degrades…, Current conditions (model estimate), 7-day forecast and rule-based agro…, crop_group() (+5 more)

### Community 60 - "test_p03_outbreaks.py"
Cohesion: 0.21
Nodes (15): clear_db(), asyncio, fixture, parametrize, test_diagnoses_without_location_are_recorded_but_not_clustered(), test_ineligible_diagnoses_never_form_outbreaks(), test_insufficient_observations_no_outbreak(), test_outbreak_coordinates_are_coarsened_for_privacy() (+7 more)

### Community 61 - "env.py"
Cohesion: 0.18
Nodes (10): do_run_migrations(), run_async_migrations(), run_migrations_online(), Connection, logging_config, sqlalchemy_engine, sqlalchemy_ext_asyncio, sqlalchemy_orm (+2 more)

### Community 62 - "i18n.test.mjs"
Cohesion: 0.22
Nodes (6): ZERO, en, ref_node_assert, ref_node_child_process, ref_node_fs, ref_node_test

### Community 63 - "rate_limit.py"
Cohesion: 0.50
Nodes (7): ai_rate_limit(), _client_ip(), _local_incr(), rate_limit(), tts_rate_limit(), redis_asyncio, Request

### Community 64 - "validate_plantvillage.py"
Cohesion: 0.43
Nodes (6): AsyncClient, download_image(), fetch_image_list(), run_validation_suite(), random, sklearn_metrics

### Community 65 - "agro_rules.py"
Cohesion: 0.60
Nodes (4): evaluate(), _insight(), _num(), Deterministic agro-meteorological rules. Each insight is derived only from…

### Community 67 - "next.config.ts"
Cohesion: 0.50
Nodes (3): apiOrigin, nextConfig, securityHeaders

## Knowledge Gaps
- **192 isolated node(s):** `builds`, `routes`, `leaf`, `notImage`, `API` (+187 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 394 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `KrishiSathi — Repository Audit (2026-09-26)` connect `mock-api.ts` to `.save_diagnosis`?**
  _High betweenness centrality (0.361) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `ServiceUnavailableException` (e.g. with `install_error_handlers()` and `get_weather_risk()`) actually correct?**
  _`ServiceUnavailableException` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `ApiError` (e.g. with `get_voice_advisory()` and `diagnose_multipart()`) actually correct?**
  _`ApiError` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `builds`, `routes`, `leaf` to the rest of the system?**
  _192 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `cn` be split into smaller, more focused modules?**
  _Cohesion score 0.13090418353576247 - nodes in this community are weakly interconnected._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._
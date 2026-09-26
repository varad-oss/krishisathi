# Graph Report - krishisathi  (2026-09-26)

## Corpus Check
- 129 files · ~65,646 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 6, .example 2, .ini 1)

## Summary
- 714 nodes · 1355 edges · 70 communities (41 shown, 29 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 50 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4feae0de`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- map/page.tsx
- chat/page.tsx
- ServiceUnavailableException
- package.json
- interop.py
- compilerOptions
- What You Must Do When Invoked
- main.py
- test_p01_regression.py
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
- persistence_service.py
- states.py
- graphify reference: add a URL and watch a folder
- vercel.json
- postcss.config.mjs
- graphify reference: commit hook and native CLAUDE.md integration
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
- test_translation.py
- devDependencies
- os
- dashboard.py
- test_security.py
- api.ts
- test_failure_states.py
- scripts
- re
- eslint.config.mjs
- dashboard/page.tsx
- Header.tsx
- FastAPI
- DashboardPage
- test_p02_regression.py
- strip_pii
- RegionalAgriSignal
- WeatherService

## God Nodes (most connected - your core abstractions)
1. `ServiceUnavailableException` - 36 edges
2. `compilerOptions` - 16 edges
3. `useLanguage()` - 15 edges
4. `t()` - 15 edges
5. `ChatPage()` - 14 edges
6. `DashboardPage()` - 14 edges
7. `RegionalAgriSignal` - 13 edges
8. `DiagnosisRecord` - 13 edges
9. `OutbreakRecord` - 13 edges
10. `DiagnosePage()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `test_weather_failure_raises_exception()` --uses--> `ServiceUnavailableException`  [INFERRED]
  backend/tests/test_failure_states.py → backend/models/exceptions.py
- `post_exchange_signal()` --uses--> `Principal`  [INFERRED]
  backend/routers/states.py → backend/core/security.py
- `get_advisory()` --uses--> `ServiceUnavailableException`  [INFERRED]
  backend/routers/advisory.py → backend/models/exceptions.py
- `get_followup_advisory()` --uses--> `ServiceUnavailableException`  [INFERRED]
  backend/routers/advisory.py → backend/models/exceptions.py
- `get_voice_advisory()` --uses--> `ServiceUnavailableException`  [INFERRED]
  backend/routers/advisory.py → backend/models/exceptions.py

## Import Cycles
- None detected.

## Communities (70 total, 29 thin omitted)

### Community 0 - "map/page.tsx"
Cohesion: 0.21
Nodes (17): MapComponent, MapPage(), loadData(), MapComponent(), MapContainer, Marker, Popup, TileLayer (+9 more)

### Community 1 - "chat/page.tsx"
Cohesion: 0.16
Nodes (25): ChatPage(), LocalAlert, Message, QUICK_ACTIONS, CROP_TYPES, DiagnosePage(), diagnoseCrop(), getFollowUpAdvisory() (+17 more)

### Community 2 - "ServiceUnavailableException"
Cohesion: 0.32
Nodes (6): ServiceUnavailableException, get_current_weather(), get_forecast(), get, GeminiService, Exception

### Community 3 - "package.json"
Cohesion: 0.11
Nodes (18): name, private, version, clsx, date-fns, leaflet, react-dom, recharts (+10 more)

### Community 4 - "interop.py"
Cohesion: 0.53
Nodes (5): Enum, str, Interoperability data models for cross-state agricultural data sharing. These…, SeverityLevel, SignalType

### Community 5 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 6 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 7 - "main.py"
Cohesion: 0.18
Nodes (13): add_request_id(), ensure_db_init(), health_check(), health_live(), health_ready(), get, Request, root() (+5 more)

### Community 8 - "test_p01_regression.py"
Cohesion: 0.22
Nodes (8): asyncio, test_agent_failure_returns_503(), test_non_english_diagnosis_schema_valid(), test_telemetry_failure_no_local_persistence(), asyncio, test_weather_raises_503_on_missing_fields(), ee, unittest_mock

### Community 9 - "dependencies"
Cohesion: 0.13
Nodes (15): dependencies, clsx, date-fns, leaflet, lucide-react, next, react, react-dom (+7 more)

### Community 10 - "README.md"
Cohesion: 0.13
Nodes (14): 1. Clone the Repository, 2. Backend Setup (FastAPI), 3. Frontend Setup (Next.js), Architecture, Challenges & What I'd Improve, Features, Knowledge Base & Provenance, License (+6 more)

### Community 11 - "routers/advisory.py"
Cohesion: 0.15
Nodes (22): AdvisoryRequest, AdvisoryResponse, BaseModel, field_validator, VoiceAdvisoryRequest, VoiceAdvisoryResponse, get_advisory(), get_audio_mime_type() (+14 more)

### Community 12 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 13 - "KrishiSathi Engineering Rules"
Cohesion: 0.29
Nodes (6): 1. Graph-First Development, 2. Ponytail Anti-Overengineering Rules, 3. Trust, Correctness, and Data Integrity, 4. Security & Privacy, 5. Engineering Quality, KrishiSathi Engineering Rules

### Community 14 - "manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 15 - ".log_diagnosis"
Cohesion: 0.33
Nodes (3): Any, BigQueryService, Logs a diagnosis to BigQuery using batch load jobs to comply with Sandbox…

### Community 17 - "diagnose.py"
Cohesion: 0.05
Nodes (48): AsyncClient, asyncio, get_idempotency_result(), set_idempotency_result(), ai_rate_limit(), Request, rate_limit(), DiagnosisRequest (+40 more)

### Community 18 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 19 - "persistence_service.py"
Cohesion: 0.05
Nodes (47): alembic, do_run_migrations(), run_async_migrations(), run_migrations_online(), DiseaseAlert, OutbreakReport, BaseModel, AdvisoryRecord (+39 more)

### Community 20 - "states.py"
Cohesion: 0.18
Nodes (14): AggregatedStateReport, BaseModel, Per-state configuration that adapts KrishiSathi to local context. The same…, National-level aggregation of state signals — for the policymaker dashboard., StateConfig, get_exchange_signals(), get_state_config(), list_states() (+6 more)

### Community 21 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 25 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 27 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 28 - "frontend/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 36 - "test_disease_reference.py"
Cohesion: 0.20
Nodes (4): Config, Settings, test_model_configuration_override(), BaseSettings

### Community 37 - "test_translation.py"
Cohesion: 0.29
Nodes (4): TranslationServiceUnavailable, TranslationService, test_translation_api_failure_becomes_503(), test_translation_failure_raises_exception()

### Community 39 - "devDependencies"
Cohesion: 0.20
Nodes (10): devDependencies, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, @types/leaflet, @types/node, @types/react (+2 more)

### Community 40 - "os"
Cohesion: 0.19
Nodes (6): asyncio, Prove that hard-coded crop-health values are not returned., test_crop_health_unavailable(), os, pytest, sys

### Community 41 - "dashboard.py"
Cohesion: 0.48
Nodes (6): get_crop_health(), get_dashboard_outbreaks(), get_dashboard_report(), get_recent_activity(), get_stats(), get

### Community 42 - "test_security.py"
Cohesion: 0.09
Nodes (13): create_token(), MockRedis, asyncio, fixture, setup_env(), test_admin_role_allowed(), test_debug_endpoint_truthful(), test_expired_token() (+5 more)

### Community 43 - "api.ts"
Cohesion: 0.20
Nodes (19): IS_DEMO_MODE, mockAdvisory, mockAlerts, mockCropHealth, mockDashboardStats, mockDiagnosis, mockOutbreaks, mockStates (+11 more)

### Community 44 - "test_failure_states.py"
Cohesion: 0.29
Nodes (5): mock_gemini_error(), mock_weather_error(), fixture, test_weather_failure_raises_exception(), fastapi_testclient

### Community 45 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 47 - "eslint.config.mjs"
Cohesion: 0.50
Nodes (3): eslintConfig, eslint, eslint-config-next

### Community 48 - "dashboard/page.tsx"
Cohesion: 0.19
Nodes (11): CrossStateSignal, Home(), SignalPublisher(), postExchangeSignal(), LanguageContext, LanguageContextType, useLanguage(), t() (+3 more)

### Community 49 - "Header.tsx"
Cohesion: 0.13
Nodes (10): nextConfig, frontend_src_app_globals, inter, metadata, Footer(), Header(), LanguageProvider(), SUPPORTED_LANGUAGES (+2 more)

### Community 50 - "FastAPI"
Cohesion: 0.17
Nodes (14): get_current_user(), Principal, BaseModel, Validates OIDC-compatible JWT token. Uses settings.JWT_SECRET (if provided) to…, require_system_role(), lifespan(), debug_db(), get_ee_status() (+6 more)

### Community 51 - "DashboardPage"
Cohesion: 0.29
Nodes (10): DashboardPage(), loadData(), ApiError, fetchWithFallback(), getAdvisory(), getDashboardReport(), getDashboardStats(), getExchangeSignals() (+2 more)

### Community 52 - "test_p02_regression.py"
Cohesion: 0.39
Nodes (7): asyncio, test_dashboard_report_correctness(), test_federation_broadcast_signal_round_trip(), test_federation_targeted_signal_round_trip(), test_report_endpoint_not_implemented(), test_zero_diagnosis_state(), patch

### Community 54 - "strip_pii"
Cohesion: 0.33
Nodes (6): Strip any personally identifiable information before data flows from a state-…, strip_pii(), post_exchange_signal(), post, Publish a new agricultural signal to the national federation network. Strips…, test_strip_pii()

### Community 55 - "RegionalAgriSignal"
Cohesion: 0.40
Nodes (4): Config, Standard payload for cross-state agricultural data exchange. Any state system…, RegionalAgriSignal, test_regional_agri_signal_creation()

## Knowledge Gaps
- **153 isolated node(s):** `Config`, `Config`, `builds`, `routes`, `eslintConfig` (+148 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 330 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ServiceUnavailableException` connect `ServiceUnavailableException` to `test_translation.py`, `test_p01_regression.py`, `dashboard.py`, `routers/advisory.py`, `test_failure_states.py`, `diagnose.py`, `WeatherService`, `.__init__`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Why does `PersistenceService` connect `persistence_service.py` to `.get_dashboard_stats`, `RegionalAgriSignal`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Why does `RegionalAgriSignal` connect `RegionalAgriSignal` to `interop.py`, `os`, `persistence_service.py`, `states.py`, `test_p02_regression.py`, `strip_pii`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `ServiceUnavailableException` (e.g. with `get_advisory()` and `get_followup_advisory()`) actually correct?**
  _`ServiceUnavailableException` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `Config`, `builds` to the rest of the system?**
  _153 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._
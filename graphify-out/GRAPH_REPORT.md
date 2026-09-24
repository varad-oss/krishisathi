# Graph Report - KrishiSathi  (2026-09-24)

## Corpus Check
- 77 files · ~57,040 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 10 file(s) not represented in the graph (top: (none) 5, .example 2, .jsonl 1)

## Summary
- 521 nodes · 966 edges · 49 communities (34 shown, 15 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 33 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `468ee3cf`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- api.ts
- chat/page.tsx
- ServiceUnavailableException
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
- BigQueryService
- EarthEngineService
- diagnose.py
- graphify reference: query, path, explain
- alerts.py
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
- test_weather_ee.py
- dashboard.py
- .process_advisory
- validate_plantvillage.py
- test_failure_states.py
- scripts
- KvkService
- eslint.config.mjs
- DiseaseReferenceService

## God Nodes (most connected - your core abstractions)
1. `ServiceUnavailableException` - 34 edges
2. `compilerOptions` - 16 edges
3. `ChatPage()` - 14 edges
4. `DashboardPage()` - 14 edges
5. `DiagnosePage()` - 13 edges
6. `useLanguage()` - 13 edges
7. `t()` - 13 edges
8. `cn()` - 13 edges
9. `What You Must Do When Invoked` - 12 edges
10. `MapPage()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `test_weather_failure_raises_exception()` --uses--> `ServiceUnavailableException`  [INFERRED]
  backend/tests/test_failure_states.py → backend/models/exceptions.py
- `get_advisory()` --uses--> `ServiceUnavailableException`  [INFERRED]
  backend/routers/advisory.py → backend/models/exceptions.py
- `get_followup_advisory()` --uses--> `ServiceUnavailableException`  [INFERRED]
  backend/routers/advisory.py → backend/models/exceptions.py
- `get_voice_advisory()` --uses--> `ServiceUnavailableException`  [INFERRED]
  backend/routers/advisory.py → backend/models/exceptions.py
- `transcribe_audio()` --uses--> `ServiceUnavailableException`  [INFERRED]
  backend/routers/advisory.py → backend/models/exceptions.py

## Import Cycles
- None detected.

## Communities (49 total, 15 thin omitted)

### Community 0 - "api.ts"
Cohesion: 0.10
Nodes (45): DashboardPage(), loadData(), MapComponent, MapPage(), loadData(), MapComponent(), MapContainer, Marker (+37 more)

### Community 1 - "chat/page.tsx"
Cohesion: 0.08
Nodes (43): nextConfig, ChatPage(), Message, QUICK_ACTIONS, CROP_TYPES, DiagnosePage(), frontend_src_app_globals, inter (+35 more)

### Community 2 - "ServiceUnavailableException"
Cohesion: 0.19
Nodes (7): ServiceUnavailableException, get_current_weather(), get_forecast(), get, GeminiService, WeatherService, Exception

### Community 3 - "package.json"
Cohesion: 0.11
Nodes (18): name, private, version, clsx, date-fns, leaflet, react-dom, recharts (+10 more)

### Community 4 - "interop.py"
Cohesion: 0.15
Nodes (18): Config, Enum, str, Interoperability data models for cross-state agricultural data sharing. These…, Strip any personally identifiable information before data flows from a state-…, Standard payload for cross-state agricultural data exchange. Any state system…, Per-state configuration that adapts KrishiSathi to local context. The same…, RegionalAgriSignal (+10 more)

### Community 5 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 6 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 7 - "main.py"
Cohesion: 0.11
Nodes (17): add_request_id(), health_check(), lifespan(), get, root(), get_ee_status(), get, Debug endpoint for hackathon judges to verify Earth Engine pipeline status. (+9 more)

### Community 8 - "gemini_service.py"
Cohesion: 0.24
Nodes (9): ee, google, google_cloud, google_genai, json, logging, os, pydantic_settings (+1 more)

### Community 9 - "dependencies"
Cohesion: 0.13
Nodes (15): dependencies, clsx, date-fns, leaflet, lucide-react, next, react, react-dom (+7 more)

### Community 10 - "README.md"
Cohesion: 0.15
Nodes (12): 1. Clone the Repository, 2. Backend Setup (FastAPI), 3. Frontend Setup (Next.js), Architecture, Challenges & What I'd Improve, Features, Knowledge Base & Provenance, License (+4 more)

### Community 11 - "routers/advisory.py"
Cohesion: 0.19
Nodes (20): AdvisoryRequest, AdvisoryResponse, BaseModel, VoiceAdvisoryRequest, VoiceAdvisoryResponse, get_advisory(), get_audio_mime_type(), get_followup_advisory() (+12 more)

### Community 12 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 13 - "KrishiSathi Engineering Rules"
Cohesion: 0.29
Nodes (6): 1. Graph-First Development, 2. Ponytail Anti-Overengineering Rules, 3. Trust, Correctness, and Data Integrity, 4. Security & Privacy, 5. Engineering Quality, KrishiSathi Engineering Rules

### Community 14 - "manifest.json"
Cohesion: 0.25
Nodes (7): background_color, display, icons, name, short_name, start_url, theme_color

### Community 15 - "BigQueryService"
Cohesion: 0.38
Nodes (4): Any, BigQueryService, Logs a diagnosis to BigQuery using batch load jobs to comply with Sandbox…, Fallback logging to local file when BigQuery Sandbox is not configured.

### Community 17 - "diagnose.py"
Cohesion: 0.19
Nodes (16): DiagnosisRequest, DiagnosisResponse, BaseModel, Enum, str, SeverityEnum, SpreadRiskEnum, TreatmentPlan (+8 more)

### Community 18 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 19 - "alerts.py"
Cohesion: 0.22
Nodes (13): DiseaseAlert, OutbreakReport, BaseModel, get_alerts(), get_outbreaks(), get_personalized_alerts(), _haversine(), get (+5 more)

### Community 20 - "states.py"
Cohesion: 0.21
Nodes (11): AggregatedStateReport, BaseModel, National-level aggregation of state signals — for the policymaker dashboard., get_exchange_signals(), get_state_config(), list_states(), get, List all supported Indian agricultural states. (+3 more)

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
Cohesion: 0.27
Nodes (4): TranslationServiceUnavailable, TranslationService, test_translation_api_failure_becomes_503(), test_translation_failure_raises_exception()

### Community 39 - "devDependencies"
Cohesion: 0.20
Nodes (10): devDependencies, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, @types/leaflet, @types/node, @types/react (+2 more)

### Community 40 - "test_weather_ee.py"
Cohesion: 0.25
Nodes (4): asyncio, test_weather_raises_503_on_missing_fields(), pytest, unittest_mock

### Community 41 - "dashboard.py"
Cohesion: 0.33
Nodes (8): get_crop_health(), get_dashboard_outbreaks(), get_dashboard_report(), get_recent_activity(), get_stats(), get, Recent farmer activity feed for the dashboard., random

### Community 42 - ".process_advisory"
Cohesion: 0.22
Nodes (7): AgentService, get_kvk_tool(), get_state_config_tool(), get_weather_tool(), Get current weather information for a specific location., Find the nearest Krishi Vigyan Kendra (KVK) to the given location coordinates., Get agricultural configuration and details for an Indian state given its…

### Community 43 - "validate_plantvillage.py"
Cohesion: 0.36
Nodes (7): AsyncClient, download_image(), fetch_image_list(), run_validation_suite(), httpx, sklearn_metrics, sys

### Community 44 - "test_failure_states.py"
Cohesion: 0.29
Nodes (5): mock_gemini_error(), mock_weather_error(), test_weather_failure_raises_exception(), fastapi_testclient, fixture

### Community 45 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 47 - "eslint.config.mjs"
Cohesion: 0.50
Nodes (3): eslintConfig, eslint, eslint-config-next

## Knowledge Gaps
- **149 isolated node(s):** `Config`, `Config`, `builds`, `routes`, `eslintConfig` (+144 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 240 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ServiceUnavailableException` connect `ServiceUnavailableException` to `test_translation.py`, `gemini_service.py`, `dashboard.py`, `.process_advisory`, `routers/advisory.py`, `test_failure_states.py`, `test_weather_ee.py`, `diagnose.py`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `dependencies` connect `dependencies` to `package.json`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Why does `lucide-react` connect `chat/page.tsx` to `api.ts`, `package.json`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `ServiceUnavailableException` (e.g. with `get_advisory()` and `get_followup_advisory()`) actually correct?**
  _`ServiceUnavailableException` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `Config`, `builds` to the rest of the system?**
  _149 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `api.ts` be split into smaller, more focused modules?**
  _Cohesion score 0.10437710437710437 - nodes in this community are weakly interconnected._
- **Should `chat/page.tsx` be split into smaller, more focused modules?**
  _Cohesion score 0.07924984875983061 - nodes in this community are weakly interconnected._
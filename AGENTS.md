# KrishiSathi Engineering Rules

## 1. Graph-First Development
- **Architecture-first**: Understand the problem, then query the Graphify knowledge graph to identify affected nodes/components. Trace dependencies and data flow before implementing changes.
- **Do not blindly create files**: Search the existing implementation for reusable code using the graph and identify the smallest safe change.
- **Re-query**: Query Graphify again when the architecture materially changes.

## 2. Ponytail Anti-Overengineering Rules
You are a lazy senior developer. Lazy means efficient, not careless. The best code is the code never written. Before writing any code, stop at the first rung that holds:
1. Does this need to be built at all? (YAGNI)
2. Does it already exist in this codebase? Reuse the helper, util, or pattern that's already here, don't re-write it.
3. Does the standard library already do this? Use it.
4. Does a native platform feature cover it? Use it.
5. Does an already-installed dependency solve it? Use it.
6. Can this be one line? Make it one line.
7. Only then: write the minimum code that works.

- **No abstractions without current need**: Avoid frameworks merely because they are popular. Don't introduce microservices or Kubernetes prematurely.
- **Preserve existing behavior**: Unless intentionally changing it. Replace working code only with evidence.

## 3. Trust, Correctness, and Data Integrity
- **Never fabricate data**: Do not silently convert service failures into synthetic “live” data.
- **Explicit provenance**: All external data (weather, satellite, etc.) must have explicit source and provenance.
- **Avoid silent mock UI fallbacks**: If a service fails, throw an explicit error or show an unavailable state rather than deceiving the user with perfect mock data.
- **Agricultural advisory safety**: Ensure model-generated explanations are distinct from verified source data. Grounding must be strictly tied to real datasets. Never fabricate treatments.

## 4. Security & Privacy
- Enforce strict privacy boundaries, data aggregation policies, and PII protection.
- Validate all inputs and handle secrets securely.
- Ensure cross-state data exchange anonymizes and strips PII.

## 5. Engineering Quality
- **Tests required**: Add regression tests for behavior changes.
- **Multilingual correctness**: Strictly adhere to non-Romanized localization (native Indic scripts and numeral formatting). Do not fallback to English in translated outputs unless intended.
- **Documentation**: Update documentation when the implementation changes.
- **Small, reviewable changes**: Implement narrow-scoped, independently mergeable PRs.

# BRICS interoperability

KrishiSathi does not build a central BRICS farmer database. Each country keeps its farm-level data in its own
deployment and publishes **aggregated, provenance-labelled signals** in a shared, versioned schema.

```
national data sources ─► CountryAdapter ─► schema v1.0 objects ─► /api/interoperability/*
(weather, surveillance,     (one per          (codes, provenance,       (pagination, partner auth,
 advisory records)           country)          privacy rules)            rate limits, events)
```

## Schema v1.0 (`backend/models/interop_v1.py`)

| Shape | Purpose | Served publicly |
|---|---|---|
| `CropV1` | stable `crop_code` (e.g. `pearl_millet`), English name, group, aliases | yes |
| `DiseaseV1` | `disease_code`, names, crop codes, literature references | yes |
| `ObservationV1` | one aggregated observation: type, geography, period, variable, value, unit, sample size, confidence | partners |
| `RiskSignalV1` | risk/early-warning signal: type, category, severity, `source_region`, optional `affected_region`, crops, disease, report count, period, confidence | partners |
| `AdvisoryV1`, `OutcomeSummaryV1` | advice issued and aggregated self-reported outcomes | defined, not yet published |
| `FarmV1`, `PlotV1`, `FarmerRefV1` | in-country exchange only (pseudonymous refs, no names or phone numbers) | never |

Conventions: ISO 3166-1 alpha-2 countries, ISO 3166-2 regions (`IN-MH`), grid cells as south-west corner +
size, `provenance.kind` from a closed list (observed, forecast, model_estimate, satellite_observation,
rule_based, ai_generated, ai_classified_reports, farmer_reported, official_statistic, curated_reference,
authenticated_submission). Unknown fields are rejected, so personal fields cannot be smuggled in.
`GET /api/interoperability/schemas` returns the JSON Schema of every shape.

## API (`backend/routers/interoperability.py`)

| Endpoint | Auth | Content (India adapter) |
|---|---|---|
| `GET /schemas`, `/adapters`, `/models` | public | schemas; adapter sources, coverage, privacy, limitations; model registry |
| `GET /crops`, `/diseases` | public | crop catalogue; curated ICAR disease reference |
| `GET /weather-signals` | partner | agro-rule evaluations of Open-Meteo forecasts at one reference point per state |
| `GET /agricultural-observations` | partner | counts of moderate/high-certainty AI photo detections per disease, crop and 0.5° cell |
| `GET /risk-signals` | partner | outbreak clusters (0.5° cell) and authenticated state federation signals |

All are under `/api/interoperability`, take `country` (default `IN`), `limit` (≤ 200), an opaque `cursor`
and, for dated data, `since` (at most 90 days back). Partner endpoints need a bearer JWT with role
`partner`, `system` or `admin`; without `JWT_SECRET` they fail closed (`AUTH_NOT_CONFIGURED`). Responses carry
a `privacy` block. Each call logs an `interoperability_signals_served` event.

**Privacy.** No farm ids, farmer data, exact coordinates, free text or submission metadata are published.
Geography is a 0.5° cell (~55 km) or a region; any group smaller than 3 reports is suppressed. Low-certainty
detections are never counted.

**Cross-border signals.** A `RiskSignalV1` names the region where the evidence is (`source_region`) and, only
if the publisher says so, an `affected_region`. It never claims that a pest or pathogen moved; responses say so.

## How another BRICS country integrates

1. Implement `CountryAdapter` (`backend/services/interop/adapter.py`): `country_code`, `privacy`,
   `describe()`, and async `crops()`, `diseases()`, `weather_signals()`, `observations(since)`,
   `risk_signals(since)`, each returning schema v1.0 objects built from that country's own sources.
2. Map its codes: its crops to `crop_code`s, its subdivisions to ISO 3166-2, its data kinds to `provenance.kind`.
3. Aggregate before returning (its own grid or regions, its own minimum group size in `privacy`).
4. Register it: `adapters.register(BrazilAdapter())`. The API then serves `?country=BR` with no other change;
   `tests/test_interoperability.py::test_another_country_plugs_in_through_an_adapter` demonstrates this.
5. Issue partner JWTs to the systems that should read its signals.

No non-Indian dataset ships with KrishiSathi: the second adapter must come from that country's real sources.

## Federated models (`backend/services/federation.py`)

`GET /api/interoperability/models` lists the models actually in use (Gemini for diagnosis and advice, an
external foundation model; the rule-based risk engine) and reports federation as **`not_running`**: no
country trains a model here. What exists is the contract for when one does:

- `ModelVersion` (id, version, kind, task, provider, federated, training basis, countries);
- `ModelUpdate` (model id, base version, country, number of examples, parameters, metrics; never raw data);
- `Aggregator` protocol with `FedAvg` (McMahan et al., 2017) as the reference: example-weighted mean, at
  least 2 countries, same base version and parameter shape.

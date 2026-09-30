# BRICS interoperability

KrishiSathi does not build a central BRICS farmer database. Two country adapters exist: **India**
(KrishiSathi's own aggregated data) and **Brazil** (IBGE official crop statistics), both publishing through
the same v1.0 schema. Each country keeps its farm-level data in its own
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
| `ObservationV1` | one aggregated observation: type (`disease_observation`, `weather_observation`, `soil_observation`, `crop_health_observation`, `production_statistic`), geography, period, variable, value, unit, sample size, confidence | partners |
| `RiskSignalV1` | risk/early-warning signal: type, category, severity, `source_region`, optional `affected_region`, crops, disease, report count, period, confidence | partners |
| `AdvisoryV1`, `OutcomeSummaryV1` | advice issued and aggregated self-reported outcomes | defined, not yet published |
| `FarmV1`, `PlotV1`, `FarmerRefV1` | in-country exchange only (pseudonymous refs, no names or phone numbers) | never |

Conventions: ISO 3166-1 alpha-2 countries, ISO 3166-2 regions (`IN-MH`), grid cells as south-west corner +
size, `provenance.kind` from a closed list (observed, forecast, model_estimate, satellite_observation,
rule_based, ai_generated, ai_classified_reports, farmer_reported, official_statistic, curated_reference,
authenticated_submission). Unknown fields are rejected, so personal fields cannot be smuggled in.
`GET /api/interoperability/schemas` returns the JSON Schema of every shape.

`production_statistic` was added for Brazil's official crop statistics. It is an additive change inside v1.0
(no field changed meaning); a consumer that validates against an older copy of the schema must refresh it.
Pages (`PageV1`) now carry `status`: `available`, or `unsupported` when the country has no real source for
the category (then `items` is empty by definition and `notes` says why).

## API (`backend/routers/interoperability.py`)

| Endpoint | Auth | Content (India adapter) |
|---|---|---|
| `GET /schemas`, `/adapters`, `/models` | public | schemas; adapter sources, categories, coverage, privacy, limitations; model registry |
| `GET /compare?crop=` | public | every registered country through the same contract (see below) |
| `GET /crops`, `/diseases` | public | crop catalogue; curated ICAR disease reference |
| `GET /weather-signals` | partner | agro-rule evaluations of Open-Meteo forecasts at one reference point per state |
| `GET /agricultural-observations` | partner | counts of moderate/high-certainty AI photo detections per disease, crop and 0.5° cell |
| `GET /risk-signals` | partner | outbreak clusters (0.5° cell) and authenticated state federation signals |

All are under `/api/interoperability`, take `country` (default `IN`), `limit` (≤ 200), an opaque `cursor`
and, for dated data, `since` (at most 90 days back). Partner endpoints need a bearer JWT with role
`partner`, `system` or `admin`; without `JWT_SECRET` they fail closed (`AUTH_NOT_CONFIGURED`). Responses carry
a `privacy` block. Each call logs an `interoperability_signals_served` event.

**Privacy.** No farm ids, farm tokens, farmer data, exact coordinates, field outlines (plot geometry), photos,
free text or submission metadata are published. Geography is a 0.5° cell (~55 km) or a region; any group
smaller than 3 reports is suppressed. Low-certainty detections are never counted. Field outlines live only in
`farm_plots`, are returned only to the farm-token holder, are not logged (Earth Engine errors for polygons log
the error type only) and are cached only under a hash; `tests/test_plots.py` checks that a saved outline never
appears in any public interoperability or dashboard response.

**Unsupported vs unavailable.** A category the country has no real source for is `status: "unsupported"`
(HTTP 200, empty). A real source that cannot be reached right now is HTTP 503 `SOURCE_UNAVAILABLE`. An empty
`available` page means the source answered and had nothing. No adapter fills any of these with placeholders.

**Cross-border signals.** A `RiskSignalV1` names the region where the evidence is (`source_region`) and, only
if the publisher says so, an `affected_region`. It never claims that a pest or pathogen moved; responses say so.

## How another BRICS country integrates

1. Implement `CountryAdapter` (`backend/services/interop/adapter.py`): `country_code`, `privacy`,
   `describe()`, and async `crops()`, `diseases()`, `weather_signals()`, `observations(since)`,
   `risk_signals(since)`, each returning schema v1.0 objects built from that country's own sources.
2. Map its codes: its crops to `crop_code`s, its subdivisions to ISO 3166-2, its data kinds to `provenance.kind`.
3. Aggregate before returning (its own grid or regions, its own minimum group size in `privacy`).
4. Register it: `adapters.register(...)`. The API then serves `?country=XX` with no other change;
   `tests/test_interoperability.py::test_another_country_plugs_in_through_an_adapter` demonstrates this.
5. Raise `UnsupportedCategory` for categories without a real source and `SourceUnavailable` when the source
   fails; declare `categories` and `publishes` in `describe()`.
6. Issue partner JWTs to the systems that should read its signals.

## Brazil adapter (`backend/services/interop/brazil.py`)

**Source used (the only one):** IBGE (Instituto Brasileiro de Geografia e Estatística), *Produção Agrícola
Municipal* (PAM), SIDRA table **5457** ("área plantada ou destinada à colheita, área colhida, quantidade
produzida, rendimento médio e valor da produção das lavouras temporárias e permanentes"), read from the public
SIDRA API: `https://apisidra.ibge.gov.br/values/t/5457/n3/all/v/216,214,112/p/last%201/c782/all?formato=json`
(states, harvested area / production / average yield, latest published year, all products). No key is needed.

**Why this source.** Official national statistics agency; public and keyless; a long-stable documented API
whose responses carry their own variable names and units; national coverage by state; structured JSON; public
official statistics that may be reused with attribution to IBGE. Sources considered:

| Source | Status | Reason |
|---|---|---|
| IBGE SIDRA, PAM table 5457 | **used** | as above |
| Embrapa AgroAPI **Agritec v2** (ZARC planting windows, climate-risk zoning, productivity) | identified, not integrated | requires AgroAPI registration (OAuth client credentials); its response semantics could not be verified from this deployment, and guessing field meanings would risk mislabelled risk signals |
| MAPA open-data portal (`dados.agricultura.gov.br`), ZARC tables | identified, not integrated | bulk tabular releases, not an API; a later import could feed risk signals |

**Mapping to v1.0.**

| IBGE | v1.0 |
|---|---|
| Unidade da Federação code (e.g. 51) | `geo.region_code` ISO 3166-2 (`BR-MT`), `basis: region` |
| Ano (e.g. 2024) | `period` 2024-01-01 → 2024-12-31 |
| Produto (e.g. "Soja (em grão)") | `crop_code` (`soybean`, same code as India where the crop is the same) and `subject` (the IBGE product name, unchanged) |
| Variável 216 / 214 / 112 | `variable` `harvested_area` / `production` / `yield` (a row whose Portuguese variable name does not match its code is dropped) |
| Unidade de Medida | `unit` `ha` / `t` / `kg/ha` (unknown units are dropped, not guessed) |
| cells `-`, `..`, `...`, `X` | omitted (zero, not applicable, not available, confidential); never turned into numbers |
| — | `observation_type: production_statistic`, `provenance.kind: official_statistic`, `source`, `url`, `method` (with the SIDRA variable), `retrieved_at`, `notes`; `confidence` is not assessed (null) |

The parser reads which column holds which dimension from SIDRA's own header row instead of assuming an order.
Mapped products: soybean, maize, rice, wheat, sorghum, cotton, sugarcane, potato, tomato, onion, groundnut,
common bean (dry), cassava and coffee (total only, so arabica and canephora are not double-counted). Other
PAM products are not published because no confident English crop code exists for them.

**Categories.** `crops` and `observations`: available. `diseases`, `weather_signals`, `risk_signals`:
`unsupported` (no Brazilian source is connected; nothing is simulated).

**Operation.** One HTTP request per day at most (24 h in-process cache; concurrent callers share one fetch;
failures are not cached), 20 s timeout. SIDRA unreachable → 503 `SOURCE_UNAVAILABLE`.

**Limitations.** Annual state totals with about a one-year lag, so they describe production, not current
conditions; `since` does not filter them (the latest published year is always returned, and the page says
so). They are not comparable with India's AI-classified disease reports: same contract, different meaning.
This development environment's network policy blocked `apisidra.ibge.gov.br`, so the live response was not
fetched here; the adapter is tested against the documented SIDRA JSON layout with test values, and the
query was checked against published SIDRA usage of table 5457 / classification C782. Run
`GET /api/interoperability/compare` on a deployment with internet access to see real IBGE data.

## India vs Brazil (`GET /api/interoperability/compare?crop=soybean`)

A developer view (also on the About page) that puts every registered adapter through the same contract:

| | India | Brazil |
|---|---|---|
| Crop | `soybean` (KrishiSathi crop list) | `soybean` (IBGE "Soja (em grão)") |
| Observation type | `disease_observation` (AI-classified photo detections) | `production_statistic` (harvested area, production, yield) |
| Risk type | `weather_risk`, `disease_cluster`, state signals | unsupported |
| Geography | 0.5° grid cell / state reference point | state (ISO 3166-2) |
| Period | requested window | calendar year (latest published) |
| Source kind | `ai_classified_reports`, `forecast` | `official_statistic` |
| Confidence | low / moderate | not assessed |
| Access | partners | public official statistics |

Samples are shown only for public categories, and every sample is a real adapter item validated against the
schema; partner-only categories show "partners only", and an unreachable source shows "unavailable" rather
than an example. The point is *different national sources → the same interoperability contract*, not that
the figures can be compared.

## Federated models (`backend/services/federation.py`)

`GET /api/interoperability/models` separates two lists:

* **`currently_running`** / `models`: what is actually deployed (Gemini for diagnosis and advice, an external
  foundation model; the rule-based risk engine). None is federated.
* **`federated_ready`**: interfaces that could take part in a future federation, each with a status:
  `model_update_contract` and `fedavg_aggregator` are `contract_only` (code and tests, nothing runs);
  `country_adapter` is `running` for data exchange only, not for training; `evaluation_contract` is
  `contract_only` (a shape a country could use to evaluate a shared model locally).

Federation itself is **`not_running`**: no country trains a model here, and no simulation is presented as
training. What exists is the contract for when one does:

- `ModelVersion` (id, version, kind, task, provider, federated, training basis, countries);
- `ModelUpdate` (model id, base version, country, number of examples, parameters, metrics; never raw data);
- `Aggregator` protocol with `FedAvg` (McMahan et al., 2017) as the reference: example-weighted mean, at
  least 2 countries, same base version and parameter shape.

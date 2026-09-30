# Farm Intelligence Engine

`GET /api/farm/intelligence?lat=&lng=&crop=&sowing_date=` answers one question: *what matters most for this
farm right now?* It fuses the sources KrishiSathi already uses into explainable risks and one prioritized
action. It is rule-based; no AI model is called and no score exists that the rules below do not explain.

```
Open-Meteo weather ─┐
SoilGrids soil ─────┤
Sentinel-2 NDVI ────┤   FarmContext   ─►  risk engine  ─►  risks (severity, confidence,
Crop + sowing date ─┤  (each signal        (rules)          drivers, evidence, rules, action)
Nearby reports ─────┤   has a status)                  ─►  top action ("What matters today")
Farm history ───────┘                                  ─►  data quality per source
```

Code: `services/farm_context.py` (context), `services/risk_engine.py` (rules), `services/intelligence_service.py`
(assembly, data quality, structured event), contract in `models/intelligence.py`.

## Inputs and their status

Every input is `available`, `unavailable`, `not_configured`, `no_data`, `not_provided` or `pending`.
Slow sources get a time budget (soil 12 s, satellite 8 s). When it runs out the input is `pending`: the
upstream query keeps running and fills its cache, so the next request has it. Nothing is estimated in place
of a missing input.

| Input | Source | Kind |
|---|---|---|
| Weather now + 7-day forecast, topsoil moisture 3–9 cm | Open-Meteo | model estimate / forecast |
| Sand, clay, organic carbon (0–15 cm) | ISRIC SoilGrids 2.0 | model estimate (not a field test) |
| NDVI, current and previous 30 days | Sentinel-2 L2A via Google Earth Engine | satellite observation |
| Crop stage | FAO-56 Table 11 stage lengths from the sowing date | rule-based estimate |
| Nearby disease clusters | KrishiSathi photo diagnoses | AI-classified reports, not lab-confirmed |
| Farm's own recent diagnoses | KrishiSathi farm record | AI-generated |

## Derived signals

**Crop stage** (`services/crop_stage.py`). Days since sowing are placed on the FAO-56 Table 11 stage lengths
(initial, development, mid-season, late season) for one cited table row per crop. The Indian rows (wheat,
maize) give *moderate* confidence, other regions *low*. Crops without a citable row (chickpea, pigeon pea,
mustard, finger millet) return `no_calendar`; past the typical season returns `beyond_season` with no stage.

**Topsoil water status** (`services/soil_water.py`). Field capacity and wilting point are estimated from
SoilGrids texture and organic matter with the Saxton & Rawls (2006) pedotransfer equations; Open-Meteo
moisture is expressed as the fraction of plant-available water. Below 0.5 (the FAO-56 default depletion
fraction) is *dry*, at or above field capacity is *wet*. Two models are stacked, so confidence is always
*low*.

## Risks

Weather thresholds come from `services/agro_rules.py` (IMD where IMD publishes one) and are not redefined.

| Risk | High | Moderate | Action |
|---|---|---|---|
| Waterlogging | IMD heavy rain (≥ 64.5 mm/day) in 3 days | rain expected (≥ 5 mm, ≥ 60 %) on *wet* topsoil | clear drainage / delay irrigation |
| Water stress | 7-day dry spell (rain < 2 mm, ET0 ≥ 25 mm) on *dry* topsoil | dry spell or dry topsoil, no rain expected | irrigate soon |
| Heat stress | IMD heat ≥ 45 °C, or ≥ 40 °C in the mid-season stage¹ | IMD ≥ 40 °C | protect from heat |
| Cold stress | IMD ≤ 2 °C | IMD ≤ 4 °C | protect from cold |
| Disease | two independent signals² | one signal² | scout the field |
| Spray window | — | wind ≥ 15 km/h now, or rain today/tomorrow | postpone spraying |
| Harvest weather | late season + heavy rain | late season + rain expected | protect harvest |
| Crop health | — | NDVI fell by ≥ 0.1 between 30-day windows³ | inspect the field |
| Pest | always `unavailable` (`no_pest_data_source`) | | |

1. Heat during flowering and grain/fruit set is most damaging (Hatfield & Prueger 2015); FAO-56 "mid-season" covers it.
2. Signals: humid-weather fungal rule, a nearby AI-classified disease cluster for the crop, the farm's own
   disease detection in the last 14 days.
3. A screening rule to prompt a field visit, not a validated crop-loss indicator.

Severity is `low`, `moderate`, `high` or `unavailable` (always with a `reason`). Confidence is qualitative.
Every moderate/high risk carries `drivers`, `evidence` (value, unit, date, basis, source) and `rules`
(threshold source and link).

## What matters today

Risks are ordered by severity, then whether there is something to do, then how soon, then a fixed damage
order (waterlogging, heat, cold, water stress, disease, harvest, crop health, spray, pest). The first
moderate/high risk with an action becomes the top action. If none, a low risk with an action (e.g. "rain is
expected, consider delaying irrigation") is shown; otherwise routine monitoring. If weather is unavailable
and nothing else is moderate or high, the top action is `unavailable` rather than a false all-clear.

The API returns ids and numbers only; the frontend renders them in the farmer's language.

## Limitations

- Stage lengths are typical values for one region and season; the farmer's variety may differ.
- Topsoil water is derived from two global models at 3–9 cm; it is not a field measurement.
- No pest surveillance data is connected, so pest risk is not assessed.
- The NDVI decline threshold is a screening rule; see `docs/EARTH_ENGINE.md` for the satellite method.

## Farm digital twin and the action → outcome loop

`POST /api/farms` registers a farm (location, optional crop, sowing date, area) and returns a `farm_id` and a
random `farm_token` once; only the token's SHA-256 is stored and every later call sends `X-Farm-Token`.
No name, phone or account is collected, and the location is kept to 3 decimals (~110 m).

| Endpoint | Purpose |
|---|---|
| `POST /api/farms` | register (rate-limited) |
| `GET /api/farms/{id}` | profile + history: snapshots, recommendations with feedback, photo diagnoses |
| `POST /api/farms/{id}` | update profile |
| `GET /api/farms/{id}/intelligence` | intelligence for the stored profile, using the farm's own recent diagnoses; records a snapshot (≤ 1/h unless the top action changes) and the recommended action (one per action per day) |
| `POST /api/farms/{id}/actions/{action_id}/feedback` | `followed`: yes / partial / no / not_applicable; `outcome`: improved / same / worse / diagnosis_wrong (diagnoses only) / not_sure |

Tables (`migrations/versions/b7d2e4f6a8c1_farm_digital_twin.py`): `farms`, `farm_snapshots`,
`advisory_actions` (recommendation + self-reported follow-through and outcome), and `diagnoses.farm_id`.

Follow-through and outcomes are what the farmer says happened. They are feedback signals, never evidence
that a recommendation caused an outcome, and the UI says so next to every question.

### Measurement (`GET /api/dashboard/feedback-metrics`)

Aggregates over 90 days: follow-through rate (yes + partly over applicable answers), outcome counts, and the
same by source (daily advice, photo check, soil practice), crop, 1° region cell and diagnosis certainty
(does the model's stated certainty match "diagnosis was wrong" reports?), plus repeat disease detections per
farm. Groups under 5 records are suppressed. Labelled `app_derived_feedback`: not official statistics.

## Contextual diagnosis, safety tiers and escalation

`POST /api/diagnose` (and `/base64`) still takes a photo, crop and location, and now also `sowing_date` and
`farm_id` + `X-Farm-Token`. A linked farm fills in the crop, location and sowing date the request leaves out,
and the result is stored on the farm (its disease detections then feed the farm's disease risk).

The model receives, as clearly labelled *supporting information, never proof*: current weather (model
estimate), the estimated crop stage, nearby AI-classified reports and, only if already cached, the Sentinel-2
change. It returns a **differential** (up to 3 causes with likelihood and reason, non-disease causes included);
malformed entries are dropped.

Rules the model cannot override (`services/diagnosis_policy.py`, thresholds in settings, never below *moderate*):

| Guidance | When | Effect |
|---|---|---|
| `supported` | disease detected, certainty ≥ `DIAGNOSIS_SUPPORTED_MIN_CERTAINTY` (high), verified reference, good photo | steps shown |
| `cautious` | disease detected otherwise | steps shown with "confirm before buying treatment"; expert review advised when severity is high |
| `escalate` | uncertain cause, low certainty or poor photo | "do not treat yet", KVK referral |
| `none` | healthy / not a plant | — |

Chemical options appear only with a verified ICAR reference entry *and* certainty ≥
`DIAGNOSIS_CHEMICAL_MIN_CERTAINTY` (moderate), always next to "confirm product and dose with your KVK".

**Escalation** returns the district KVK from the reference list (with its verification link) and a structured
case (`schema_version` 1.0: crop, stage, ~1 km location, the AI result labelled `ai_generated`, symptoms,
differential, weather, nearby reports). The photo is never included: the farmer attaches it when sharing.
`EscalationSink` is the plug-in point for a real KVK or state extension system; the current
`NotConnectedSink` answers `not_submitted / no_kvk_integration`, and the UI says the farmer shares the case
themselves. No expert response is simulated.

## Regenerative plan and crop options

**Practice plan** (`GET /api/farm/regenerative?lat=&lng=&crop=&sowing_date=`). The existing recommendations
(`services/regenerative_service.py`, triggered by soil, crop and forecast signals) are placed on the crop cycle:

| Field | Values |
|---|---|
| `timing` | `now`, `before_sowing`, `at_harvest`, `after_harvest`, `ongoing` (fixed per practice) |
| `horizon` | `current` (this season), `next` (next season), `long_term` (a lasting habit) |
| `confidence` | `moderate` when soil data informed the practice, otherwise `low` (general guidance) |
| `stage_based` | true only when a sowing date gave an FAO-56 stage estimate |

Harvest-time practices (residue retention) move into *this season* once the estimated stage is late season.
Without a sowing date the plan uses general timing, and the farm page asks for the date.

**Adoption** (`POST /api/farms/{id}/practices`, body `{practice, status}` with status `adopted | partial |
skipped`) stores the farmer's answer as a `regenerative` action in the farm history (`followed` yes / partial /
no), so outcomes can be asked about later and counted in the feedback metrics. It is self-reported.

**Crop options** (`GET /api/farm/crop-options?lat=&lng=&crop=`, `services/crop_options.py`) lists the farm's
crop and the crops typical for the nearest state (all supported crops when the point is more than 400 km from
every state reference point), with:

- seasonal water need (FAO Irrigation Water Management Training Manual No. 3, Table 13; rice excludes water
  lost to flooding and percolation);
- season length (FAO-56 Table 11);
- the number of verified ICAR disease reference entries;
- nearby AI-classified disease clusters (`null` when reports cannot be read: unknown, not zero).

It never ranks crops (`ranking: null`). Market prices, input costs and profit have no verified connected source,
so they are returned as `unavailable` and the UI says so and points to the mandi or eNAM.

## Voice, offline use and the "something is wrong" entry point

**Voice-first answers.** `POST /api/advisory` and `/followup` accept `mode: "text" | "speech"` (default text,
unchanged) and an optional `sowing_date`. Speech mode:

1. adds the farm risk engine's output (top action, severity, confidence, drivers, crop stage) to the DATA blocks,
   listed as the `farm_intelligence` source;
2. asks for at most 3 short sentences under 60 words: the action first, then the one reason that matters, with
   no lists, markdown, symbols or jargon. The language rule is the same as for text.

The response echoes `mode`. `POST /api/advisory/voice` (audio in, audio out) always uses speech mode. In the
advisor, a question dictated with the microphone and sent unedited gets a speech-mode answer. It is read out
automatically, since the farmer just spoke, and the text stays on screen with the usual sources and a "Read
aloud" button.

**Offline** (`frontend/src/lib/offline.ts`). Nothing pretends live services work offline.

- Farm panels (conditions, risks, crop health, soil and practices, crop options, KVK) save their last good
  response on the device. The copy is keyed by location, crop and sowing date, and dropped after 7 days.
- A saved copy is shown only when the device cannot reach the server (`OFFLINE` / `NETWORK_ERROR`) and nothing
  fresher is loaded. It appears with the offline reason and "Last successfully updated …", never as current.
  The panel reloads when the connection returns.
- The profile, language and farm record are stored on the device as before. The last advisor answer is saved
  and shown as "Your last answer, saved …".
- Follow-through, outcome and practice answers given while offline are queued (`krishi_outbox`) and sent on
  reconnect. An item is dropped only when delivered or rejected by the server (4xx).
- A banner says when the device is offline and how many answers are waiting.

**Something is wrong with my crop** (`/problem`) offers seven plain choices, each routed to an existing tool:

| Choice | Goes to |
|---|---|
| Take a photo / Insects or pest damage | `/diagnose` |
| Weather problem | `/farm#weather` |
| Too much or too little water | `/farm#risks` |
| Soil concern | `/farm#soil` |
| Crop is not growing well / I don't know | `/advisor?topic=…`, with a starting question the farmer can edit (never sent automatically) |

It is the landing page's main farmer action and is linked from the farm page's *Today* card.

## Policymaker early warning

`GET /api/dashboard/early-warning` (`services/early_warning.py`) returns three kinds of signal, plus coverage.
Each signal carries its geography, period, number of observations, confidence and source.

- **Disease signals.** Confident (moderate or high certainty), located `disease_detected` diagnoses are grouped
  by disease and 0.5° cell (~55 km, coarser than any farm) for the last 7 days, and compared with the 7 days
  before.
  - A signal needs at least 3 reports in the current week, the same bar as a cluster. Weaker groups are only
    counted (`below_threshold`).
  - `trend` is `new`, `rising`, `steady` or `falling`.
  - `confidence` is a sample-size rule, not a statistical test: under 5 reports is low, 5–9 moderate, 10 or
    more high.
- **Weather threats.** Watch and warning insights from the rule engine at one reference point per state. States
  whose forecast failed are listed as unavailable.
- **Crop-health anomalies.** Always `unavailable`, with the reason: satellite not configured, or regional
  aggregation not implemented. No value is estimated.
- **Coverage.** Observations and cells in 14 days. `insufficient_data` is true under 20 observations, and the
  dashboard then tells officials to treat signals as leads for field verification.

On the dashboard every chart and map (early warning, cluster map, 30-day trend, weather risk) ends with the same
block: period, geography, observations, source and limits.

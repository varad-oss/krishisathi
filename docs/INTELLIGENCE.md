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

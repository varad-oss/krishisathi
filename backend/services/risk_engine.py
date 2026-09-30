"""Farm risk engine: interpretable rules over the FarmContext.

Every risk says which evidence raised it (`drivers`, `evidence`), which published threshold or rule was
applied (`rules`), how strong the evidence is (`confidence`, `confidence_basis`) and what to do (`action`).
Weather thresholds are the ones in agro_rules (IMD where one exists), so this module adds no new weather
thresholds; it combines signals that agro_rules evaluates one at a time with soil water, crop stage, nearby
reports, the farm's own history and satellite observations. No score is produced that is not explained by
these rules, and no probability is stated: none of these rules has been calibrated against field outcomes.

Two separate axes (never collapse them):

* Risk level (`severity`: low | moderate | high | unavailable) - how concerning the condition would be if
  the signals are right. "unavailable" always carries a `reason`.
* Evidence confidence (`confidence`: low | moderate | high) - how reliable the signals behind that level are.
  "High risk, low confidence" is a legitimate answer: "this would be serious; the data is weak; go and look".

Evidence confidence
-------------------
Each evidence item gets a qualitative `reliability` from what kind of statement it is (EVIDENCE_RELIABILITY):
a forecast for the next two days is "moderate", further out or a multi-day total is "low"; modelled soil
water, AI-classified reports and AI photo diagnoses are "low"; a Sentinel-2 value is "moderate" only when the
satellite quality summary is "good" (drawn field, mostly clear, mostly cropland), else "low". Nothing is
"high" on its own: no connected source is a ground observation of the farm.

Each item also has a `role` for the risk's stated level:
* required   - the level depends on it (e.g. "rain AND wet soil" for moderate waterlogging). Confidence is
               the weakest required item: a conclusion is no stronger than its weakest necessary condition.
* supporting - an alternative or corroborating signal. Confidence is the strongest one.
* context    - shown, but does not raise the risk (stale or distant reports, low-certainty diagnoses).

Independence: evidence sharing an upstream source is one `group` (the forecast, soil moisture and topsoil
water all come from the same weather model; nearby outbreak clusters are built from the same AI photo
diagnoses as the farm's own history; NDVI change and NDVI baseline share the same current Sentinel-2 value).
Severity rules that need corroboration (disease "high") count distinct groups, never evidence items.
Agreement between independent groups is reported in `confidence_basis` but does not raise confidence:
without outcome calibration there is no basis for a numeric boost.
"""
from datetime import date as Date
from typing import Optional

from models.intelligence import Evidence, Risk, RuleRef, TopAction
from services.agro_rules import GUIDANCE as AGRO_GUIDANCE
from services.farm_context import FarmContext

ENGINE = {"id": "krishisathi-farm-risk-engine", "version": "1.1", "kind": "rule_based", "ai_used": False}

SEVERITY_RANK = {"unavailable": 0, "low": 1, "moderate": 2, "high": 3}
CONFIDENCE_RANK = {None: 0, "low": 1, "moderate": 2, "high": 3}
# Tie-break when two risks share a severity: the more damaging and less reversible first.
CATEGORY_ORDER = ["waterlogging", "heat_stress", "cold_stress", "water_stress", "disease", "harvest_weather",
                  "crop_health", "spray_window", "pest"]

GUIDANCE = AGRO_GUIDANCE["name"]
SOIL_WATER_RULE = RuleRef(id="soil_water_status", source="Saxton & Rawls (2006) pedotransfer; FAO-56 depletion fraction p = 0.5",
                          url="https://doi.org/10.2136/sssaj2005.0117")
HEAT_STAGE_RULE = RuleRef(id="heat_sensitive_stage", source="Hatfield & Prueger (2015), Weather and Climate Extremes 10:4-10",
                          url="https://doi.org/10.1016/j.wace.2015.08.001")
STAGE_RULE = RuleRef(id="crop_stage_calendar", source="FAO Irrigation and Drainage Paper 56, Table 11",
                     url="https://www.fao.org/4/x0490e/x0490e0b.htm")
DISEASE_RULE = RuleRef(id="disease_signal_count", source=f"{GUIDANCE}; high only when independent sources agree")
NDVI_RULE = RuleRef(id="ndvi_decline", source=f"{GUIDANCE}; screening threshold, not a validated crop-loss indicator")
NDVI_DECLINE = -0.1   # NDVI change between two 30-day windows that is worth a field visit
BASELINE_RULE = RuleRef(id="ndvi_baseline_range", source="KrishiSathi rule: current NDVI outside the range of the same weeks in previous years")
SAR_WATER_RULE = RuleRef(id="sar_water_signal", source="UN-SPIDER Recommended Practice, Sentinel-1 flood mapping (VH ratio > 1.25)",
                         url="https://www.un-spider.org/advisory-support/recommended-practices/recommended-practice-google-earth-engine-flood-mapping")
RECENT_DIAGNOSIS_DAYS = 14
FORECAST_RELIABLE_DAYS = 2          # beyond this lead time a single-point forecast is treated as low reliability
RAIN_LIKELY_PCT = 50
OUTBREAK_RELEVANT_KM = 50           # the clustering radius; farther clusters are context only
OUTBREAK_FRESH_DAYS = 7             # the clustering window; older last reports are context only
DIAGNOSIS_DRIVER_CERTAINTY = ("moderate", "high")  # a low-certainty photo check never raises a farm risk

# Independence groups (see module docstring).
WEATHER_MODEL, SENTINEL2, SENTINEL1, AI_PHOTO_REPORTS, CROP_CALENDAR = "weather_model", "sentinel2", "sentinel1", "ai_photo_reports", "crop_calendar"


def _rule(insight: dict) -> RuleRef:
    src = insight["basis"]["source"]
    return RuleRef(id=insight["id"], source=src["name"], url=src.get("url"))


# --- evidence ------------------------------------------------------------------------------------

def _lead_days(day: Optional[str], today: Date) -> Optional[int]:
    try:
        return (Date.fromisoformat(day[:10]) - today).days if day else None
    except ValueError:
        return None


def _forecast_reliability(e: Evidence, today: Date) -> tuple[str, str]:
    if e.id == "dry_spell_forecast":
        return "low", "multi_day_forecast_total"
    lead = _lead_days(e.date, today)
    if lead is None or lead > FORECAST_RELIABLE_DAYS:
        return "low", "forecast_beyond_2_days"
    prob = e.params.get("probability_pct")
    if e.id == "rain_forecast" and isinstance(prob, (int, float)) and prob < RAIN_LIKELY_PCT:
        return "low", "forecast_low_probability"
    return "moderate", "forecast_within_2_days"


def _satellite_quality(ctx: FarmContext) -> Optional[str]:
    return ((ctx.crop_health.data or {}).get("quality") or {}).get("level")


def _grade(e: Evidence, ctx: FarmContext, role: str = "supporting") -> Evidence:
    """Sets the evidence's independence group, reliability and role (EVIDENCE_RELIABILITY in the docstring)."""
    basis_tag = None
    if e.basis == "forecast":
        group, (level, basis_tag) = WEATHER_MODEL, _forecast_reliability(e, ctx.today)
    elif e.id == "wind_now":
        group, level, basis_tag = WEATHER_MODEL, "moderate", "current_model_estimate"
    elif e.id in ("soil_moisture", "soil_water_status"):
        group, level, basis_tag = WEATHER_MODEL, "low", "modelled_soil_water"
    elif e.id in ("ndvi_change", "ndvi_baseline"):
        quality = _satellite_quality(ctx)
        group, level, basis_tag = SENTINEL2, "moderate" if quality == "good" else "low", f"satellite_quality_{quality or 'unknown'}"
    elif e.id == "sar_vh_change":
        group, level, basis_tag = SENTINEL1, "low", "radar_screening_signal"
    elif e.id == "nearby_outbreak":
        group, level, basis_tag = AI_PHOTO_REPORTS, "low", "ai_classified_reports"
    elif e.id == "recent_diagnosis":
        group, level, basis_tag = AI_PHOTO_REPORTS, "low", "ai_diagnosis_unconfirmed"
    elif e.id == "crop_stage":
        group, level, basis_tag = CROP_CALENDAR, ctx.crop_stage.get("confidence") or "low", "crop_stage_estimate"
    else:
        group, level = e.source, "low"
    e.group, e.reliability, e.role = group, level, role
    e.params = {**e.params, "reliability_basis": basis_tag} if basis_tag else e.params
    return e


def evidence_confidence(evidence: list[Evidence]) -> tuple[Optional[str], list[str], int]:
    """(confidence, basis ids, independent groups) from graded evidence. See the module docstring."""
    required = [e for e in evidence if e.role == "required"]
    supporting = [e for e in evidence if e.role == "supporting"]
    counted = required + supporting
    if not counted:
        return None, [], 0
    if required:
        weakest = min(required, key=lambda e: CONFIDENCE_RANK[e.reliability])
        level, basis = weakest.reliability, ["weakest_required_condition", weakest.params.get("reliability_basis")]
    else:
        strongest = max(supporting, key=lambda e: CONFIDENCE_RANK[e.reliability])
        level, basis = strongest.reliability, [strongest.params.get("reliability_basis")]
    groups = {e.group for e in counted}
    basis.append("independent_sources_agree" if len(groups) >= 2 else "single_source")
    if len(counted) > len(groups):
        basis.append("correlated_signals_counted_once")
    return level, [b for b in dict.fromkeys(basis) if b], len(groups)


def _ev_insight(i: dict) -> Evidence:
    p = i["params"]
    if i["id"] in ("heavy_rain", "rain_expected"):
        return Evidence(id="rain_forecast", value=p.get("precipitation_mm"), unit="mm", date=i["date"], basis="forecast",
                        source="weather", params={"probability_pct": p.get("probability_pct")})
    if i["id"] == "heat_stress":
        return Evidence(id="temp_max_forecast", value=p.get("temp_max_c"), unit="°C", date=i["date"], basis="forecast", source="weather")
    if i["id"] == "cold_stress":
        return Evidence(id="temp_min_forecast", value=p.get("temp_min_c"), unit="°C", date=i["date"], basis="forecast", source="weather")
    if i["id"] == "fungal_risk":
        return Evidence(id="humid_forecast", value=p.get("humidity_mean_pct"), unit="%", date=i["date"], basis="forecast",
                        source="weather", params={"temp_mean_c": p.get("temp_mean_c")})
    if i["id"] == "dry_spell":
        return Evidence(id="dry_spell_forecast", value=p.get("precipitation_total_mm"), unit="mm", date=i["date"], basis="forecast",
                        source="weather", params={"et0_total_mm": p.get("et0_total_mm"), "days": p.get("days")})
    if i["id"] == "spray_wind":
        return Evidence(id="wind_now", value=p.get("wind_kmh"), unit="km/h", basis="model_estimate", source="weather")
    raise ValueError(i["id"])


def _ev_soil_water(ctx: FarmContext) -> list[Evidence]:
    cur = ctx.weather.data["current"] if ctx.weather.ok else {}
    out = []
    if cur.get("soil_moisture_3_9cm") is not None:
        out.append(Evidence(id="soil_moisture", value=cur["soil_moisture_3_9cm"], unit="m³/m³", date=cur.get("valid_at"),
                            basis="model_estimate", source="weather", params={"depth": "3-9 cm"}))
    sw = ctx.soil_water
    if sw["status"] != "unavailable":
        out.append(Evidence(id="soil_water_status", value=sw["status"], basis="model_estimate", source="soil_water",
                            params={"available_water_fraction": sw["available_water_fraction"]}))
    return out


def _sar(ctx: FarmContext) -> dict:
    """Sentinel-1 summary when the satellite query ran (it is reported even when Sentinel-2 saw only cloud)."""
    data = ctx.crop_health.data or {}
    sar = data.get("sar") or {}
    return sar if sar.get("status") == "available" else {}


def _ev_sar(sar: dict) -> Evidence:
    return Evidence(id="sar_vh_change", value=sar.get("vh_change_db"), unit="dB", date=sar.get("latest_image_date"),
                    basis="satellite_observation", source="satellite_radar",
                    params={"vh_db": sar.get("vh_db"), "vh_db_previous": sar.get("vh_db_previous"), "orbit_pass": sar.get("orbit_pass")})


def _ev_stage(ctx: FarmContext) -> list[Evidence]:
    s = ctx.crop_stage
    if s["status"] not in ("estimated", "beyond_season"):
        return []
    return [Evidence(id="crop_stage", value=s["stage"] or s["status"], basis="rule_based", source="crop_stage",
                     params={"days_since_sowing": s["days_since_sowing"], "calendar": s["calendar"]})]


def _unavailable(category: str, reason: str, ctx: FarmContext, **extra) -> Risk:
    return Risk(category=category, severity="unavailable", reason=reason, crop=ctx.crop, crop_stage=ctx.crop_stage.get("stage"), **extra)


def _risk(category: str, severity: str, ctx: FarmContext, evidence: Optional[list[tuple[Evidence, str]]] = None,
          clear_confidence: Optional[str] = None, **fields) -> Risk:
    """`evidence`: (item, role) pairs. Without non-context evidence the risk is an all-clear whose confidence is
    `clear_confidence` (how much the checked sources can say that nothing crossed a rule)."""
    graded = [_grade(e, ctx, role) for e, role in (evidence or [])]
    confidence, basis, groups = evidence_confidence(graded)
    if confidence is None:
        confidence, basis = clear_confidence, ["no_rule_triggered"] if clear_confidence else []
    return Risk(category=category, severity=severity, confidence=confidence, confidence_basis=basis, independent_sources=groups,
                evidence=graded, crop=ctx.crop, crop_stage=ctx.crop_stage.get("stage"), **fields)


def _all(items: list[Evidence], role: str) -> list[tuple[Evidence, str]]:
    return [(e, role) for e in items]


# --- individual risks ----------------------------------------------------------------------------

def waterlogging(ctx: FarmContext) -> Risk:
    if not ctx.weather.ok:
        return _unavailable("waterlogging", "weather_unavailable", ctx)
    heavy, rain = ctx.insight("heavy_rain"), ctx.insight("rain_expected")
    wet = ctx.soil_water["status"] == "wet"
    soil_ev = _ev_soil_water(ctx)
    soil_rules = [SOIL_WATER_RULE] if soil_ev and ctx.soil_water["status"] != "unavailable" else []
    if heavy:
        # The heavy-rain threshold alone sets the level; modelled soil water comes from the same weather model.
        return _risk("waterlogging", "high", ctx, [(_ev_insight(heavy), "required"), *_all(soil_ev, "context")],
                     drivers=["heavy_rain_forecast"] + (["soil_wet"] if wet else []), action="clear_drainage", date=heavy["date"],
                     rules=[_rule(heavy), *soil_rules])
    sar = _sar(ctx)
    if sar.get("water_signal"):
        # Radar sees through the cloud that usually accompanies waterlogging; a screening signal, never a flood map.
        drivers = ["sar_water_signal"] + (["rain_expected"] if rain else []) + (["soil_wet"] if wet else [])
        evidence = [(_ev_sar(sar), "required")] + ([(_ev_insight(rain), "context")] if rain else []) + _all(soil_ev, "context")
        return _risk("waterlogging", "moderate", ctx, evidence, drivers=drivers, action="clear_drainage",
                     date=sar.get("latest_image_date"), rules=[SAR_WATER_RULE] + ([_rule(rain)] if rain else []) + soil_rules)
    if rain and wet:
        # Moderate needs both conditions, so the weaker one (modelled soil water) sets the confidence.
        soil_status = [e for e in soil_ev if e.id == "soil_water_status"]
        return _risk("waterlogging", "moderate", ctx,
                     [(_ev_insight(rain), "required"), *_all(soil_status, "required"), *_all([e for e in soil_ev if e not in soil_status], "context")],
                     drivers=["rain_expected", "soil_wet"], action="delay_irrigation", date=rain["date"], rules=[_rule(rain), SOIL_WATER_RULE])
    if rain:
        return _risk("waterlogging", "low", ctx, [(_ev_insight(rain), "supporting"), *_all(soil_ev, "context")], drivers=["rain_expected"],
                     action="delay_irrigation", date=rain["date"], rules=[_rule(rain), *soil_rules])
    return _risk("waterlogging", "low", ctx, _all(soil_ev, "supporting" if wet else "context"),
                 clear_confidence="low" if soil_ev else "moderate", drivers=["soil_wet"] if wet else ["no_heavy_rain"], rules=soil_rules)


def water_stress(ctx: FarmContext) -> Risk:
    if not ctx.weather.ok:
        return _unavailable("water_stress", "weather_unavailable", ctx)
    spell = ctx.insight("dry_spell")
    rain_soon = ctx.insight("rain_expected") or ctx.insight("heavy_rain")
    dry = ctx.soil_water["status"] == "dry"
    soil_ev = _ev_soil_water(ctx)
    rules = ([_rule(spell)] if spell else []) + ([SOIL_WATER_RULE] if ctx.soil_water["status"] != "unavailable" else [])
    drivers = (["dry_spell_forecast"] if spell else []) + (["soil_dry"] if dry else [])
    spell_ev = [_ev_insight(spell)] if spell else []
    if spell and dry:
        status = [e for e in soil_ev if e.id == "soil_water_status"]
        return _risk("water_stress", "high", ctx, [*_all(spell_ev, "required"), *_all(status, "required"),
                                                    *_all([e for e in soil_ev if e not in status], "context")],
                     drivers=drivers, action="irrigate_soon", date=spell["date"], rules=rules)
    if (spell or dry) and not rain_soon:
        return _risk("water_stress", "moderate", ctx, [*_all(spell_ev, "supporting"), *_all(soil_ev, "supporting" if dry else "context")],
                     drivers=drivers, action="irrigate_soon", date=spell["date"] if spell else None, rules=rules)
    return _risk("water_stress", "low", ctx, [*_all(spell_ev, "context"), *_all(soil_ev, "context")],
                 clear_confidence="low" if soil_ev else "moderate",
                 drivers=["rain_expected"] if rain_soon else drivers or ["no_dry_spell"], rules=rules)


def _temperature(ctx: FarmContext, category: str, insight_id: str, action: str) -> Risk:
    if not ctx.weather.ok:
        return _unavailable(category, "weather_unavailable", ctx)
    i = ctx.insight(insight_id)
    if not i:
        return _risk(category, "low", ctx, clear_confidence="moderate", drivers=[f"no_{insight_id}"])
    severity = "high" if i["severity"] == "warning" else "moderate"
    drivers, evidence, rules = [f"{insight_id}_forecast"], [(_ev_insight(i), "required")], [_rule(i)]
    # Heat during flowering and grain/fruit set does the most damage; the FAO-56 mid-season stage covers it.
    if category == "heat_stress" and severity == "moderate" and ctx.crop_stage.get("stage") == "mid_season":
        severity = "high"
        drivers.append("sensitive_stage")
        evidence += _all(_ev_stage(ctx), "required")  # "high" rests on the stage estimate too
        rules += [STAGE_RULE, HEAT_STAGE_RULE]
    return _risk(category, severity, ctx, evidence, drivers=drivers, action=action, date=i["date"], rules=rules)


def _outbreak_role(o: dict, ctx: FarmContext) -> str:
    """A cluster raises the risk only when it is within the clustering radius and reported in the clustering window."""
    age = _lead_days(ctx.today.isoformat(), Date.fromisoformat(o["last_report_at"][:10]))
    return "supporting" if o["distance_km"] <= OUTBREAK_RELEVANT_KM and age is not None and age <= OUTBREAK_FRESH_DAYS else "context"


def disease(ctx: FarmContext) -> Risk:
    drivers, evidence, rules, date = [], [], [], None
    fungal = ctx.insight("fungal_risk")
    if fungal:
        drivers.append("fungal_weather")
        evidence.append((_ev_insight(fungal), "supporting"))
        rules.append(_rule(fungal))
        date = fungal["date"]
    if ctx.outbreaks.ok and ctx.outbreaks.data:
        roles = []
        for o in ctx.outbreaks.data[:3]:
            role = _outbreak_role(o, ctx)
            roles.append(role)
            evidence.append((Evidence(id="nearby_outbreak", value=o["disease"], date=o["last_report_at"][:10], basis="ai_classified_reports",
                                      source="outbreaks", params={"report_count": o["report_count"], "distance_km": o["distance_km"],
                                                                  "severity": o["severity"]}), role))
        if "supporting" in roles:
            drivers.append("nearby_outbreak")
    recent = [d for d in ctx.history.get("recent_diagnoses", []) if d.get("status") == "disease_detected"
              and d.get("age_days", RECENT_DIAGNOSIS_DAYS) < RECENT_DIAGNOSIS_DAYS]
    if recent:
        roles = []
        for d in recent[:2]:
            role = "supporting" if d.get("certainty") in DIAGNOSIS_DRIVER_CERTAINTY else "context"
            roles.append(role)
            evidence.append((Evidence(id="recent_diagnosis", value=d.get("disease"), date=d.get("date"), basis="ai_generated",
                                      source="farm_history", params={"certainty": d.get("certainty")}), role))
        if "supporting" in roles:
            drivers.append("recent_farm_diagnosis")

    if not drivers:
        if not ctx.weather.ok and not ctx.outbreaks.ok:
            return _unavailable("disease", "weather_and_reports_unavailable", ctx)
        if not ctx.weather.ok:
            return _unavailable("disease", "weather_unavailable", ctx)
        return _risk("disease", "low", ctx, evidence, clear_confidence="low", drivers=["no_disease_signal"],
                     reason=None if ctx.outbreaks.ok else "reports_unavailable")
    # "High" needs independent sources to agree: disease-favouring weather AND AI-photo evidence of the disease.
    # Nearby clusters and the farm's own diagnoses are the same kind of source (AI photo checks), so together they
    # still count once. When the level rests on both, each is required and the weaker sets the confidence.
    groups = {"weather": bool(fungal), "reports": any(d in drivers for d in ("nearby_outbreak", "recent_farm_diagnosis"))}
    severity = "high" if all(groups.values()) else "moderate"
    if severity == "high":
        evidence = [(e, "required" if role == "supporting" else role) for e, role in evidence]
    return _risk("disease", severity, ctx, evidence, drivers=drivers, action="scout_for_disease", date=date, rules=[*rules, DISEASE_RULE])


def pest(ctx: FarmContext) -> Risk:
    # No pest surveillance or trap data is connected; a weather-only pest score would be guesswork.
    return _unavailable("pest", "no_pest_data_source", ctx)


def spray_window(ctx: FarmContext) -> Risk:
    if not ctx.weather.ok:
        return _unavailable("spray_window", "weather_unavailable", ctx)
    days = [d["date"] for d in ctx.weather.data["daily"][:2]]
    drivers, evidence, rules, date = [], [], [], None
    wind = ctx.insight("spray_wind")
    if wind:
        drivers.append("wind_high")
        evidence.append((_ev_insight(wind), "supporting"))
        rules.append(_rule(wind))
    rain = ctx.insight("heavy_rain") or ctx.insight("rain_expected")
    if rain and rain["date"] in days:
        drivers.append("rain_soon")
        evidence.append((_ev_insight(rain), "supporting"))
        rules.append(_rule(rain))
        date = rain["date"]
    if drivers:
        return _risk("spray_window", "moderate", ctx, evidence, drivers=drivers, action="postpone_spraying", date=date, rules=rules)
    return _risk("spray_window", "low", ctx, clear_confidence="moderate", drivers=["no_spray_conflict"])


def harvest_weather(ctx: FarmContext) -> Risk:
    stage = ctx.crop_stage
    if stage["status"] not in ("estimated", "beyond_season"):
        return _unavailable("harvest_weather", "crop_stage_unknown", ctx)
    if not ctx.weather.ok:
        return _unavailable("harvest_weather", "weather_unavailable", ctx)
    if stage["status"] == "estimated" and stage["stage"] != "late_season":
        return _risk("harvest_weather", "low", ctx, _all(_ev_stage(ctx), "supporting"), drivers=["not_harvest_stage"], rules=[STAGE_RULE])
    heavy, rain = ctx.insight("heavy_rain"), ctx.insight("rain_expected")
    i = heavy or rain
    if not i:
        return _risk("harvest_weather", "low", ctx, _all(_ev_stage(ctx), "context"), clear_confidence="low",
                     drivers=["no_rain_forecast"], rules=[STAGE_RULE])
    # The risk needs both: rain in the forecast AND the crop being at harvest stage.
    return _risk("harvest_weather", "high" if heavy else "moderate", ctx, [(_ev_insight(i), "required"), *_all(_ev_stage(ctx), "required")],
                 drivers=["harvest_stage", "heavy_rain_forecast" if heavy else "rain_expected"], action="protect_harvest",
                 date=i["date"], rules=[_rule(i), STAGE_RULE])


def crop_health(ctx: FarmContext) -> Risk:
    sat = ctx.crop_health
    if not sat.ok:
        return _unavailable("crop_health", sat.reason or sat.status, ctx)
    h = sat.data
    change = h.get("change")
    baseline = h.get("baseline") or {}
    below = baseline.get("status") == "available" and baseline.get("position") == "below_range"
    if change is None and baseline.get("status") != "available":
        return _unavailable("crop_health", "insufficient_history", ctx)
    evidence = []
    if change is not None:
        evidence.append(Evidence(id="ndvi_change", value=change, date=h.get("latest_image_date"), basis="satellite_observation", source="satellite",
                                 params={"ndvi": h.get("ndvi"), "ndvi_previous": h.get("ndvi_previous"), "clear_pixel_fraction": h.get("clear_pixel_fraction"),
                                         "field_mode": (h.get("roi") or {}).get("mode")}))
    if baseline.get("status") == "available":
        evidence.append(Evidence(id="ndvi_baseline", value=baseline.get("position"), date=h.get("latest_image_date"), basis="satellite_observation",
                                 source="satellite", params={"ndvi": h.get("ndvi"), "min": baseline.get("min"), "max": baseline.get("max"),
                                                             "years": sum(y["ndvi"] is not None for y in baseline.get("years", []))}))
    declined = change is not None and change <= NDVI_DECLINE
    drivers = (["ndvi_decline"] if declined else []) + (["ndvi_below_baseline"] if below else [])
    rules = ([NDVI_RULE] if change is not None else []) + ([BASELINE_RULE] if baseline.get("status") == "available" else [])
    # Change and baseline share the same current Sentinel-2 value: one source, so agreement does not add confidence.
    # Confidence follows the satellite quality summary (field outline, clear share, land-cover mix). Crop rotation,
    # sowing date and harvest also move NDVI, so the level never goes above moderate.
    if drivers:
        return _risk("crop_health", "moderate", ctx, _all(evidence, "supporting"), drivers=drivers, action="inspect_field",
                     date=h.get("latest_image_date"), rules=rules)
    return _risk("crop_health", "low", ctx, _all(evidence, "supporting"), drivers=["ndvi_stable"], rules=rules)


def assess(ctx: FarmContext) -> list[Risk]:
    risks = [
        waterlogging(ctx), water_stress(ctx),
        _temperature(ctx, "heat_stress", "heat_stress", "protect_from_heat"),
        _temperature(ctx, "cold_stress", "cold_stress", "protect_from_cold"),
        disease(ctx), pest(ctx), spray_window(ctx), harvest_weather(ctx), crop_health(ctx),
    ]
    return sorted(risks, key=_priority)


def _priority(r: Risk):
    """What to look at first: the more serious risk; then the one that happens sooner; then the one with stronger
    evidence; then the less reversible kind of damage (CATEGORY_ORDER)."""
    return (-SEVERITY_RANK[r.severity], r.action is None, r.date or "9999-12-31", -CONFIDENCE_RANK[r.confidence],
            CATEGORY_ORDER.index(r.category))


def _priority_reason(first: Risk, others: list[Risk]) -> str:
    if not others:
        return "only_action"
    nxt = others[0]
    if SEVERITY_RANK[first.severity] > SEVERITY_RANK[nxt.severity]:
        return "highest_severity"
    if (first.date or "9999-12-31") < (nxt.date or "9999-12-31"):
        return "soonest"
    if CONFIDENCE_RANK[first.confidence] > CONFIDENCE_RANK[nxt.confidence]:
        return "stronger_evidence"
    return "less_reversible"


def top_action(risks: list[Risk], ctx: FarmContext) -> TopAction:
    """The one thing to pay attention to first: the highest-priority risk that has an action (see _priority)."""
    actionable = [r for r in sorted(risks, key=_priority) if r.action]
    first: Optional[Risk] = actionable[0] if actionable else None
    if first and first.severity in ("high", "moderate"):
        return _from_risk(first, actionable[1:])
    if not ctx.weather.ok:
        # Without weather most risks cannot be assessed, so "nothing to do" would be a false all-clear.
        return TopAction(status="unavailable", reason="weather_unavailable")
    if first:
        return _from_risk(first, actionable[1:])
    return TopAction(status="routine", action="routine_monitoring", drivers=["no_risk_above_low"])


def _from_risk(r: Risk, others: list[Risk]) -> TopAction:
    return TopAction(status="action", action=r.action, category=r.category, severity=r.severity, confidence=r.confidence,
                     confidence_basis=r.confidence_basis, drivers=r.drivers, evidence=r.evidence, rules=r.rules, date=r.date,
                     priority_reason=_priority_reason(r, others))

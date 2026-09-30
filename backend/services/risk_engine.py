"""Farm risk engine: interpretable rules over the FarmContext.

Every risk says which evidence raised it (`drivers`, `evidence`), which published threshold or rule was
applied (`rules`), how sure it is (`confidence`) and what to do (`action`). Weather thresholds are the
ones in agro_rules (IMD where one exists), so this module adds no new weather thresholds; it combines
signals that agro_rules evaluates one at a time with soil water, crop stage, nearby reports, the farm's
own history and satellite observations. No score is produced that is not explained by these rules.

Severity is one of low | moderate | high | unavailable. "unavailable" always carries a `reason`.
"""
from typing import Optional

from models.intelligence import Evidence, Risk, RuleRef, TopAction
from services.agro_rules import GUIDANCE as AGRO_GUIDANCE
from services.farm_context import FarmContext

ENGINE = {"id": "krishisathi-farm-risk-engine", "version": "1.0", "kind": "rule_based", "ai_used": False}

SEVERITY_RANK = {"unavailable": 0, "low": 1, "moderate": 2, "high": 3}
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
DISEASE_RULE = RuleRef(id="disease_signal_count", source=GUIDANCE)
NDVI_RULE = RuleRef(id="ndvi_decline", source=f"{GUIDANCE}; screening threshold, not a validated crop-loss indicator")
NDVI_DECLINE = -0.1   # NDVI change between two 30-day windows that is worth a field visit
RECENT_DIAGNOSIS_DAYS = 14


def _rule(insight: dict) -> RuleRef:
    src = insight["basis"]["source"]
    return RuleRef(id=insight["id"], source=src["name"], url=src.get("url"))


# --- evidence ------------------------------------------------------------------------------------

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


def _ev_stage(ctx: FarmContext) -> list[Evidence]:
    s = ctx.crop_stage
    if s["status"] not in ("estimated", "beyond_season"):
        return []
    return [Evidence(id="crop_stage", value=s["stage"] or s["status"], basis="rule_based", source="crop_stage",
                     params={"days_since_sowing": s["days_since_sowing"], "calendar": s["calendar"]})]


def _unavailable(category: str, reason: str, ctx: FarmContext, **extra) -> Risk:
    return Risk(category=category, severity="unavailable", reason=reason, crop=ctx.crop, crop_stage=ctx.crop_stage.get("stage"), **extra)


def _risk(category: str, severity: str, ctx: FarmContext, **fields) -> Risk:
    return Risk(category=category, severity=severity, crop=ctx.crop, crop_stage=ctx.crop_stage.get("stage"), **fields)


# --- individual risks ----------------------------------------------------------------------------

def waterlogging(ctx: FarmContext) -> Risk:
    if not ctx.weather.ok:
        return _unavailable("waterlogging", "weather_unavailable", ctx)
    heavy, rain = ctx.insight("heavy_rain"), ctx.insight("rain_expected")
    wet = ctx.soil_water["status"] == "wet"
    soil_ev = _ev_soil_water(ctx)
    soil_rules = [SOIL_WATER_RULE] if soil_ev and ctx.soil_water["status"] != "unavailable" else []
    if heavy:
        return _risk("waterlogging", "high", ctx, confidence="moderate", drivers=["heavy_rain_forecast"] + (["soil_wet"] if wet else []),
                     evidence=[_ev_insight(heavy), *soil_ev], action="clear_drainage", date=heavy["date"], rules=[_rule(heavy), *soil_rules])
    if rain and wet:
        return _risk("waterlogging", "moderate", ctx, confidence="low", drivers=["rain_expected", "soil_wet"],
                     evidence=[_ev_insight(rain), *soil_ev], action="delay_irrigation", date=rain["date"], rules=[_rule(rain), SOIL_WATER_RULE])
    if rain:
        return _risk("waterlogging", "low", ctx, confidence="moderate", drivers=["rain_expected"], evidence=[_ev_insight(rain), *soil_ev],
                     action="delay_irrigation", date=rain["date"], rules=[_rule(rain), *soil_rules])
    return _risk("waterlogging", "low", ctx, confidence="low" if soil_ev else "moderate", drivers=["soil_wet"] if wet else ["no_heavy_rain"],
                 evidence=soil_ev, rules=soil_rules)


def water_stress(ctx: FarmContext) -> Risk:
    if not ctx.weather.ok:
        return _unavailable("water_stress", "weather_unavailable", ctx)
    spell = ctx.insight("dry_spell")
    rain_soon = ctx.insight("rain_expected") or ctx.insight("heavy_rain")
    dry = ctx.soil_water["status"] == "dry"
    soil_ev = _ev_soil_water(ctx)
    evidence = ([_ev_insight(spell)] if spell else []) + soil_ev
    rules = ([_rule(spell)] if spell else []) + ([SOIL_WATER_RULE] if ctx.soil_water["status"] != "unavailable" else [])
    drivers = (["dry_spell_forecast"] if spell else []) + (["soil_dry"] if dry else [])
    if spell and dry:
        return _risk("water_stress", "high", ctx, confidence="low", drivers=drivers, evidence=evidence, action="irrigate_soon",
                     date=spell["date"], rules=rules)
    if (spell or dry) and not rain_soon:
        return _risk("water_stress", "moderate", ctx, confidence="moderate" if spell and not dry else "low", drivers=drivers,
                     evidence=evidence, action="irrigate_soon", date=spell["date"] if spell else None, rules=rules)
    return _risk("water_stress", "low", ctx, confidence="low" if soil_ev else "moderate",
                 drivers=["rain_expected"] if rain_soon else drivers or ["no_dry_spell"], evidence=evidence, rules=rules)


def _temperature(ctx: FarmContext, category: str, insight_id: str, action: str) -> Risk:
    if not ctx.weather.ok:
        return _unavailable(category, "weather_unavailable", ctx)
    i = ctx.insight(insight_id)
    if not i:
        return _risk(category, "low", ctx, confidence="moderate", drivers=[f"no_{insight_id}"])
    severity = "high" if i["severity"] == "warning" else "moderate"
    drivers, evidence, rules = [f"{insight_id}_forecast"], [_ev_insight(i)], [_rule(i)]
    # Heat during flowering and grain/fruit set does the most damage; the FAO-56 mid-season stage covers it.
    if category == "heat_stress" and severity == "moderate" and ctx.crop_stage.get("stage") == "mid_season":
        severity = "high"
        drivers.append("sensitive_stage")
        evidence += _ev_stage(ctx)
        rules += [STAGE_RULE, HEAT_STAGE_RULE]
    return _risk(category, severity, ctx, confidence="moderate", drivers=drivers, evidence=evidence, action=action, date=i["date"], rules=rules)


def disease(ctx: FarmContext) -> Risk:
    drivers, evidence, rules, date = [], [], [], None
    fungal = ctx.insight("fungal_risk")
    if fungal:
        drivers.append("fungal_weather")
        evidence.append(_ev_insight(fungal))
        rules.append(_rule(fungal))
        date = fungal["date"]
    if ctx.outbreaks.ok and ctx.outbreaks.data:
        drivers.append("nearby_outbreak")
        for o in ctx.outbreaks.data[:3]:
            evidence.append(Evidence(id="nearby_outbreak", value=o["disease"], date=o["last_report_at"][:10], basis="ai_classified_reports",
                                     source="outbreaks", params={"report_count": o["report_count"], "distance_km": o["distance_km"], "severity": o["severity"]}))
    recent = [d for d in ctx.history.get("recent_diagnoses", []) if d.get("status") == "disease_detected"
              and d.get("age_days", RECENT_DIAGNOSIS_DAYS) < RECENT_DIAGNOSIS_DAYS]
    if recent:
        drivers.append("recent_farm_diagnosis")
        for d in recent[:2]:
            evidence.append(Evidence(id="recent_diagnosis", value=d.get("disease"), date=d.get("date"), basis="ai_generated",
                                     source="farm_history", params={"certainty": d.get("certainty")}))

    if not drivers:
        if not ctx.weather.ok and not ctx.outbreaks.ok:
            return _unavailable("disease", "weather_and_reports_unavailable", ctx)
        if not ctx.weather.ok:
            return _unavailable("disease", "weather_unavailable", ctx)
        return _risk("disease", "low", ctx, confidence="low", drivers=["no_disease_signal"],
                     reason=None if ctx.outbreaks.ok else "reports_unavailable")
    # Independent signals (weather, nearby reports, the farm's own photo diagnoses) reinforce each other.
    severity = "high" if len(drivers) >= 2 else "moderate"
    return _risk("disease", severity, ctx, confidence="low", drivers=drivers, evidence=evidence, action="scout_for_disease",
                 date=date, rules=[*rules, DISEASE_RULE])


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
        evidence.append(_ev_insight(wind))
        rules.append(_rule(wind))
    rain = ctx.insight("heavy_rain") or ctx.insight("rain_expected")
    if rain and rain["date"] in days:
        drivers.append("rain_soon")
        evidence.append(_ev_insight(rain))
        rules.append(_rule(rain))
        date = rain["date"]
    if drivers:
        return _risk("spray_window", "moderate", ctx, confidence="moderate", drivers=drivers, evidence=evidence,
                     action="postpone_spraying", date=date, rules=rules)
    return _risk("spray_window", "low", ctx, confidence="moderate", drivers=["no_spray_conflict"])


def harvest_weather(ctx: FarmContext) -> Risk:
    stage = ctx.crop_stage
    if stage["status"] not in ("estimated", "beyond_season"):
        return _unavailable("harvest_weather", "crop_stage_unknown", ctx)
    if not ctx.weather.ok:
        return _unavailable("harvest_weather", "weather_unavailable", ctx)
    if stage["status"] == "estimated" and stage["stage"] != "late_season":
        return _risk("harvest_weather", "low", ctx, confidence=stage["confidence"], drivers=["not_harvest_stage"],
                     evidence=_ev_stage(ctx), rules=[STAGE_RULE])
    heavy, rain = ctx.insight("heavy_rain"), ctx.insight("rain_expected")
    i = heavy or rain
    if not i:
        return _risk("harvest_weather", "low", ctx, confidence="low", drivers=["no_rain_forecast"], evidence=_ev_stage(ctx), rules=[STAGE_RULE])
    return _risk("harvest_weather", "high" if heavy else "moderate", ctx, confidence="low",
                 drivers=["harvest_stage", "heavy_rain_forecast" if heavy else "rain_expected"],
                 evidence=[_ev_insight(i), *_ev_stage(ctx)], action="protect_harvest", date=i["date"], rules=[_rule(i), STAGE_RULE])


def crop_health(ctx: FarmContext) -> Risk:
    sat = ctx.crop_health
    if not sat.ok:
        return _unavailable("crop_health", sat.reason or sat.status, ctx)
    h = sat.data
    change = h.get("change")
    if change is None:
        return _unavailable("crop_health", "insufficient_history", ctx)
    evidence = [Evidence(id="ndvi_change", value=change, date=h.get("latest_image_date"), basis="satellite_observation", source="satellite",
                         params={"ndvi": h.get("ndvi"), "ndvi_previous": h.get("ndvi_previous"), "clear_pixel_fraction": h.get("clear_pixel_fraction")})]
    if change <= NDVI_DECLINE:
        return _risk("crop_health", "moderate", ctx, confidence="low", drivers=["ndvi_decline"], evidence=evidence,
                     action="inspect_field", date=h.get("latest_image_date"), rules=[NDVI_RULE])
    return _risk("crop_health", "low", ctx, confidence="low", drivers=["ndvi_stable"], evidence=evidence, rules=[NDVI_RULE])


def assess(ctx: FarmContext) -> list[Risk]:
    risks = [
        waterlogging(ctx), water_stress(ctx),
        _temperature(ctx, "heat_stress", "heat_stress", "protect_from_heat"),
        _temperature(ctx, "cold_stress", "cold_stress", "protect_from_cold"),
        disease(ctx), pest(ctx), spray_window(ctx), harvest_weather(ctx), crop_health(ctx),
    ]
    return sorted(risks, key=_priority)


def _priority(r: Risk):
    return (-SEVERITY_RANK[r.severity], r.action is None, r.date or "9999-12-31", CATEGORY_ORDER.index(r.category))


def top_action(risks: list[Risk], ctx: FarmContext) -> TopAction:
    """The one thing that matters most today: the highest-priority risk that has an action."""
    actionable = [r for r in sorted(risks, key=_priority) if r.action]
    first: Optional[Risk] = actionable[0] if actionable else None
    if first and first.severity in ("high", "moderate"):
        return _from_risk(first)
    if not ctx.weather.ok:
        # Without weather most risks cannot be assessed, so "nothing to do" would be a false all-clear.
        return TopAction(status="unavailable", reason="weather_unavailable")
    if first:
        return _from_risk(first)
    return TopAction(status="routine", action="routine_monitoring", drivers=["no_risk_above_low"])


def _from_risk(r: Risk) -> TopAction:
    return TopAction(status="action", action=r.action, category=r.category, severity=r.severity, confidence=r.confidence,
                     drivers=r.drivers, evidence=r.evidence, date=r.date)

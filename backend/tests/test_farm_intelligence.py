"""Farm intelligence: crop stage, soil water, risk engine, prioritization and the unified endpoint."""
from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from helpers import open_meteo_payload
from main import app
from models.exceptions import ServiceUnavailableException
from services import agro_rules, risk_engine
from services import weather_service as ws
from services.crop_stage import estimate_stage
from services.farm_context import FarmContext, Signal
from services.intelligence_service import assemble
from services.soil_water import topsoil_water, water_limits

client = TestClient(app)
TODAY = date(2026, 9, 26)  # first forecast day of open_meteo_payload()

LOAM = {"status": "available", "properties": {"ph": 7.1, "organic_carbon_pct": 1.45, "sand_pct": 40.0, "clay_pct": 20.0,
                                              "total_nitrogen_g_per_kg": 1.2},
        "ratings": {"ph": "neutral", "organic_carbon": "high"}, "provenance": {"retrieved_at": "2026-09-26T04:00:00+00:00"}}


def ctx(daily=None, moisture=0.27, soil=LOAM, sat=None, outbreaks=None, crop="Wheat", sowing=None, weather_ok=True, history=None, wind=8.5):
    payload = open_meteo_payload(**(daily or {}))
    payload["current"]["soil_moisture_3_9cm"] = moisture
    payload["current"]["wind_speed_10m"] = wind
    conditions = ws.parse_conditions(payload, 18.5, 73.8)
    weather = Signal("available", conditions) if weather_ok else Signal("unavailable", reason="weather_unavailable")
    sat = sat or Signal("not_configured", {"status": "unavailable", "reason": "not_configured"}, reason="not_configured")
    return FarmContext(
        lat=18.5, lng=73.8, crop=crop, sowing_date=sowing, today=TODAY,
        weather=weather, soil=Signal(soil["status"], soil, reason=soil.get("reason")), crop_health=sat,
        outbreaks=Signal("available", outbreaks or []),
        crop_stage=estimate_stage(crop, sowing, TODAY),
        soil_water=topsoil_water(moisture if weather_ok else None, soil),
        insights=agro_rules.evaluate(conditions) if weather_ok else [],
        history=history or {},
    )


def risks_by_category(c):
    return {r.category: r for r in risk_engine.assess(c)}


DRY_WEEK = {"precipitation_sum": [0, 0, 0, 0, 0, 0, 0], "precipitation_probability_max": [5] * 7,
            "relative_humidity_2m_mean": [40] * 7, "et0_fao_evapotranspiration": [5.0] * 7}


# --- crop stage --------------------------------------------------------------------------------

def test_stage_from_sowing_date_uses_fao56_calendar():
    s = estimate_stage("Wheat", date(2026, 7, 1), TODAY)  # day 87 of 20+25+60+30
    assert s["status"] == "estimated" and s["stage"] == "mid_season"
    assert s["days_since_sowing"] == 87 and s["season_length_days"] == 135
    assert s["confidence"] == "moderate"  # Table 11 has a Central India row for wheat
    assert "FAO" in s["reference"]["source"]


def test_stage_confidence_is_low_for_non_indian_calendar_rows():
    assert estimate_stage("Rice", date(2026, 9, 1), TODAY)["confidence"] == "low"


@pytest.mark.parametrize("crop,sowing,status", [
    ("Wheat", None, "not_provided"),
    (None, date(2026, 9, 1), "not_provided"),
    ("Chickpea", date(2026, 9, 1), "no_calendar"),     # no citable Table 11 row: never guess
    ("Wheat", date(2026, 10, 5), "before_sowing"),
    ("Wheat", date(2025, 1, 1), "beyond_season"),
])
def test_stage_is_not_guessed(crop, sowing, status):
    s = estimate_stage(crop, sowing, TODAY)
    assert s["status"] == status
    assert s["stage"] is None


# --- soil water --------------------------------------------------------------------------------

def test_saxton_rawls_matches_published_texture_class_values():
    wp, fc = water_limits(40, 20, 2.5 / 1.724)  # loam, 2.5 % organic matter
    assert round(fc, 2) == 0.28 and 0.12 <= wp <= 0.14


@pytest.mark.parametrize("moisture,status", [(0.18, "dry"), (0.24, "adequate"), (0.30, "wet")])
def test_topsoil_water_status(moisture, status):
    r = topsoil_water(moisture, LOAM)
    assert r["status"] == status and r["confidence"] == "low"


def test_topsoil_water_unavailable_without_texture_or_moisture():
    assert topsoil_water(0.3, {"status": "unavailable", "reason": "timeout"})["reason"] == "soil_texture_unavailable"
    assert topsoil_water(None, LOAM)["reason"] == "soil_moisture_unavailable"
    assert topsoil_water("0.3", LOAM)["status"] == "unavailable"  # malformed upstream value is not coerced


# --- risks -------------------------------------------------------------------------------------

def test_rain_on_wet_soil_means_delay_irrigation():
    """The documented example: rain likely and soil already wet -> delay irrigation, with evidence."""
    c = ctx(moisture=0.30)
    r = risks_by_category(c)["waterlogging"]
    assert r.severity == "moderate" and r.action == "delay_irrigation"
    assert r.drivers == ["rain_expected", "soil_wet"]
    ids = {e.id: e for e in r.evidence}
    assert ids["rain_forecast"].value == 12.0 and ids["rain_forecast"].basis == "forecast"
    assert ids["rain_forecast"].params["probability_pct"] == 80
    assert ids["soil_water_status"].value == "wet" and ids["soil_water_status"].basis == "model_estimate"
    assert r.confidence == "low"  # soil water rests on two models


def test_heavy_rain_is_high_waterlogging_and_the_top_action():
    c = ctx(daily={"precipitation_sum": [0, 80.0, 0, 0, 0, 0, 0]})
    risks = risk_engine.assess(c)
    top = risk_engine.top_action(risks, c)
    assert top.status == "action" and top.action == "clear_drainage" and top.severity == "high"
    assert any(rule.source.startswith("India Meteorological") for rule in risks[0].rules)


def test_dry_spell_on_dry_soil_is_high_water_stress():
    r = risks_by_category(ctx(daily=DRY_WEEK, moisture=0.18))["water_stress"]
    assert r.severity == "high" and r.action == "irrigate_soon"
    assert set(r.drivers) == {"dry_spell_forecast", "soil_dry"}


def test_heat_during_mid_season_is_raised_with_a_cited_reason():
    daily = {**DRY_WEEK, "temperature_2m_max": [41.0] * 7}
    early = risks_by_category(ctx(daily=daily, sowing=date(2026, 9, 16)))["heat_stress"]    # initial stage
    flowering = risks_by_category(ctx(daily=daily, sowing=date(2026, 7, 1)))["heat_stress"]  # mid-season
    assert early.severity == "moderate"
    assert flowering.severity == "high" and "sensitive_stage" in flowering.drivers
    assert any("Hatfield" in rule.source for rule in flowering.rules)


def test_disease_combines_weather_reports_and_farm_history():
    outbreak = {"disease": "Rust", "distance_km": 12, "report_count": 4, "severity": "moderate", "last_report_at": "2026-09-25T10:00:00+00:00"}
    r = risks_by_category(ctx(outbreaks=[outbreak]))["disease"]
    assert r.severity == "high" and set(r.drivers) == {"fungal_weather", "nearby_outbreak"}
    kinds = {e.id: e.basis for e in r.evidence}
    assert kinds["nearby_outbreak"] == "ai_classified_reports"  # never presented as confirmed

    hist = {"recent_diagnoses": [{"status": "disease_detected", "disease": "Rust", "age_days": 3, "date": "2026-09-23", "certainty": "moderate"}]}
    r = risks_by_category(ctx(daily=DRY_WEEK, history=hist))["disease"]
    assert r.severity == "moderate" and r.drivers == ["recent_farm_diagnosis"]
    assert r.evidence[0].basis == "ai_generated"


def test_pest_risk_is_never_invented():
    r = risks_by_category(ctx())["pest"]
    assert r.severity == "unavailable" and r.reason == "no_pest_data_source" and not r.evidence


def test_spray_window_and_harvest_weather():
    c = ctx(wind=20.0, sowing=date(2026, 6, 1))  # day 117: wheat late season
    r = risks_by_category(c)
    assert r["spray_window"].severity == "moderate" and set(r["spray_window"].drivers) == {"wind_high", "rain_soon"}
    assert r["harvest_weather"].severity == "moderate" and r["harvest_weather"].action == "protect_harvest"
    assert risks_by_category(ctx())["harvest_weather"].reason == "crop_stage_unknown"


def test_weather_outage_makes_weather_risks_unavailable_not_low():
    c = ctx(weather_ok=False)
    r = risks_by_category(c)
    for cat in ("waterlogging", "water_stress", "heat_stress", "cold_stress", "spray_window"):
        assert r[cat].severity == "unavailable" and r[cat].reason == "weather_unavailable"
    top = risk_engine.top_action(list(r.values()), c)
    assert top.status == "unavailable" and top.action is None  # no false all-clear


def test_satellite_states():
    assert risks_by_category(ctx())["crop_health"].reason == "not_configured"
    decline = Signal("available", {"status": "available", "ndvi": 0.41, "ndvi_previous": 0.58, "change": -0.17, "latest_image_date": "2026-09-20"})
    r = risks_by_category(ctx(sat=decline))["crop_health"]
    assert r.severity == "moderate" and r.evidence[0].basis == "satellite_observation"
    single = Signal("available", {"status": "available", "ndvi": 0.5, "change": None})
    assert risks_by_category(ctx(sat=single))["crop_health"].reason == "insufficient_history"


def test_malformed_forecast_values_cannot_raise_risks():
    c = ctx(daily={"precipitation_sum": ["900", None, "x", 0, 0, 0, 0], "temperature_2m_max": ["55"] * 7})
    r = risks_by_category(c)
    assert r["waterlogging"].severity == "low" and r["heat_stress"].severity == "low"


def test_quiet_forecast_gives_routine_action():
    c = ctx(daily={**DRY_WEEK, "et0_fao_evapotranspiration": [3.0] * 7}, moisture=0.24, crop=None)
    risks = risk_engine.assess(c)
    top = risk_engine.top_action(risks, c)
    assert top.status == "routine" and top.action == "routine_monitoring"


def test_risks_are_sorted_by_severity_then_actionability():
    risks = risk_engine.assess(ctx(daily={"precipitation_sum": [0, 80.0, 0, 0, 0, 0, 0]}))
    ranks = [risk_engine.SEVERITY_RANK[r.severity] for r in risks]
    assert ranks == sorted(ranks, reverse=True)


def test_every_non_low_risk_is_explained():
    c = ctx(daily={"precipitation_sum": [0, 80.0, 0, 0, 0, 0, 0]}, wind=20.0)
    for r in risk_engine.assess(c):
        if r.severity in ("moderate", "high"):
            assert r.drivers and r.evidence and r.rules and r.action and r.confidence
        if r.severity == "unavailable":
            assert r.reason


def test_assembled_intelligence_reports_data_quality():
    body = assemble(ctx(sowing=date(2026, 7, 1))).model_dump()
    dq = {d["source"]: d for d in body["data_quality"]}
    assert dq["weather"]["status"] == "available" and dq["weather"]["as_of"] == "2026-09-26T10:15"
    assert dq["satellite"]["status"] == "not_configured"
    assert dq["crop_stage"]["status"] == "available"
    assert body["engine"]["ai_used"] is False
    assert body["farm"]["crop_stage"]["stage"] == "mid_season"


# --- endpoint ----------------------------------------------------------------------------------

def _conditions(**daily):
    return ws.parse_conditions(open_meteo_payload(**daily), 18.5, 73.8)


def test_intelligence_endpoint_fuses_sources():
    with patch("services.farm_context.weather_service.get_conditions", AsyncMock(return_value=_conditions())), \
            patch("services.farm_context.soil_service.get_soil", AsyncMock(return_value=LOAM)), \
            patch("services.farm_context.persistence_service.get_outbreaks", AsyncMock(return_value=[])):
        res = client.get("/api/farm/intelligence", params={"lat": 18.5204, "lng": 73.8567, "crop": "wheat", "sowing_date": "2026-07-01"})
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["schema_version"] == "1.0"
    assert body["farm"]["crop"] == "Wheat"
    assert body["farm"]["location"] == {"lat": 18.52, "lng": 73.857}
    assert body["top_action"]["status"] in ("action", "routine")
    assert {r["category"] for r in body["risks"]} >= {"waterlogging", "disease", "pest", "crop_health"}
    assert body["weather"]["provenance"]["source"] == "Open-Meteo"


def test_intelligence_endpoint_when_weather_is_down():
    with patch("services.farm_context.weather_service.get_conditions", AsyncMock(side_effect=ServiceUnavailableException("down"))), \
            patch("services.farm_context.soil_service.get_soil", AsyncMock(return_value={"status": "unavailable", "reason": "timeout"})), \
            patch("services.farm_context.persistence_service.get_outbreaks", AsyncMock(return_value=[])):
        res = client.get("/api/farm/intelligence", params={"lat": 18.5, "lng": 73.8})
    assert res.status_code == 200
    body = res.json()
    assert body["top_action"]["status"] == "unavailable"
    assert body["weather"] is None and body["soil"] is None
    dq = {d["source"]: d for d in body["data_quality"]}
    assert dq["weather"]["status"] == "unavailable" and dq["soil"]["reason"] == "timeout"


def test_intelligence_endpoint_validates_input():
    assert client.get("/api/farm/intelligence", params={"lat": 91, "lng": 0}).status_code == 422
    assert client.get("/api/farm/intelligence", params={"lat": 1, "lng": 1, "sowing_date": "yesterday"}).status_code == 422


def test_radar_water_signal_raises_waterlogging_through_cloud():
    sar = {"status": "available", "orbit_pass": "ASCENDING", "vh_db": -19.5, "vh_db_previous": -15.0, "vh_change_db": -4.5,
           "water_signal": True, "latest_image_date": "2026-09-24"}
    cloudy = Signal("no_data", {"status": "no_data", "reason": "no_suitable_observation", "sar": sar}, reason="no_suitable_observation")
    r = risks_by_category(ctx(daily=DRY_WEEK, sat=cloudy))
    assert r["waterlogging"].severity == "moderate" and r["waterlogging"].drivers[0] == "sar_water_signal"
    assert r["waterlogging"].evidence[0].id == "sar_vh_change" and r["waterlogging"].evidence[0].basis == "satellite_observation"
    assert any("UN-SPIDER" in rule.source for rule in r["waterlogging"].rules)
    assert r["crop_health"].severity == "unavailable"  # radar is not turned into a crop-health score
    dq = {d.source: d for d in assemble(ctx(sat=cloudy)).data_quality}
    assert dq["satellite"].status == "no_data" and dq["radar"].status == "available" and dq["radar"].as_of == "2026-09-24"


def test_ndvi_below_seasonal_baseline():
    base = {"status": "available", "position": "below_range", "min": 0.58, "max": 0.62, "years": [{"ndvi": 0.62}, {"ndvi": 0.58}, {"ndvi": None}]}
    both = Signal("available", {"status": "available", "ndvi": 0.41, "ndvi_previous": 0.58, "change": -0.17, "baseline": base})
    r = risks_by_category(ctx(sat=both))["crop_health"]
    # Change and baseline share the same current Sentinel-2 value: one source, and without a quality summary confidence stays low.
    assert r.severity == "moderate" and r.drivers == ["ndvi_decline", "ndvi_below_baseline"] and r.confidence == "low"
    assert r.independent_sources == 1 and "correlated_signals_counted_once" in r.confidence_basis
    only_baseline = Signal("available", {"status": "available", "ndvi": 0.41, "change": None, "baseline": base})
    r = risks_by_category(ctx(sat=only_baseline))["crop_health"]
    assert r.drivers == ["ndvi_below_baseline"] and r.confidence == "low"
    assert {e.id for e in r.evidence} == {"ndvi_baseline"}

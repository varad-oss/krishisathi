"""Risk level vs evidence confidence: reliability per evidence kind, required vs supporting evidence,
independence groups, and an interpretable top action. No numeric probabilities anywhere."""
import json
from datetime import date

from models.intelligence import Evidence
from services import risk_engine
from services.farm_context import Signal
from services.intelligence_service import assemble
from test_farm_intelligence import DRY_WEEK, ctx, risks_by_category

OUTBREAK = {"disease": "Rust", "distance_km": 12, "report_count": 4, "severity": "moderate", "last_report_at": "2026-09-25T10:00:00+00:00"}
HUMID = {"relative_humidity_2m_mean": [60, 95, 95, 95, 60, 60, 60]}


def test_high_risk_with_low_confidence_when_weather_and_ai_reports_agree():
    """The documented example: humid conditions + nearby AI reports = elevated risk, low evidence confidence."""
    r = risks_by_category(ctx(outbreaks=[OUTBREAK]))["disease"]
    assert r.severity == "high" and r.confidence == "low"
    assert "weakest_required_condition" in r.confidence_basis and "independent_sources_agree" in r.confidence_basis
    assert r.independent_sources == 2
    assert {e.role for e in r.evidence} == {"required"}


def test_nearby_reports_and_own_diagnosis_are_one_source_and_do_not_make_high():
    hist = {"recent_diagnoses": [{"status": "disease_detected", "disease": "Rust", "age_days": 2, "date": "2026-09-24", "certainty": "high"}]}
    r = risks_by_category(ctx(daily=DRY_WEEK, outbreaks=[OUTBREAK], history=hist))["disease"]
    assert set(r.drivers) == {"nearby_outbreak", "recent_farm_diagnosis"}
    assert r.severity == "moderate" and r.confidence == "low" and r.independent_sources == 1
    assert "correlated_signals_counted_once" in r.confidence_basis


def test_low_certainty_diagnosis_never_raises_a_farm_risk():
    hist = {"recent_diagnoses": [{"status": "disease_detected", "disease": "Blight", "age_days": 1, "date": "2026-09-25", "certainty": "low"}]}
    r = risks_by_category(ctx(daily=DRY_WEEK, history=hist))["disease"]
    assert r.severity == "low" and r.action is None
    assert r.evidence[0].id == "recent_diagnosis" and r.evidence[0].role == "context"


def test_distant_or_stale_clusters_are_context_only():
    far = {**OUTBREAK, "distance_km": 70}
    stale = {**OUTBREAK, "last_report_at": "2026-09-10T10:00:00+00:00"}
    for o in (far, stale):
        r = risks_by_category(ctx(daily=DRY_WEEK, outbreaks=[o]))["disease"]
        assert r.severity == "low" and "nearby_outbreak" not in r.drivers and r.evidence[0].role == "context"


def test_forecast_reliability_depends_on_lead_time_and_probability():
    near = risks_by_category(ctx(daily={"precipitation_sum": [0, 80.0, 0, 0, 0, 0, 0]}))["waterlogging"]
    assert near.severity == "high" and near.confidence == "moderate" and "forecast_within_2_days" in near.confidence_basis
    today = date(2026, 9, 26)
    grade = lambda **kw: risk_engine._forecast_reliability(Evidence(id="rain_forecast", basis="forecast", source="weather", **kw), today)
    assert grade(date="2026-09-27", params={"probability_pct": 80}) == ("moderate", "forecast_within_2_days")
    assert grade(date="2026-09-30", params={"probability_pct": 80}) == ("low", "forecast_beyond_2_days")
    assert grade(date="2026-09-27", params={"probability_pct": 30}) == ("low", "forecast_low_probability")
    assert grade(date=None) == ("low", "forecast_beyond_2_days")
    spell = Evidence(id="dry_spell_forecast", basis="forecast", source="weather", date="2026-09-26")
    assert risk_engine._forecast_reliability(spell, today) == ("low", "multi_day_forecast_total")


def test_modelled_soil_water_is_the_weak_link_when_it_is_required():
    r = risks_by_category(ctx(moisture=0.30))["waterlogging"]
    assert r.severity == "moderate" and r.confidence == "low"
    soil = next(e for e in r.evidence if e.id == "soil_water_status")
    assert soil.role == "required" and soil.reliability == "low" and soil.group == "weather_model"
    rain = next(e for e in r.evidence if e.id == "rain_forecast")
    assert rain.group == soil.group  # same weather model: not independent


def test_satellite_confidence_follows_the_quality_summary():
    def sat(level, mode):
        return Signal("available", {"status": "available", "ndvi": 0.41, "ndvi_previous": 0.58, "change": -0.17, "roi": {"mode": mode},
                                    "quality": {"level": level}, "latest_image_date": "2026-09-20"})
    good = risks_by_category(ctx(sat=sat("good", "polygon")))["crop_health"]
    limited = risks_by_category(ctx(sat=sat("limited", "point")))["crop_health"]
    assert good.severity == limited.severity == "moderate"
    assert good.confidence == "moderate" and limited.confidence == "low"
    assert "satellite_quality_limited" in limited.confidence_basis


def test_insufficient_satellite_data_is_unavailable_not_a_score():
    sat = Signal("insufficient_data", {"status": "insufficient_data", "reason": "too_few_clear_pixels"}, reason="too_few_clear_pixels")
    r = risks_by_category(ctx(sat=sat))["crop_health"]
    assert r.severity == "unavailable" and r.reason == "too_few_clear_pixels"
    dq = {d.source: d for d in assemble(ctx(sat=sat)).data_quality}
    assert dq["satellite"].status == "insufficient_data"


def test_every_graded_evidence_has_group_reliability_and_role():
    c = ctx(daily={"precipitation_sum": [0, 80.0, 0, 0, 0, 0, 0], **HUMID}, wind=20.0, outbreaks=[OUTBREAK], sowing=date(2026, 7, 1))
    for r in risk_engine.assess(c):
        for e in r.evidence:
            assert e.group and e.reliability in ("low", "moderate", "high") and e.role in ("required", "supporting", "context")
        if r.severity in ("moderate", "high"):
            assert r.confidence and r.confidence_basis


def test_no_numeric_probabilities_are_introduced():
    body = assemble(ctx(outbreaks=[OUTBREAK])).model_dump()
    for r in body["risks"] + [body["top_action"]]:
        assert r["confidence"] in (None, "low", "moderate", "high")
        assert "probability" not in json.dumps({k: v for k, v in r.items() if k != "evidence"})


def test_top_action_is_complete_and_says_why_it_is_first():
    c = ctx(daily={"precipitation_sum": [0, 80.0, 0, 0, 0, 0, 0]}, wind=20.0)
    top = risk_engine.top_action(risk_engine.assess(c), c)
    assert top.status == "action" and top.action == "clear_drainage"
    assert top.category and top.severity and top.confidence and top.drivers and top.evidence and top.rules and top.date
    assert top.confidence_basis and top.priority_reason == "highest_severity"


def test_top_action_prefers_the_sooner_risk_at_equal_severity():
    # Wind now (spray window, today) vs heavy rain in 4 days would differ in severity; use two moderates instead.
    c = ctx(daily={**DRY_WEEK, "temperature_2m_max": [30, 30, 30, 39.5, 30, 30, 30]}, wind=20.0)
    risks = risk_engine.assess(c)
    top = risk_engine.top_action(risks, c)
    assert top.severity == "moderate" and top.priority_reason in ("soonest", "stronger_evidence", "less_reversible")

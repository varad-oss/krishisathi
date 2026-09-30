"""Early warning: disease signals follow stated rules, thin data is flagged, nothing is estimated."""
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from main import app
from services import early_warning as ew

NOW = datetime(2026, 9, 30, 12, tzinfo=timezone.utc)
client = TestClient(app)


def det(disease="Rust", lat=30.91, lng=75.84, days_ago=1, severity="moderate", crop="Wheat"):
    return {"disease": disease, "crop": crop, "severity": severity, "lat": lat, "lng": lng, "timestamp": NOW - timedelta(days=days_ago)}


def test_signal_needs_three_reports_in_the_current_week():
    out = ew.disease_signals([det(), det()], NOW)
    assert out["signals"] == [] and out["below_threshold"] == 1


def test_new_rising_falling_and_steady_trends():
    assert ew.trend_for(3, 0) == "new" and ew.trend_for(5, 3) == "rising"
    assert ew.trend_for(3, 5) == "falling" and ew.trend_for(4, 4) == "steady"
    out = ew.disease_signals([det()] * 4 + [det(days_ago=10)] * 2, NOW)
    s = out["signals"][0]
    assert (s["observations"], s["observations_previous"], s["trend"]) == (4, 2, "rising")


def test_confidence_is_a_sample_size_rule():
    assert [ew.confidence_for(n) for n in (3, 4, 5, 9, 10)] == ["low", "low", "moderate", "moderate", "high"]


def test_signals_are_reported_at_half_degree_cells_never_farm_coordinates():
    s = ew.disease_signals([det(lat=30.91, lng=75.84)] * 3, NOW)["signals"][0]
    assert s["geography"] == {"kind": "grid_cell", "size_deg": 0.5, "lat": 30.75, "lng": 75.75}
    assert "30.91" not in str(s)


def test_diseases_and_cells_are_kept_apart_and_ordered_by_severity():
    records = [det(disease="Rust", severity="moderate")] * 5 + [det(disease="Blast", severity="high")] * 3 + [det(lat=18.5, lng=73.8)] * 3
    out = ew.disease_signals(records, NOW)
    assert [(s["disease"], s["geography"]["lat"]) for s in out["signals"]] == [("Blast", 30.75), ("Rust", 30.75), ("Rust", 18.75)]


def test_weather_threats_keep_only_watch_and_warning_and_list_unavailable_states():
    risk = {"regions": [
        {"state": "PB", "status": "available", "insights": [
            {"id": "heat_stress", "severity": "watch", "date": "2026-10-02", "params": {"temp": 41}},
            {"id": "rain_expected", "severity": "info", "date": "2026-10-01", "params": {}}]},
        {"state": "WB", "status": "available", "insights": [{"id": "heavy_rain", "severity": "warning", "date": "2026-10-03", "params": {"mm": 80}}]},
        {"state": "TN", "status": "unavailable", "insights": []},
    ], "provenance": {"source": "Open-Meteo"}}
    out = ew.weather_threats(risk)
    assert [(t["state"], t["id"]) for t in out["threats"]] == [("WB", "heavy_rain"), ("PB", "heat_stress")]
    assert out["states_unavailable"] == ["TN"]
    assert out["threats"][0]["geography"]["kind"] == "single_reference_point_per_state"


def test_endpoint_flags_insufficient_data_and_keeps_crop_health_unavailable():
    risk = {"regions": [], "aggregation": "single_reference_point_per_state", "provenance": {"source": "Open-Meteo"}}
    with patch.object(ew.persistence_service, "recent_detections", AsyncMock(return_value=[det()] * 3)), \
         patch.object(ew, "state_weather_risk", AsyncMock(return_value=risk)):
        body = client.get("/api/dashboard/early-warning").json()
    assert body["coverage"] == {"observations_14d": 3, "grid_cells_14d": 1, "cell_deg": 0.5, "insufficient_data": True, "min_observations": 20}
    assert body["crop_health"]["status"] == "unavailable"
    assert body["disease"]["kind"] == "ai_classified_user_reports" and "not_lab_confirmed" in body["disease"]["limitations"]
    assert body["period"]["compared_with"]["end"] == body["period"]["start"]
    assert len(body["disease"]["signals"]) == 1


def test_recent_detections_reads_only_confident_located_detections():
    import asyncio
    from services.persistence_service import persistence_service
    base = {"diagnosis_status": "disease_detected", "certainty": "moderate", "severity": "high", "spread_risk": "low"}
    async def seed():
        await persistence_service.save_diagnosis({**base, "disease_name": "EW-Test-Blight"}, "Rice", 22.1, 88.1, "en")
        await persistence_service.save_diagnosis({**base, "disease_name": "EW-Test-Blight", "certainty": "low"}, "Rice", 22.1, 88.1, "en")
        await persistence_service.save_diagnosis({**base, "disease_name": "EW-Test-Blight"}, "Rice", None, None, "en")
        return await persistence_service.recent_detections(days=14)
    found = [r for r in asyncio.run(seed()) if r["disease"] == "EW-Test-Blight"]
    assert len(found) == 1 and found[0]["severity"] == "high" and found[0]["timestamp"].tzinfo is not None

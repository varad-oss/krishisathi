import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from main import app
from models.interop import RegionalAgriSignal, SignalType, SeverityLevel
from datetime import datetime
import jwt
from config import settings


@pytest.fixture(autouse=True)
def jwt_secret():
    settings.JWT_SECRET = 'testsecret'
    yield


@pytest.mark.asyncio
async def test_removed_fake_report_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/alerts/report", params={"disease": "Rust", "lat": 1.0, "lng": 2.0})
        assert response.status_code in (404, 405)


@pytest.mark.asyncio
async def test_client_cannot_choose_signal_id():
    token = jwt.encode({"sub": "test_sys", "role": "system"}, 'testsecret', algorithm="HS256")
    signal = {"signal_id": "fixed-id", "from_state": "MH", "signal_type": "disease_alert", "severity": "high", "message": "x"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/states/exchange/signals", json=signal, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    assert res.json()["signal_id"] != "fixed-id"


@pytest.mark.asyncio
async def test_federation_targeted_signal_round_trip():
    signal = {
        "from_state": "MH",
        "to_state": "KA",
        "signal_type": "disease_alert",
        "severity": "high",
        "message": "Test signal",
        "metadata": {"test": "data", "farmer_name": "Should Be Stripped"}
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # POST
        token = jwt.encode({"sub": "test_sys", "role": "system"}, 'testsecret', algorithm="HS256")
        post_response = await ac.post("/api/states/exchange/signals", json=signal, headers={"Authorization": f"Bearer {token}"})
        assert post_response.status_code == 201
        
        # GET
        token = jwt.encode({"sub": "test_sys", "role": "system"}, 'testsecret', algorithm="HS256")
        get_response = await ac.get("/api/states/exchange/signals", headers={"Authorization": f"Bearer {token}"})
        assert get_response.status_code == 200
        data = get_response.json()
        assert len(data["signals"]) > 0
        latest = data["signals"][0]
        assert latest["to_state"] == "KA"
        assert latest["metadata"] == {"test": "data"} # farmer_name stripped
        
@pytest.mark.asyncio
async def test_federation_broadcast_signal_round_trip():
    signal = {
        "from_state": "PB",
        "signal_type": "weather_advisory",
        "severity": "info",
        "message": "Broadcast test",
        "metadata": {}
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        token = jwt.encode({"sub": "test_sys", "role": "system"}, 'testsecret', algorithm="HS256")
        post_response = await ac.post("/api/states/exchange/signals", json=signal, headers={"Authorization": f"Bearer {token}"})
        assert post_response.status_code == 201
        
        token = jwt.encode({"sub": "test_sys", "role": "system"}, 'testsecret', algorithm="HS256")
        get_response = await ac.get("/api/states/exchange/signals", headers={"Authorization": f"Bearer {token}"})
        data = get_response.json()
        latest = data["signals"][0]
        assert latest["to_state"] is None
        assert latest["message"] == "Broadcast test"


from unittest.mock import patch, AsyncMock
from services.persistence_service import persistence_service


def _stats(total):
    return {
        "generated_at": "2026-09-26T00:00:00Z", "total_diagnoses": total, "diagnoses_last_7_days": total,
        "diagnoses_previous_7_days": 0, "total_advisories": 0, "active_outbreaks": 0, "disease_distribution": {},
        "crop_distribution_30d": {}, "status_distribution_30d": {}, "daily_diagnoses_30d": [],
        "coverage": {"grid_cells_30d": 0, "grid_size_deg": 0.5}, "provenance": {},
    }


@pytest.mark.asyncio
async def test_dashboard_report_generated_from_real_stats():
    with patch.object(persistence_service, "get_dashboard_stats", AsyncMock(return_value=_stats(12))), \
         patch("services.gemini_service.gemini_service.generate_dashboard_report", AsyncMock(return_value="Mocked report")) as gen:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/dashboard/report?language=hi")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "available"
    assert data["kind"] == "ai_generated_summary"
    report_input = gen.call_args.args[0]
    assert "farmers_reached" not in report_input
    assert report_input["total_diagnoses"] == 12


@pytest.mark.asyncio
async def test_dashboard_report_insufficient_data_skips_ai():
    with patch.object(persistence_service, "get_dashboard_stats", AsyncMock(return_value=_stats(2))), \
         patch("services.gemini_service.gemini_service.generate_dashboard_report", AsyncMock()) as gen:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/dashboard/report")
    assert response.json()["status"] == "insufficient_data"
    gen.assert_not_called()


@pytest.mark.asyncio
async def test_stats_contain_no_fabricated_fields():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    for fabricated in ("farmers_reached", "diagnoses_trend", "languages_served", "recent_activity"):
        assert fabricated not in data
    assert data["total_diagnoses"] >= 0
    assert data["provenance"]["kind"] == "ai_classified_user_reports"


@pytest.mark.asyncio
async def test_states_have_no_invented_statistics():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        states = (await ac.get("/api/states")).json()["states"]
    for s in states:
        assert "farmers_reached" not in s and "active_alerts" not in s and "arable_land_mha" not in s

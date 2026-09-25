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
settings.JWT_SECRET = 'testsecret'

@pytest.mark.asyncio
async def test_report_endpoint_not_implemented():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/alerts/report", params={"disease": "Rust", "lat": 1.0, "lng": 2.0})
        assert response.status_code == 501
        assert response.json()["detail"] == "Feature not implemented yet."

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


from unittest.mock import patch

@pytest.mark.asyncio
@patch("services.gemini_service.gemini_service.generate_dashboard_report", return_value="Mocked report")
async def test_dashboard_report_correctness(mock_generate):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/dashboard/report")
        assert response.status_code == 200
        data = response.json()
        assert "Real-time" in data["period"]
        assert "August" not in data["period"]

@pytest.mark.asyncio
async def test_zero_diagnosis_state():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_diagnoses"] >= 0
        assert data["active_outbreaks"] >= 0

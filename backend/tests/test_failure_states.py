import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from models.exceptions import ServiceUnavailableException
from services.weather_service import weather_service
from services.gemini_service import gemini_service

client = TestClient(app)

@pytest.fixture
def mock_weather_error():
    with patch("services.weather_service.httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = Exception("Network timeout")
        yield mock_get

@pytest.fixture
def mock_gemini_error():
    with patch.object(gemini_service, '_call_with_fallback') as mock_call:
        mock_call.side_effect = ServiceUnavailableException("Diagnostic model is temporarily unavailable.")
        yield mock_call

def test_weather_failure_raises_exception():
    with patch("services.weather_service.httpx.AsyncClient.get", side_effect=Exception("Network Timeout")):
        import asyncio
        with pytest.raises(ServiceUnavailableException):
            asyncio.run(weather_service.get_current_weather(28.0, 77.0))

def test_weather_router_failure(mock_weather_error):
    response = client.get("/api/weather?lat=28.0&lng=77.0")
    assert response.status_code == 503
    assert response.json()["detail"]["error"] == "service_unavailable"
    assert "unavailable" in response.json()["detail"]["message"].lower()

def test_diagnose_gemini_failure(mock_gemini_error):
    with patch.object(weather_service, 'get_current_weather', return_value={"temp": 30, "humidity": 60, "rainfall": 0, "wind": 10, "soil_moisture": 0.3, "description": "Clear sky", "source": "Mock"}):
        response = client.post(
            "/api/diagnose/base64",
            json={
                "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg==",
                "crop_type": "Wheat",
                "latitude": 28.0,
                "longitude": 77.0,
                "language": "en"
            }
        )
        assert response.status_code == 503
        assert response.json()["detail"]["error"] == "service_unavailable"
        assert "unavailable" in response.json()["detail"]["message"].lower()

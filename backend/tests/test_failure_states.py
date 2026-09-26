"""Every upstream failure must surface as an explicit, retryable error, never as synthetic data."""
import asyncio
import base64
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from helpers import jpeg_bytes
from main import app
from models.exceptions import ServiceUnavailableException
from services import weather_service as ws
from services.bigquery_service import bq_service
from services.earth_engine_service import earth_engine_service
from services.gemini_service import gemini_service
from services.weather_service import weather_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_caches():
    ws._cache.clear()
    from core import rate_limit
    rate_limit._local_windows.clear()
    yield
    ws._cache.clear()


def test_weather_failure_raises_exception():
    with patch("services.weather_service.httpx.AsyncClient.get", side_effect=Exception("Network Timeout")):
        with pytest.raises(ServiceUnavailableException):
            asyncio.run(weather_service.get_current_weather(28.0, 77.0))


def test_weather_timeout_has_specific_message():
    with patch("services.weather_service.httpx.AsyncClient.get", side_effect=httpx.ReadTimeout("slow")):
        with pytest.raises(ServiceUnavailableException, match="did not respond in time"):
            asyncio.run(weather_service.get_conditions(28.0, 77.0))


@pytest.mark.parametrize("path", ["/api/weather?lat=28&lng=77", "/api/farm/conditions?lat=28&lng=77", "/api/weather/forecast?lat=28&lng=77"])
def test_weather_endpoints_return_503_envelope(path):
    with patch("services.weather_service.httpx.AsyncClient.get", side_effect=Exception("Network timeout")):
        res = client.get(path)
    assert res.status_code == 503
    error = res.json()["error"]
    assert error["code"] == "SERVICE_UNAVAILABLE"
    assert error["retryable"] is True
    assert "unavailable" in error["message"].lower()
    assert error["request_id"]


def test_diagnose_gemini_failure_is_503_not_a_fake_result():
    with patch.object(gemini_service, "_call", side_effect=ServiceUnavailableException("Diagnostic model is temporarily unavailable.")):
        res = client.post("/api/diagnose/base64", json={"image": base64.b64encode(jpeg_bytes()).decode(), "language": "en"})
    assert res.status_code == 503
    assert res.json()["error"]["code"] == "SERVICE_UNAVAILABLE"


def test_ai_not_configured_is_explicit():
    with patch.object(gemini_service, "client", None):
        res = client.post("/api/diagnose/base64", json={"image": base64.b64encode(jpeg_bytes()).decode(), "language": "en"})
    assert res.status_code == 503
    assert "not configured" in res.json()["error"]["message"]


def test_ai_timeout_becomes_503():
    async def slow(**kwargs):
        await asyncio.sleep(5)

    fake_client = SimpleNamespace(aio=SimpleNamespace(models=SimpleNamespace(generate_content=slow)))
    with patch.object(gemini_service, "client", fake_client), patch("services.gemini_service.settings.AI_TIMEOUT_SECONDS", 0.05):
        res = client.post("/api/diagnose/base64", json={"image": base64.b64encode(jpeg_bytes()).decode(), "language": "en"})
    assert res.status_code == 503
    assert "too long" in res.json()["error"]["message"]


def test_invalid_ai_json_is_rejected():
    fake_response = SimpleNamespace(text='{"disease_name": "Rust", "model_confidence_score": 0.95}')
    with patch.object(gemini_service, "_call", AsyncMock(return_value=fake_response)):
        res = client.post("/api/diagnose/base64", json={"image": base64.b64encode(jpeg_bytes()).decode(), "language": "en"})
    assert res.status_code == 503
    assert "invalid response" in res.json()["error"]["message"]


@pytest.mark.asyncio
async def test_telemetry_failure_does_not_raise():
    with patch.object(bq_service, "client", None), patch("services.bigquery_service.logger.error") as mock_error:
        await bq_service.log_diagnosis({"test": "data"})
        mock_error.assert_called_with("BigQuery client not configured or unavailable. Telemetry data dropped.")


def test_earth_engine_sanitized_error():
    with patch("ee.ImageCollection", side_effect=Exception("Internal EE API key invalid error xyz123")):
        earth_engine_service.initialized = True
        try:
            result = earth_engine_service.calculate_regional_ndvi(None, "2026-01-01", "2026-01-31")
        finally:
            earth_engine_service.initialized = False
    assert result["status"] == "unavailable"
    assert "xyz123" not in result["message"]


def test_crop_health_not_configured_is_unavailable():
    earth_engine_service.initialized = False
    res = client.get("/api/farm/crop-health?lat=18.5&lng=73.8")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "unavailable"
    assert body["reason"] == "not_configured"
    assert "ndvi" not in body


def test_soil_failure_is_unavailable_not_invented():
    from services import soil_service
    soil_service._cache.clear()
    with patch("services.soil_service.httpx.AsyncClient.get", side_effect=Exception("down")):
        res = client.get("/api/farm/soil?lat=18.5&lng=73.8")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "unavailable"
    assert "properties" not in body

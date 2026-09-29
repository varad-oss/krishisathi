"""Server errors must reach the browser as errors, not as CORS failures that look like "no internet"."""
from unittest.mock import AsyncMock, patch

import helpers  # noqa: F401
from fastapi.testclient import TestClient

from main import app

client = TestClient(app, raise_server_exceptions=False)
ORIGIN = {"Origin": "https://ai-krishisathi.vercel.app"}


def test_unhandled_500_carries_cors_headers_and_envelope():
    with patch("main.ensure_tables", AsyncMock(side_effect=RuntimeError("db exploded"))):
        res = client.get("/api/kvk/nearest?lat=18.5&lng=73.8", headers=ORIGIN)
    assert res.status_code == 500
    assert res.headers["access-control-allow-origin"] == ORIGIN["Origin"]
    assert res.json()["error"]["code"] == "INTERNAL_ERROR"
    assert "db exploded" not in res.text
    assert res.headers.get("x-request-id")


def test_handled_503_carries_cors_headers():
    with patch("routers.farm.weather_service.get_conditions", AsyncMock(side_effect=__import__("models.exceptions", fromlist=["x"]).ServiceUnavailableException("down"))):
        res = client.get("/api/farm/conditions?lat=18.5&lng=73.8", headers=ORIGIN)
    assert res.status_code == 503
    assert res.headers["access-control-allow-origin"] == ORIGIN["Origin"]
    assert res.json()["error"]["retryable"] is True


def test_unknown_origin_gets_no_cors_grant():
    res = client.get("/health/live", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in res.headers


def test_preflight_allowed_for_frontend():
    res = client.options(
        "/api/advisory/tts",
        headers={**ORIGIN, "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "content-type"},
    )
    assert res.status_code == 200
    assert res.headers["access-control-allow-origin"] == ORIGIN["Origin"]

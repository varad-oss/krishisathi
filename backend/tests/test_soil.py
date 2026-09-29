"""SoilGrids integration: each failure mode is reported with its own reason, never with invented values."""
import asyncio
from unittest.mock import patch

import helpers  # noqa: F401
import httpx
import pytest
from fastapi.testclient import TestClient

from main import app
from services import soil_service as soil_module
from services.soil_service import soil_service

client = TestClient(app)
URL = soil_module.BASE_URL

SOILGRIDS = {
    "properties": {
        "layers": [
            {"name": "phh2o", "unit_measure": {"d_factor": 10}, "depths": [{"label": "0-5cm", "values": {"mean": 72}}, {"label": "5-15cm", "values": {"mean": 74}}]},
            {"name": "soc", "unit_measure": {"d_factor": 10}, "depths": [{"label": "0-5cm", "values": {"mean": 80}}, {"label": "5-15cm", "values": {"mean": 60}}]},
        ]
    }
}
EMPTY = {"properties": {"layers": [{"name": "phh2o", "unit_measure": {"d_factor": 10}, "depths": [{"label": "0-5cm", "values": {"mean": None}}]}]}}


def resp(status: int, json_body=None, text: str | None = None):
    request = httpx.Request("GET", URL)
    if json_body is not None:
        return httpx.Response(status, json=json_body, request=request)
    return httpx.Response(status, text=text or "", request=request)


@pytest.fixture(autouse=True)
def reset(monkeypatch):
    soil_module._cache.clear()
    soil_module._inflight.clear()
    monkeypatch.setattr(soil_module, "RETRY_DELAY_SECONDS", 0)
    yield
    soil_module._cache.clear()


def get(lat=18.61, lng=73.95):
    return asyncio.run(soil_service.get_soil(lat, lng))


def test_success_returns_properties_with_provenance_and_is_cached():
    with patch("services.soil_service.httpx.AsyncClient.get", return_value=resp(200, SOILGRIDS)) as call:
        first = get()
        second = get()
    assert first["status"] == "available"
    assert first["properties"]["ph"] == 7.33
    assert first["provenance"]["retrieved_at"]
    assert second == first and call.call_count == 1


def test_query_uses_lon_lat_order_expected_by_soilgrids():
    with patch("services.soil_service.httpx.AsyncClient.get", return_value=resp(200, SOILGRIDS)) as call:
        get(18.61, 73.95)
    params = dict(p for p in call.call_args.kwargs["params"] if p[0] in ("lat", "lon"))
    assert params == {"lat": 18.61, "lon": 73.95}


def test_no_prediction_at_point_is_no_coverage():
    with patch("services.soil_service.httpx.AsyncClient.get", return_value=resp(200, EMPTY)):
        body = get()
    assert body["status"] == "no_data" and body["reason"] == "no_coverage"
    assert "properties" not in body


def test_rate_limit_is_reported_and_briefly_cached():
    with patch("services.soil_service.httpx.AsyncClient.get", return_value=resp(429, text="Too Many Requests")) as call:
        first = get()
        second = get()
    assert first["status"] == "unavailable" and first["reason"] == "rate_limited" and first["retryable"]
    assert second["reason"] == "rate_limited" and call.call_count == 1  # not hammering the fair-use limit


def test_server_error_is_retried_once_then_reported():
    with patch("services.soil_service.httpx.AsyncClient.get", side_effect=[resp(503, text="down"), resp(200, SOILGRIDS)]) as call:
        body = get()
    assert body["status"] == "available" and call.call_count == 2

    soil_module._cache.clear()
    with patch("services.soil_service.httpx.AsyncClient.get", return_value=resp(502, text="bad gateway")):
        body = get()
    assert body["status"] == "unavailable" and body["reason"] == "upstream_error"


def test_failures_are_not_cached():
    with patch("services.soil_service.httpx.AsyncClient.get", return_value=resp(502, text="x")):
        get()
    with patch("services.soil_service.httpx.AsyncClient.get", return_value=resp(200, SOILGRIDS)):
        assert get()["status"] == "available"


def test_timeout_reason():
    with patch("services.soil_service.httpx.AsyncClient.get", side_effect=httpx.ReadTimeout("slow")):
        body = get()
    assert body["reason"] == "timeout" and body["retryable"]


def test_network_error_reason():
    with patch("services.soil_service.httpx.AsyncClient.get", side_effect=httpx.ConnectError("dns")):
        assert get()["reason"] == "network_error"


def test_malformed_response_reason():
    with patch("services.soil_service.httpx.AsyncClient.get", return_value=resp(200, text="<html>maintenance</html>")):
        body = get()
    assert body["reason"] == "bad_response"
    with patch("services.soil_service.httpx.AsyncClient.get", return_value=resp(200, {"properties": "oops"})):
        soil_module._cache.clear()
        assert get()["reason"] == "bad_response"


def test_rejected_query_is_not_retryable():
    with patch("services.soil_service.httpx.AsyncClient.get", return_value=resp(400, text="bad coordinates")):
        body = get()
    assert body["reason"] == "request_rejected" and body["retryable"] is False


def test_concurrent_requests_share_one_upstream_call():
    async def slow(*args, **kwargs):
        await asyncio.sleep(0.05)
        return resp(200, SOILGRIDS)

    async def many():
        return await asyncio.gather(*(soil_service.get_soil(18.61, 73.95) for _ in range(5)))

    with patch("services.soil_service.httpx.AsyncClient.get", side_effect=slow) as call:
        results = asyncio.run(many())
    assert call.call_count == 1
    assert all(r["status"] == "available" for r in results)


def test_endpoint_exposes_reason():
    with patch("services.soil_service.httpx.AsyncClient.get", return_value=resp(429, text="")):
        body = client.get("/api/farm/soil?lat=18.7&lng=73.7").json()
    assert body == {**body, "status": "unavailable", "reason": "rate_limited"}

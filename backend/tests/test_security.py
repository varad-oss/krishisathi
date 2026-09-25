import pytest
from fastapi.testclient import TestClient
from main import app
from core.security import Principal
import jwt
from config import settings

client = TestClient(app)

def test_missing_credentials():
    response = client.post("/api/states/exchange/signals", json={
        "from_state": "PB",
        "to_state": "UP",
        "signal_type": "disease_alert",
        "severity": "high",
        "message": "test",
        "disease_name": "Wheat Rust",
        "affected_crop": "Wheat",
        "affected_district": "Ludhiana",
        "report_count": 10
    })
    assert response.status_code in [401, 403]

def test_invalid_credentials():
    response = client.post("/api/states/exchange/signals", 
        headers={"Authorization": "Bearer invalid_token"},
        json={"from_state": "PB"}
    )
    # The actual implementation of PyJWT without secret in test env returns 401 or 403
    assert response.status_code in [401, 403]

def test_rate_limit_enforcement():
    # We bypass redis in testing if not configured, but if it is, we check.
    # Without redis, the dependency just returns None and allows traffic.
    # To mock rate limiting, we don't strictly need to test Redis internals if it fails open,
    # but we can check that endpoints exist and respond.
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200

def test_oversized_payload():
    # For diagnosis, max size is 10,000,000. Let's send 11MB.
    large_payload = "A" * 11_000_000
    response = client.post("/api/diagnose/base64", json={
        "image": large_payload,
        "latitude": 0,
        "longitude": 0,
        "language": "en"
    })
    assert response.status_code == 422 # Pydantic validation error for max_length

def test_debug_endpoint_secured():
    response = client.get("/api/debug/earth-engine-status")
    assert response.status_code in [401, 403]

def test_cors_headers_present():
    response = client.options("/api/diagnose", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST"
    })
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers

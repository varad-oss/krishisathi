import base64
import time
from unittest.mock import patch

import jwt
import pytest
from fastapi.testclient import TestClient

from helpers import jpeg_bytes
from config import settings
from main import app
from models.exceptions import ServiceUnavailableException
from services.gemini_service import gemini_service

client = TestClient(app)


def create_token(sub="user1", role="system", exp_delta=3600, secret="testsecret"):
    payload = {"sub": sub, "role": role, "exp": int(time.time()) + exp_delta}
    return jwt.encode(payload, secret, algorithm="HS256")


def err(res):
    return res.json()["error"]


@pytest.fixture(autouse=True)
def setup_env():
    settings.JWT_SECRET = "testsecret"
    settings.ENVIRONMENT = "development"
    settings.TRUST_REVERSE_PROXY = False
    from core import rate_limit
    rate_limit._local_windows.clear()
    yield
    rate_limit._local_windows.clear()


@pytest.fixture
def ai_down():
    with patch.object(gemini_service, "_call", side_effect=ServiceUnavailableException("Diagnostic model is temporarily unavailable.")):
        yield


def image_payload():
    return {"image": base64.b64encode(jpeg_bytes()).decode(), "language": "en"}


# --- Authentication -------------------------------------------------------------

def test_missing_token():
    res = client.get("/api/debug/earth-engine-status")
    assert res.status_code == 401
    assert err(res)["code"] == "UNAUTHORIZED"


def test_malformed_token():
    res = client.get("/api/debug/earth-engine-status", headers={"Authorization": "Bearer not.a.token"})
    assert res.status_code == 401
    assert err(res)["message"] == "Invalid token."


def test_expired_token():
    res = client.get("/api/debug/earth-engine-status", headers={"Authorization": f"Bearer {create_token(exp_delta=-100)}"})
    assert res.status_code == 401
    assert err(res)["code"] == "TOKEN_EXPIRED"


def test_wrong_signature():
    res = client.get("/api/debug/earth-engine-status", headers={"Authorization": f"Bearer {create_token(secret='wrongsecret')}"})
    assert res.status_code == 401


def test_missing_sub():
    token = jwt.encode({"role": "system", "exp": int(time.time()) + 3600}, "testsecret", algorithm="HS256")
    res = client.get("/api/debug/earth-engine-status", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401
    assert "missing subject" in err(res)["message"].lower()


def test_user_role_denied():
    res = client.get("/api/debug/earth-engine-status", headers={"Authorization": f"Bearer {create_token(role='user')}"})
    assert res.status_code == 403
    assert "insufficient privileges" in err(res)["message"]


def test_system_and_admin_roles_allowed():
    for role in ("system", "admin"):
        res = client.get("/api/debug/earth-engine-status", headers={"Authorization": f"Bearer {create_token(role=role)}"})
        assert res.status_code == 200


def test_auth_fails_closed_without_secret():
    """Regression: without JWT_SECRET any token (incl. the old hardcoded demo token) used to be accepted."""
    settings.JWT_SECRET = None
    for token in ("mock-system-token-123", create_token()):
        res = client.post(
            "/api/states/exchange/signals",
            headers={"Authorization": f"Bearer {token}"},
            json={"from_state": "MH", "signal_type": "disease_alert", "severity": "high", "message": "x"},
        )
        assert res.status_code == 503
        assert err(res)["code"] == "AUTH_NOT_CONFIGURED"


def test_debug_db_endpoint_removed():
    assert client.get("/api/debug/db").status_code in (401, 404)


# --- Input validation -----------------------------------------------------------

def test_malformed_base64():
    res = client.post("/api/diagnose/base64", json={"image": "not_base64_%&*", "language": "en"})
    assert res.status_code == 422
    assert err(res)["code"] == "INVALID_INPUT"
    assert "Invalid base64" in str(res.json())


def test_oversized_encoded_payload():
    res = client.post("/api/diagnose/base64", json={"image": "A" * 11_000_000, "language": "en"})
    assert res.status_code == 422


def test_oversized_decoded_payload():
    b64 = base64.b64encode(b"0" * (5 * 1024 * 1024 + 10)).decode("utf-8")
    res = client.post("/api/diagnose/base64", json={"image": b64, "language": "en"})
    assert res.status_code == 422
    assert "exceeds" in str(res.json())


def test_non_image_bytes_rejected_even_with_image_content_type():
    res = client.post("/api/diagnose", data={"language": "en"}, files={"file": ("x.jpg", b"not an image at all", "image/jpeg")})
    assert res.status_code == 415
    assert err(res)["code"] == "UNSUPPORTED_MEDIA_TYPE"


def test_unsupported_language_rejected():
    res = client.post("/api/diagnose/base64", json={**image_payload(), "language": "xx"})
    assert res.status_code == 422


def test_out_of_range_coordinates_rejected():
    assert client.get("/api/farm/conditions?lat=200&lng=10").status_code == 422
    assert client.get("/api/kvk/nearest?lat=10&lng=-500").status_code == 422


def test_oversized_multipart():
    res = client.post("/api/diagnose", data={"language": "en"}, files={"file": ("test.jpg", b"0" * (5 * 1024 * 1024 + 10), "image/jpeg")})
    assert res.status_code == 413


def test_tts_text_length_limited():
    res = client.get("/api/advisory/tts", params={"text": "a" * 2000, "lang": "hi"})
    assert res.status_code == 422


# --- Rate limiting --------------------------------------------------------------

class MockRedis:
    def __init__(self):
        self.data = {}

    async def incr(self, key):
        self.data[key] = self.data.get(key, 0) + 1
        return self.data[key]

    async def expire(self, key, seconds):
        pass


def test_rate_limiting_flow(ai_down):
    mock_redis = MockRedis()
    with patch("core.rate_limit.redis_client", mock_redis), patch("core.rate_limit.time.time", return_value=1000000.0):
        for _ in range(settings.RATE_LIMIT_AI):
            # 503 from the (mocked) model means the request passed the limiter
            assert client.post("/api/diagnose/base64", json=image_payload()).status_code == 503
        res = client.post("/api/diagnose/base64", json=image_payload())
        assert res.status_code == 429
        assert err(res)["code"] == "RATE_LIMITED"
        assert err(res)["retryable"] is True
        assert "Retry-After" in res.headers


def test_rate_limit_falls_back_to_in_process_without_redis(ai_down):
    """Regression: without Redis the limiter used to be silently disabled."""
    with patch("core.rate_limit.redis_client", None), patch("core.rate_limit.time.time", return_value=2000000.0):
        codes = [client.post("/api/diagnose/base64", json=image_payload()).status_code for _ in range(settings.RATE_LIMIT_AI + 1)]
    assert codes[:-1] == [503] * settings.RATE_LIMIT_AI
    assert codes[-1] == 429


def test_trusted_proxy(ai_down):
    mock_redis = MockRedis()
    with patch("core.rate_limit.redis_client", mock_redis):
        client.post("/api/diagnose/base64", headers={"X-Forwarded-For": "9.9.9.9"}, json=image_payload())
        assert not any("9.9.9.9" in k for k in mock_redis.data)

        mock_redis.data = {}
        settings.TRUST_REVERSE_PROXY = True
        client.post("/api/diagnose/base64", headers={"X-Forwarded-For": "9.9.9.9"}, json=image_payload())
        assert any("9.9.9.9" in k for k in mock_redis.data)


# --- Audio ----------------------------------------------------------------------

def test_invalid_audio_mime():
    res = client.post("/api/advisory/voice", json={"audio_base64": base64.b64encode(b"randombinarydata").decode(), "latitude": 0, "longitude": 0, "language": "en"})
    assert res.status_code == 415
    assert err(res)["message"] == "Unsupported audio format"


def test_valid_audio_webm_reaches_transcription():
    webm = base64.b64encode(bytes([0x1A, 0x45, 0xdf, 0xa3, 0x61, 0x62, 0x63])).decode()
    with patch.object(gemini_service, "client", None):
        res = client.post("/api/advisory/voice", json={"audio_base64": webm, "latitude": 0, "longitude": 0, "language": "en"})
    assert res.status_code == 503


# --- Transport security ---------------------------------------------------------

def test_debug_endpoint_truthful():
    res = client.get("/api/debug/earth-engine-status", headers={"Authorization": f"Bearer {create_token()}"})
    data = res.json()
    assert "earth_engine_library_installed" in data
    assert "demo_ndvi_score" not in data


def test_cors_allows_configured_origin():
    res = client.options("/api/diagnose", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"})
    assert res.status_code == 200
    assert res.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_cors_rejects_unknown_origin():
    """Regression: allow_origins used to include '*' together with credentials."""
    res = client.options("/api/diagnose", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"})
    assert res.headers.get("access-control-allow-origin") != "https://evil.example"
    res = client.get("/health/live", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in res.headers


def test_security_headers_and_request_id():
    res = client.get("/health/live", headers={"X-Request-ID": "abc-123"})
    assert res.headers["x-request-id"] == "abc-123"
    assert res.headers["x-content-type-options"] == "nosniff"
    assert res.headers["x-frame-options"] == "DENY"


def test_malicious_request_id_is_replaced():
    res = client.get("/health/live", headers={"X-Request-ID": "bad\nvalue with spaces" * 5})
    assert res.headers["x-request-id"] != "bad\nvalue with spaces" * 5
    assert len(res.headers["x-request-id"]) == 32


def test_unhandled_errors_do_not_leak_details():
    with patch("services.persistence_service.persistence_service.get_dashboard_stats", side_effect=RuntimeError("secret-dsn://user:pw@host")):
        res = TestClient(app, raise_server_exceptions=False).get("/api/dashboard/stats")
    assert res.status_code == 500
    body = res.json()
    assert body["error"]["code"] == "INTERNAL_ERROR"
    assert "secret" not in res.text
    assert body["error"]["request_id"] == res.headers["x-request-id"]

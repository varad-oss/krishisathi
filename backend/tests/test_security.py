import pytest
from fastapi.testclient import TestClient
from main import app
from core.security import Principal
import jwt
import time
import base64
from config import settings
from unittest.mock import patch, AsyncMock
import datetime

client = TestClient(app)

# Helper for tokens
def create_token(sub="user1", role="system", exp_delta=3600, secret="testsecret"):
    payload = {"sub": sub, "role": role, "exp": int(time.time()) + exp_delta}
    return jwt.encode(payload, secret, algorithm="HS256")

@pytest.fixture(autouse=True)
def setup_env():
    settings.JWT_SECRET = "testsecret"
    settings.ENVIRONMENT = "development"
    settings.TRUST_REVERSE_PROXY = False
    yield

# Authentication Tests
def test_missing_token():
    res = client.get("/api/debug/earth-engine-status")
    assert res.status_code in [401, 403]

def test_malformed_token():
    res = client.get("/api/debug/earth-engine-status", headers={"Authorization": "Bearer not.a.token"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid token"

def test_expired_token():
    token = create_token(exp_delta=-100)
    res = client.get("/api/debug/earth-engine-status", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401
    assert "expired" in res.json()["detail"].lower()

def test_wrong_signature():
    token = create_token(secret="wrongsecret")
    res = client.get("/api/debug/earth-engine-status", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid token"

def test_missing_sub():
    payload = {"role": "system", "exp": int(time.time()) + 3600}
    token = jwt.encode(payload, "testsecret", algorithm="HS256")
    res = client.get("/api/debug/earth-engine-status", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401
    assert "missing subject" in res.json()["detail"].lower()

# Authorization Tests
def test_user_role_denied():
    token = create_token(role="user")
    res = client.get("/api/debug/earth-engine-status", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
    assert "Insufficient privileges" in res.json()["detail"]

def test_system_role_allowed():
    token = create_token(role="system")
    res = client.get("/api/debug/earth-engine-status", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200

def test_admin_role_allowed():
    token = create_token(role="admin")
    res = client.get("/api/debug/earth-engine-status", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200

# Input / Base64 Tests
def test_malformed_base64():
    res = client.post("/api/diagnose/base64", json={
        "image": "not_base64_%&*", "latitude": 0, "longitude": 0, "language": "en"
    })
    assert res.status_code == 422
    assert "Invalid base64" in str(res.json())

def test_oversized_encoded_payload():
    large_payload = "A" * 11_000_000
    res = client.post("/api/diagnose/base64", json={
        "image": large_payload, "latitude": 0, "longitude": 0, "language": "en"
    })
    assert res.status_code == 422
    assert "String should have at most" in str(res.json())

def test_oversized_decoded_payload():
    # 5MB + 1 byte limit.
    # 6MB of zeros -> base64
    zeros = b"0" * (5 * 1024 * 1024 + 10)
    b64 = base64.b64encode(zeros).decode("utf-8")
    res = client.post("/api/diagnose/base64", json={
        "image": b64, "latitude": 0, "longitude": 0, "language": "en"
    })
    assert res.status_code == 422
    assert "exceeds" in str(res.json())

# Rate limiting
class MockRedis:
    def __init__(self):
        self.data = {}
    async def incr(self, key):
        self.data[key] = self.data.get(key, 0) + 1
        return self.data[key]
    async def expire(self, key, seconds):
        pass

@pytest.mark.asyncio
async def test_rate_limiting_flow():
    mock_redis = MockRedis()
    with patch("core.rate_limit.redis_client", mock_redis), patch("core.rate_limit.time.time", return_value=1000000.0):
        # We simulate 10 requests allowed
        for _ in range(10):
            res = client.post("/api/diagnose/base64", json={
                "image": "aGVsbG8=", "latitude": 0, "longitude": 0, "language": "en"
            })
            # It will fail with 503 because weather service mock is not set, 
            # but that means it PASSED rate limiting
            assert res.status_code == 503 
        
        # 11th should be 429
        res = client.post("/api/diagnose/base64", json={
            "image": "aGVsbG8=", "latitude": 0, "longitude": 0, "language": "en"
        })
        assert res.status_code == 429
        assert "Retry-After" in res.headers

def test_redis_failure_dev():
    with patch("core.rate_limit.redis_client", None):
        res = client.post("/api/diagnose/base64", json={"image": "aGVsbG8=", "latitude": 0, "longitude": 0, "language": "en"})
        # Fails open -> hits weather service -> 503
        assert res.status_code == 503

def test_redis_failure_prod():
    settings.ENVIRONMENT = "production"
    with patch("core.rate_limit.redis_client", None):
        res = client.post("/api/diagnose/base64", json={"image": "aGVsbG8=", "latitude": 0, "longitude": 0, "language": "en"})
        assert res.status_code == 503
        assert res.json()["detail"] == "Rate limiting service unavailable"
    settings.ENVIRONMENT = "development"

# Proxy Trust
@pytest.mark.asyncio
async def test_trusted_proxy():
    mock_redis = MockRedis()
    with patch("core.rate_limit.redis_client", mock_redis):
        # Without proxy trust
        client.post("/api/diagnose/base64", headers={"X-Forwarded-For": "9.9.9.9"}, json={"image": "aGVsbG8=", "latitude": 0, "longitude": 0, "language": "en"})
        assert any("testclient" in k or "unknown" in k for k in mock_redis.data.keys())
        
        # With proxy trust
        mock_redis.data = {}
        settings.TRUST_REVERSE_PROXY = True
        client.post("/api/diagnose/base64", headers={"X-Forwarded-For": "9.9.9.9"}, json={"image": "aGVsbG8=", "latitude": 0, "longitude": 0, "language": "en"})
        assert any("9.9.9.9" in k for k in mock_redis.data.keys())
        settings.TRUST_REVERSE_PROXY = False

# Upload Limits & Audio
def test_oversized_multipart():
    large_file = b"0" * (5 * 1024 * 1024 + 10)
    res = client.post("/api/diagnose", data={"latitude": 0, "longitude": 0, "language": "en"}, files={"file": ("test.jpg", large_file, "image/jpeg")})
    assert res.status_code == 413

def test_invalid_audio_mime():
    res = client.post("/api/advisory/voice", json={"audio_base64": base64.b64encode(b"randombinarydata").decode(), "latitude": 0, "longitude": 0, "language": "en"})
    assert res.status_code == 415
    assert "Unsupported audio format" in res.json()["detail"]

def test_valid_audio_webm():
    # webm magic bytes
    res = client.post("/api/advisory/voice", json={"audio_base64": base64.b64encode(bytes([0x1A, 0x45, 0xdf, 0xa3, 0x61, 0x62, 0x63])).decode(), "latitude": 0, "longitude": 0, "language": "en"})
    # Fails further down (503 transcription service unavailable) but NOT 415
    assert res.status_code == 503

def test_debug_endpoint_truthful():
    token = create_token(role="system")
    res = client.get("/api/debug/earth-engine-status", headers={"Authorization": f"Bearer {token}"})
    data = res.json()
    assert "earth_engine_library_installed" in data
    assert "demo_ndvi_score" not in data # NO FAKE DATA

def test_cors_contract():
    res = client.options("/api/diagnose", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"})
    assert res.status_code == 200
    assert "access-control-allow-origin" in res.headers

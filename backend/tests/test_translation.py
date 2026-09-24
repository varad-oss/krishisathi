import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from services.translation import translation_service
from services.weather_service import weather_service
from models.exceptions import TranslationServiceUnavailable

client = TestClient(app)

def test_translation_success():
    # If same language, it just returns
    assert translation_service.translate_text("Hello", "en", "en") == "Hello"

def test_translation_failure_raises_exception():
    old_enabled = translation_service.enabled
    translation_service.enabled = False
    
    with pytest.raises(TranslationServiceUnavailable) as exc:
        translation_service.translate_text("Hello", "en", "hi")
    
    assert "temporarily unavailable" in str(exc.value)
    translation_service.enabled = old_enabled

def test_translation_api_failure_becomes_503():
    with patch.object(translation_service, 'translate_text', side_effect=TranslationServiceUnavailable("Translation failed")):
        with patch.object(weather_service, 'get_current_weather', return_value={"temp": 30}):
            response = client.post(
                "/api/advisory",
                json={
                    "query": "What to do about yellow leaves?",
                    "crop_type": "Tomato",
                    "latitude": 28.0,
                    "longitude": 77.0,
                    "language": "hi" # Hindi forces translation
                }
            )
            assert response.status_code == 503
            assert response.json()["detail"]["error"] == "service_unavailable"
            assert "translation" in response.json()["detail"]["message"].lower()


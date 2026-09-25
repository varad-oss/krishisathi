import pytest
import asyncio
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app
from models.exceptions import ServiceUnavailableException
from services.bigquery_service import bq_service
from services.earth_engine_service import earth_engine_service

client = TestClient(app)

@pytest.mark.asyncio
async def test_agent_failure_returns_503():
    with patch('services.agent_service.agent_service.process_advisory') as mock_process:
        mock_process.side_effect = Exception("Agent completely down")
        
        # Advisory requires weather context, so let's mock weather_service
        with patch('services.weather_service.weather_service.get_current_weather') as mock_weather:
            mock_weather.return_value = {"temp": 20}
            
            response = client.post("/api/advisory", json={
                "query": "My crops are dying",
                "latitude": 28.0,
                "longitude": 77.0,
                "crop_type": "Wheat",
                "language": "en"
            })
            
            assert response.status_code == 503
            assert response.json()["detail"]["error"] == "service_unavailable"
            assert "Advisory agent service is temporarily unavailable" in response.json()["detail"]["message"]

@pytest.mark.asyncio
async def test_telemetry_failure_no_local_persistence(tmp_path):
    with patch.object(bq_service, 'client', None):
        with patch('services.bigquery_service.logger.error') as mock_error:
            # Should not raise exception, just log and return
            await bq_service.log_diagnosis({"test": "data"})
            
            mock_error.assert_called_with("BigQuery client not configured or unavailable. Telemetry data dropped.")

def test_earth_engine_sanitized_error():
    with patch('ee.ImageCollection') as mock_collection:
        mock_collection.side_effect = Exception("Internal EE API key invalid error xyz123")
        earth_engine_service.initialized = True
        
        result = earth_engine_service.calculate_regional_ndvi(None, "2026-01-01", "2026-01-31")
        assert result["status"] == "unavailable"
        assert result["message"] == "Earth Engine data is temporarily unavailable."
        assert "xyz123" not in result["message"]

@pytest.mark.asyncio
async def test_non_english_diagnosis_schema_valid():
    # Mock gemini to return english response with canonical enums
    with patch('services.gemini_service.gemini_service.diagnose_crop_disease') as mock_diagnose:
        mock_diagnose.return_value = {
            "disease_name": "Wheat Rust",
            "scientific_name": "Puccinia triticina",
            "model_confidence_score": 0.95,
            "affected_part": "Leaves",
            "severity": "High",
            "spread_risk": "High",
            "image_analysis_summary": "Bad rust",
            "treatment": {
                "chemical": ["Use fungicide"],
                "organic": ["Use neem oil"],
                "preventive": ["Crop rotation"]
            },
            "advisory_text": "Apply immediately"
        }
        
        with patch('services.weather_service.weather_service.get_current_weather') as mock_weather:
            mock_weather.return_value = {"temp": 20}
            
            with patch('services.translation.translation_service.translate_text') as mock_translate:
                # Mock translation service to translate human text to hindi, returning json
                mock_translate.return_value = '{"disease_name": "गेहूं का रतुआ", "affected_part": "पत्ते", "image_analysis_summary": "खराब रतुआ", "treatment": {"chemical": ["कवकनाशी का प्रयोग करें"], "organic": ["नीम का तेल"], "preventive": ["फसल चक्र"]}, "advisory_text": "तुरंत लागू करें"}'
                
                # Mock BigQuery to not fail the test
                with patch.object(bq_service, 'client', None):
                    
                    response = client.post("/api/diagnose/base64", json={
                        "image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
                        "latitude": 28.0,
                        "longitude": 77.0,
                        "crop_type": "Wheat",
                        "language": "hi"
                    })
                    
                    assert response.status_code == 200
                    data = response.json()
                    # Enums MUST remain High, High
                    assert data["severity"] == "High"
                    assert data["spread_risk"] == "High"
                    # User text must be translated
                    assert data["disease_name"] == "गेहूं का रतुआ"

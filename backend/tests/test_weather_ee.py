import pytest
import asyncio
from models.exceptions import ServiceUnavailableException
from services.weather_service import weather_service
from services.earth_engine_service import earth_engine_service
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_weather_raises_503_on_missing_fields():
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Missing 'temperature' in current_weather
        mock_response.json.return_value = {
            "current_weather": {"windspeed": 10},
            "hourly": {"relative_humidity_2m": [50], "precipitation": [0], "soil_moisture_0_to_7cm": [0.2]}
        }
        mock_get.return_value = mock_response

        with pytest.raises(ServiceUnavailableException) as exc:
            await weather_service.get_current_weather(10.0, 20.0)
        assert "Incomplete" in str(exc.value)

def test_earth_engine_fallback_status():
    # Should return status: unavailable when not initialized
    earth_engine_service.initialized = False
    result = earth_engine_service.calculate_regional_ndvi(None, "2026-01-01", "2026-01-31")
    assert isinstance(result, dict)
    assert result["status"] == "unavailable"
    assert "source" in result

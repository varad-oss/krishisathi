"""Weather conditions from the Open-Meteo forecast API.

Open-Meteo "current" values are model estimates at 15-minute resolution, not
station observations; the provenance block says so explicitly so the UI never
presents them as measured facts.
"""
import logging
import time
from datetime import datetime, timezone

import httpx

from config import settings
from models.exceptions import ServiceUnavailableException

logger = logging.getLogger(__name__)

BASE_URL = "https://api.open-meteo.com/v1/forecast"
CURRENT_VARS = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "weather_code",
    "wind_speed_10m",
    "soil_moisture_0_to_1cm",
    "soil_moisture_3_to_9cm",
]
DAILY_VARS = [
    "weather_code",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "precipitation_probability_max",
    "et0_fao_evapotranspiration",
    "relative_humidity_2m_mean",
    "wind_speed_10m_max",
]
FORECAST_DAYS = 7
CACHE_TTL_SECONDS = 600

PROVENANCE_BASE = {
    "source": "Open-Meteo",
    "source_url": "https://open-meteo.com/",
    "kind": "model",
    "notes": "Current values are numerical weather model estimates (15-minute resolution), not ground-station observations. Daily values are forecasts.",
}

# WMO weather interpretation codes (as documented by Open-Meteo)
_WMO = {
    0: "clear", 1: "mainly_clear", 2: "partly_cloudy", 3: "overcast",
    45: "fog", 48: "fog",
    51: "drizzle", 53: "drizzle", 55: "drizzle", 56: "drizzle", 57: "drizzle",
    61: "rain", 63: "rain", 65: "heavy_rain", 66: "rain", 67: "heavy_rain",
    71: "snow", 73: "snow", 75: "snow", 77: "snow",
    80: "rain_showers", 81: "rain_showers", 82: "heavy_rain",
    85: "snow", 86: "snow",
    95: "thunderstorm", 96: "thunderstorm", 99: "thunderstorm",
}

_cache: dict[tuple, tuple[float, dict]] = {}


def weather_condition(code) -> str:
    return _WMO.get(code, "unknown") if isinstance(code, int) else "unknown"


def _at(values, i):
    return values[i] if isinstance(values, list) and i < len(values) else None


def parse_conditions(data: dict, lat: float, lng: float) -> dict:
    current = data.get("current") or {}
    if not isinstance(current.get("temperature_2m"), (int, float)):
        raise ServiceUnavailableException("Incomplete current weather data from provider.")

    daily = data.get("daily") or {}
    dates = daily.get("time") or []
    days = []
    for i, date in enumerate(dates[:FORECAST_DAYS]):
        code = _at(daily.get("weather_code"), i)
        days.append({
            "date": date,
            "weather_code": code,
            "condition": weather_condition(code),
            "temp_max_c": _at(daily.get("temperature_2m_max"), i),
            "temp_min_c": _at(daily.get("temperature_2m_min"), i),
            "precipitation_mm": _at(daily.get("precipitation_sum"), i),
            "precipitation_probability_pct": _at(daily.get("precipitation_probability_max"), i),
            "et0_mm": _at(daily.get("et0_fao_evapotranspiration"), i),
            "humidity_mean_pct": _at(daily.get("relative_humidity_2m_mean"), i),
            "wind_max_kmh": _at(daily.get("wind_speed_10m_max"), i),
        })

    code = current.get("weather_code")
    return {
        "location": {
            "lat": round(lat, 3),
            "lng": round(lng, 3),
            "timezone": data.get("timezone"),
            "elevation_m": data.get("elevation"),
        },
        "current": {
            "valid_at": current.get("time"),
            "temperature_c": current.get("temperature_2m"),
            "humidity_pct": current.get("relative_humidity_2m"),
            "precipitation_mm": current.get("precipitation"),
            "wind_kmh": current.get("wind_speed_10m"),
            "weather_code": code,
            "condition": weather_condition(code),
            "soil_moisture_0_1cm": current.get("soil_moisture_0_to_1cm"),
            "soil_moisture_3_9cm": current.get("soil_moisture_3_to_9cm"),
        },
        "daily": days,
        "provenance": {
            **PROVENANCE_BASE,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "valid_at": current.get("time"),
            "timezone": data.get("timezone"),
        },
    }


class WeatherService:
    async def get_conditions(self, lat: float, lng: float) -> dict:
        key = (round(lat, 2), round(lng, 2))
        cached = _cache.get(key)
        if cached and time.monotonic() - cached[0] < CACHE_TTL_SECONDS:
            return cached[1]

        params = {
            "latitude": lat,
            "longitude": lng,
            "current": ",".join(CURRENT_VARS),
            "daily": ",".join(DAILY_VARS),
            "forecast_days": FORECAST_DAYS,
            "timezone": "auto",
            "wind_speed_unit": "kmh",
        }
        try:
            async with httpx.AsyncClient(timeout=settings.EXTERNAL_API_TIMEOUT_SECONDS) as client:
                response = await client.get(BASE_URL, params=params)
                response.raise_for_status()
                result = parse_conditions(response.json(), lat, lng)
        except ServiceUnavailableException:
            raise
        except httpx.TimeoutException as e:
            logger.error("Weather API timeout: %s", e)
            raise ServiceUnavailableException("Weather service did not respond in time.") from e
        except Exception as e:
            logger.error("Weather API error: %s", e)
            raise ServiceUnavailableException("Weather data is temporarily unavailable.") from e

        if len(_cache) > 2000:
            _cache.clear()
        _cache[key] = (time.monotonic(), result)
        return result

    async def get_current_weather(self, lat: float, lng: float) -> dict:
        """Compact current-conditions dict used as AI context and by the legacy /api/weather endpoint."""
        c = await self.get_conditions(lat, lng)
        cur = c["current"]
        return {
            "temp": cur["temperature_c"],
            "humidity": cur["humidity_pct"],
            "rainfall": cur["precipitation_mm"],
            "wind": cur["wind_kmh"],
            "soil_moisture": cur["soil_moisture_3_9cm"],
            "description": cur["condition"],
            "valid_at": cur["valid_at"],
            "source": "open-meteo",
            "source_type": "model_estimate",
        }

    async def get_forecast(self, lat: float, lng: float, days: int = 7) -> list:
        c = await self.get_conditions(lat, lng)
        return c["daily"][: max(1, min(days, FORECAST_DAYS))]


weather_service = WeatherService()

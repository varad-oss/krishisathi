import httpx
import logging
from models.exceptions import ServiceUnavailableException

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    async def get_current_weather(self, lat: float, lng: float) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}?latitude={lat}&longitude={lng}&current_weather=true&hourly=relative_humidity_2m,precipitation,soil_moisture_0_to_7cm&timezone=auto"
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                current = data.get("current_weather")
                if not current or "temperature" not in current or "windspeed" not in current:
                    raise ServiceUnavailableException("Incomplete current weather data from provider.")
                    
                temp = current["temperature"]
                wind = current["windspeed"]
                
                hourly = data.get("hourly", {})
                if not all(k in hourly and len(hourly[k]) > 0 for k in ["relative_humidity_2m", "precipitation", "soil_moisture_0_to_7cm"]):
                    raise ServiceUnavailableException("Incomplete hourly weather data from provider.")
                    
                humidity = hourly["relative_humidity_2m"][0]
                rainfall = hourly["precipitation"][0]
                soil_moisture = hourly["soil_moisture_0_to_7cm"][0]
                
                return {
                    "temp": temp,
                    "humidity": humidity,
                    "rainfall": rainfall,
                    "wind": wind,
                    "soil_moisture": soil_moisture,
                    "description": self._get_weather_desc(current.get("weathercode", 0)),
                    "source": "open-meteo",
                    "source_type": "external_live_api"
                }
        except ServiceUnavailableException:
            raise
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            raise ServiceUnavailableException("Weather data is temporarily unavailable.") from e

    async def get_forecast(self, lat: float, lng: float, days: int = 7) -> list:
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}?latitude={lat}&longitude={lng}&daily=temperature_2m_max,temperature_2m_min,weathercode,precipitation_sum&timezone=auto&past_days=0"
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                daily = data.get("daily")
                if not daily:
                    raise ServiceUnavailableException("Incomplete daily forecast data from provider.")
                    
                dates = daily.get("time", [])
                t_max = daily.get("temperature_2m_max", [])
                t_min = daily.get("temperature_2m_min", [])
                w_codes = daily.get("weathercode", [])
                
                forecast = []
                for i in range(min(days, len(dates))):
                    if i >= len(t_max) or i >= len(t_min) or i >= len(w_codes):
                        raise ServiceUnavailableException("Incomplete forecast arrays from provider.")
                    forecast.append({
                        "date": dates[i],
                        "temp_max": t_max[i],
                        "temp_min": t_min[i],
                        "description": self._get_weather_desc(w_codes[i]),
                        "humidity": None 
                    })
                return forecast
        except ServiceUnavailableException:
            raise
        except Exception as e:
            logger.error(f"Forecast API error: {e}")
            raise ServiceUnavailableException("Weather forecast is temporarily unavailable.") from e

    def _get_weather_desc(self, code: int) -> str:
        if code == 0: return "Clear sky"
        if code in [1, 2, 3]: return "Partly cloudy"
        if code in [45, 48]: return "Fog"
        if code in [51, 53, 55]: return "Drizzle"
        if code in [61, 63, 65]: return "Rain"
        if code in [80, 81, 82]: return "Rain showers"
        if code in [95, 96, 99]: return "Thunderstorm"
        return "Unknown"

weather_service = WeatherService()

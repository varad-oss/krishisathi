import httpx
import logging

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
                
                current = data.get("current_weather", {})
                temp = current.get("temperature", 28.5)
                wind = current.get("windspeed", 12.5)
                
                humidity = 65
                rainfall = 0.0
                soil_moisture = 0.3 # Default volumetric
                
                if "hourly" in data:
                    if "relative_humidity_2m" in data["hourly"] and len(data["hourly"]["relative_humidity_2m"]) > 0:
                        humidity = data["hourly"]["relative_humidity_2m"][0]
                    if "precipitation" in data["hourly"] and len(data["hourly"]["precipitation"]) > 0:
                        rainfall = data["hourly"]["precipitation"][0]
                    if "soil_moisture_0_to_7cm" in data["hourly"] and len(data["hourly"]["soil_moisture_0_to_7cm"]) > 0:
                        soil_moisture = data["hourly"]["soil_moisture_0_to_7cm"][0]
                
                return {
                    "temp": temp,
                    "humidity": humidity,
                    "rainfall": rainfall,
                    "wind": wind,
                    "soil_moisture": soil_moisture,
                    "description": self._get_weather_desc(current.get("weathercode", 0)),
                    "source": "Open-Meteo Live API"
                }
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return self._mock_current_weather()

    async def get_forecast(self, lat: float, lng: float, days: int = 7) -> list:
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}?latitude={lat}&longitude={lng}&daily=temperature_2m_max,temperature_2m_min,weathercode,precipitation_sum&timezone=auto&past_days=0"
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                daily = data.get("daily", {})
                dates = daily.get("time", [])
                t_max = daily.get("temperature_2m_max", [])
                t_min = daily.get("temperature_2m_min", [])
                w_codes = daily.get("weathercode", [])
                
                forecast = []
                for i in range(min(days, len(dates))):
                    forecast.append({
                        "date": dates[i],
                        "temp_max": t_max[i] if i < len(t_max) else 30.0,
                        "temp_min": t_min[i] if i < len(t_min) else 22.0,
                        "description": self._get_weather_desc(w_codes[i] if i < len(w_codes) else 0),
                        "humidity": 60 
                    })
                return forecast
        except Exception as e:
            logger.error(f"Forecast API error: {e}")
            return self._mock_forecast(days)

    def _get_weather_desc(self, code: int) -> str:
        if code == 0: return "Clear sky"
        if code in [1, 2, 3]: return "Partly cloudy"
        if code in [45, 48]: return "Fog"
        if code in [51, 53, 55]: return "Drizzle"
        if code in [61, 63, 65]: return "Rain"
        if code in [80, 81, 82]: return "Rain showers"
        if code in [95, 96, 99]: return "Thunderstorm"
        return "Unknown"

    def _mock_current_weather(self) -> dict:
        return {
            "temp": 28.5,
            "humidity": 65,
            "rainfall": 0.0,
            "wind": 12.5,
            "description": "partly cloudy",
            "source": "Mock Data"
        }
        
    def _mock_forecast(self, days: int) -> list:
        forecast = []
        for i in range(days):
            forecast.append({
                "date": f"2026-08-{21+i:02d}",
                "temp_max": 30.0 + i % 3,
                "temp_min": 22.0 + i % 2,
                "description": "clear sky" if i % 2 == 0 else "light rain",
                "humidity": 60 + i * 2
            })
        return forecast

weather_service = WeatherService()

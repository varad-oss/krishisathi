import httpx
from config import settings

class WeatherService:
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"

    async def get_current_weather(self, lat: float, lng: float) -> dict:
        if not self.api_key:
            return self._mock_current_weather()
            
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/weather?lat={lat}&lon={lng}&appid={self.api_key}&units=metric"
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "temp": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "rainfall": data.get("rain", {}).get("1h", 0.0),
                    "wind": data["wind"]["speed"],
                    "description": data["weather"][0]["description"]
                }
        except Exception as e:
            print(f"Weather API error: {e}")
            return self._mock_current_weather()

    async def get_forecast(self, lat: float, lng: float, days: int = 7) -> list:
        if not self.api_key:
            return self._mock_forecast(days)
            
        try:
            async with httpx.AsyncClient() as client:
                # Using 5 day / 3 hour forecast API for free tier as daily forecast is paid in some plans
                url = f"{self.base_url}/forecast?lat={lat}&lon={lng}&appid={self.api_key}&units=metric"
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                # Naive grouping by day for demo
                daily_forecasts = []
                for i in range(0, min(len(data["list"]), days * 8), 8):
                    item = data["list"][i]
                    daily_forecasts.append({
                        "date": item["dt_txt"].split(" ")[0],
                        "temp_max": item["main"]["temp_max"],
                        "temp_min": item["main"]["temp_min"],
                        "description": item["weather"][0]["description"],
                        "humidity": item["main"]["humidity"]
                    })
                return daily_forecasts
        except Exception as e:
            print(f"Forecast API error: {e}")
            return self._mock_forecast(days)

    def _mock_current_weather(self) -> dict:
        return {
            "temp": 28.5,
            "humidity": 65,
            "rainfall": 0.0,
            "wind": 12.5,
            "description": "partly cloudy"
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

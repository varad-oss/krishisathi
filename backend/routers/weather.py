from fastapi import APIRouter, Query

from services.weather_service import weather_service

router = APIRouter(prefix="/api/weather", tags=["Weather"])

# ServiceUnavailableException is mapped to a 503 envelope by the global handler.


@router.get("")
async def get_current_weather(lat: float = Query(..., ge=-90, le=90), lng: float = Query(..., ge=-180, le=180)):
    return await weather_service.get_current_weather(lat, lng)


@router.get("/forecast")
async def get_forecast(lat: float = Query(..., ge=-90, le=90), lng: float = Query(..., ge=-180, le=180), days: int = Query(7, ge=1, le=7)):
    return await weather_service.get_forecast(lat, lng, days)

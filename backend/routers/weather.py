from fastapi import APIRouter, HTTPException
from services.weather_service import weather_service

router = APIRouter(prefix="/api/weather", tags=["Weather"])

@router.get("")
async def get_current_weather(lat: float, lng: float):
    try:
        return await weather_service.get_current_weather(lat, lng)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast")
async def get_forecast(lat: float, lng: float, days: int = 7):
    try:
        return await weather_service.get_forecast(lat, lng, days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

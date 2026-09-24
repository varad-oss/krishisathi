from fastapi import APIRouter, HTTPException
from services.weather_service import weather_service
from models.exceptions import ServiceUnavailableException

router = APIRouter(prefix="/api/weather", tags=["Weather"])

@router.get("")
async def get_current_weather(lat: float, lng: float):
    try:
        return await weather_service.get_current_weather(lat, lng)
    except ServiceUnavailableException as e:
        raise HTTPException(status_code=503, detail={"error": "service_unavailable", "message": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "internal_error", "message": "An unexpected error occurred."})

@router.get("/forecast")
async def get_forecast(lat: float, lng: float, days: int = 7):
    try:
        return await weather_service.get_forecast(lat, lng, days)
    except ServiceUnavailableException as e:
        raise HTTPException(status_code=503, detail={"error": "service_unavailable", "message": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "internal_error", "message": "An unexpected error occurred."})

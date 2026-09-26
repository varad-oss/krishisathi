"""Farmer-facing intelligence for one location.

Each endpoint degrades independently: a failure in soil data never hides weather,
and every block reports its own availability and provenance.
"""
from fastapi import APIRouter, Query

from services import agro_rules
from services.crops import normalize_crop
from services.earth_engine_service import earth_engine_service
from services.regenerative_service import recommend
from services.soil_service import soil_service
from services.weather_service import weather_service
from models.exceptions import ServiceUnavailableException

router = APIRouter(prefix="/api/farm", tags=["Farm intelligence"])

Lat = Query(..., ge=-90, le=90)
Lng = Query(..., ge=-180, le=180)


@router.get("/conditions")
async def get_conditions(lat: float = Lat, lng: float = Lng):
    """Current conditions (model estimate), 7-day forecast and rule-based agro insights."""
    conditions = await weather_service.get_conditions(lat, lng)
    return {**conditions, "insights": agro_rules.evaluate(conditions)}


@router.get("/soil")
async def get_soil(lat: float = Lat, lng: float = Lng):
    return await soil_service.get_soil(lat, lng)


@router.get("/crop-health")
async def get_crop_health(lat: float = Lat, lng: float = Lng):
    return await earth_engine_service.get_point_crop_health(lat, lng)


@router.get("/regenerative")
async def get_regenerative(lat: float = Lat, lng: float = Lng, crop: str | None = Query(None, max_length=40)):
    canonical_crop = normalize_crop(crop)
    soil = await soil_service.get_soil(lat, lng)
    try:
        insights = agro_rules.evaluate(await weather_service.get_conditions(lat, lng))
        weather_status = "available"
    except ServiceUnavailableException:
        insights, weather_status = [], "unavailable"
    return {
        "crop": canonical_crop,
        "soil": soil,
        "inputs": {"soil": soil.get("status"), "weather": weather_status, "crop": "provided" if canonical_crop else "not_provided"},
        "recommendations": recommend(canonical_crop, soil, insights),
    }

"""Farmer-facing intelligence for one location.

Each endpoint degrades independently: a failure in soil data never hides weather,
and every block reports its own availability and provenance.
"""
from datetime import date

from fastapi import APIRouter, Query

from models.intelligence import FarmIntelligence
from services import agro_rules
from services.crops import normalize_crop
from services.earth_engine_service import earth_engine_service
from services.intelligence_service import farm_intelligence
from services.crop_options import crop_options
from services.crop_stage import estimate_stage
from services.regenerative_service import plan, recommend
from services.soil_service import soil_service
from services.weather_service import weather_service
from models.exceptions import ServiceUnavailableException

router = APIRouter(prefix="/api/farm", tags=["Farm intelligence"])

Lat = Query(..., ge=-90, le=90)
Lng = Query(..., ge=-180, le=180)
Crop = Query(None, max_length=40)
SowingDate = Query(None, description="ISO date the crop was sown; enables crop-stage-aware risks")


@router.get("/intelligence", response_model=FarmIntelligence)
async def get_farm_intelligence(lat: float = Lat, lng: float = Lng, crop: str | None = Crop, sowing_date: date | None = SowingDate):
    """What matters for this farm right now: weather, soil, satellite, crop stage and nearby reports fused into
    explainable risks and one prioritized action. Each input reports its own status; none is estimated when missing."""
    return await farm_intelligence(lat, lng, crop, sowing_date)


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


@router.get("/crop-health/history")
async def get_crop_health_history(lat: float = Lat, lng: float = Lng):
    """Sentinel-2 NDVI for six consecutive 30-day windows; a window without a clear observation is null, never filled in."""
    return await earth_engine_service.get_point_history(lat, lng)


@router.get("/regenerative")
async def get_regenerative(lat: float = Lat, lng: float = Lng, crop: str | None = Crop, sowing_date: date | None = SowingDate):
    canonical_crop = normalize_crop(crop)
    soil = await soil_service.get_soil(lat, lng)
    try:
        insights = agro_rules.evaluate(await weather_service.get_conditions(lat, lng))
        weather_status = "available"
    except ServiceUnavailableException:
        insights, weather_status = [], "unavailable"
    stage = estimate_stage(canonical_crop, sowing_date, date.today())
    recommendations = recommend(canonical_crop, soil, insights)
    return {
        "crop": canonical_crop,
        "soil": soil,
        "inputs": {"soil": soil.get("status"), "weather": weather_status, "crop": "provided" if canonical_crop else "not_provided",
                   "crop_stage": stage["status"]},
        "recommendations": recommendations,
        "plan": plan(recommendations, stage, soil.get("status") == "available"),
        "crop_stage": stage,
    }


@router.get("/crop-options")
async def get_crop_options(lat: float = Lat, lng: float = Lng, crop: str | None = Crop):
    """Trade-offs between the farm's crop and crops commonly grown nearby. Not a ranking: no crop is called best,
    and values without a verified source (market prices, input costs, profit) are reported as unavailable."""
    return await crop_options(lat, lng, normalize_crop(crop))

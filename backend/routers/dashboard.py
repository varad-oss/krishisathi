import asyncio
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from core.rate_limit import ai_rate_limit, redis_client
from models.diagnosis import Language
from models.exceptions import ServiceUnavailableException
from routers.states import INDIAN_STATES
from services import agro_rules
from services.earth_engine_service import earth_engine_service
from services.gemini_service import gemini_service
from services.persistence_service import persistence_service
from services.weather_service import PROVENANCE_BASE, weather_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

STATS_CACHE_SECONDS = 60
MIN_DIAGNOSES_FOR_REPORT = 5
REPORT_CACHE_SECONDS = 900


async def _cache_get(key: str):
    if not redis_client:
        return None
    try:
        cached = await redis_client.get(key)
        return json.loads(cached) if cached else None
    except Exception as e:
        logger.warning("Cache read failed for %s: %s", key, e)
        return None


async def _cache_set(key: str, value, seconds: int):
    if not redis_client:
        return
    try:
        await redis_client.set(key, json.dumps(value), ex=seconds)
    except Exception as e:
        logger.warning("Cache write failed for %s: %s", key, e)


@router.get("/stats")
async def get_stats():
    cached = await _cache_get("cache:dashboard_stats:v2")
    if cached:
        return cached
    stats = await persistence_service.get_dashboard_stats()
    await _cache_set("cache:dashboard_stats:v2", stats, STATS_CACHE_SECONDS)
    return stats


@router.get("/report", dependencies=[Depends(ai_rate_limit)])
async def get_dashboard_report(language: Language = "en"):
    stats = await persistence_service.get_dashboard_stats()
    base = {"generated_at": datetime.now(timezone.utc).isoformat(), "data_as_of": stats["generated_at"], "kind": "ai_generated_summary"}
    if stats["total_diagnoses"] < MIN_DIAGNOSES_FOR_REPORT:
        return {**base, "status": "insufficient_data", "report_text": None, "minimum_records": MIN_DIAGNOSES_FOR_REPORT, "records": stats["total_diagnoses"]}

    cache_key = f"cache:dashboard_report:{language}"
    cached = await _cache_get(cache_key)
    if cached:
        return cached

    report_input = {k: v for k, v in stats.items() if k not in ("provenance",)}
    report_text = await gemini_service.generate_dashboard_report(report_input, language)
    result = {**base, "status": "available", "report_text": report_text}
    await _cache_set(cache_key, result, REPORT_CACHE_SECONDS)
    return result


@router.get("/outbreaks")
async def get_dashboard_outbreaks():
    return await persistence_service.get_outbreaks()


@router.get("/crop-health")
async def get_crop_health():
    """Regional NDVI is not computed yet; say so rather than returning estimates."""
    return {
        "status": "unavailable",
        "reason": "not_configured" if not earth_engine_service.initialized else "regional_aggregation_not_implemented",
        "message": "Regional satellite crop-health aggregation is not available.",
        "overall_index": None,
        "regions": [],
    }


@router.get("/weather-risk")
async def get_weather_risk():
    """Rule-based forecast risks at one reference point per state (indicative, not statewide)."""
    async def one(state):
        try:
            conditions = await weather_service.get_conditions(state["lat"], state["lng"])
        except ServiceUnavailableException:
            return {"state": state["code"], "status": "unavailable", "insights": []}
        return {"state": state["code"], "status": "available", "insights": agro_rules.evaluate(conditions)}

    regions = await asyncio.gather(*(one(s) for s in INDIAN_STATES))
    return {
        "regions": regions,
        "aggregation": "single_reference_point_per_state",
        "provenance": {**PROVENANCE_BASE, "retrieved_at": datetime.now(timezone.utc).isoformat()},
    }

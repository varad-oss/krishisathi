import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from core.cache import cache_get, cache_set
from core.rate_limit import ai_rate_limit
from models.diagnosis import Language
from services.earth_engine_service import earth_engine_service
from services.gemini_service import gemini_service
from services.measurement import feedback_metrics
from services.persistence_service import persistence_service
from services.regions import state_weather_risk

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

STATS_CACHE_SECONDS = 60
MIN_DIAGNOSES_FOR_REPORT = 5
REPORT_CACHE_SECONDS = 900


@router.get("/stats")
async def get_stats():
    cached = await cache_get("cache:dashboard_stats:v2")
    if cached:
        return cached
    stats = await persistence_service.get_dashboard_stats()
    await cache_set("cache:dashboard_stats:v2", stats, STATS_CACHE_SECONDS)
    return stats


@router.get("/report", dependencies=[Depends(ai_rate_limit)])
async def get_dashboard_report(language: Language = "en"):
    stats = await persistence_service.get_dashboard_stats()
    base = {"generated_at": datetime.now(timezone.utc).isoformat(), "data_as_of": stats["generated_at"], "kind": "ai_generated_summary"}
    if stats["total_diagnoses"] < MIN_DIAGNOSES_FOR_REPORT:
        return {**base, "status": "insufficient_data", "report_text": None, "minimum_records": MIN_DIAGNOSES_FOR_REPORT, "records": stats["total_diagnoses"]}

    cache_key = f"cache:dashboard_report:{language}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    report_input = {k: v for k, v in stats.items() if k not in ("provenance",)}
    report_text = await gemini_service.generate_dashboard_report(report_input, language)
    result = {**base, "status": "available", "report_text": report_text}
    await cache_set(cache_key, result, REPORT_CACHE_SECONDS)
    return result


@router.get("/feedback-metrics")
async def get_feedback_metrics():
    """App-derived follow-through and outcome signals (self-reported, small groups suppressed)."""
    cached = await cache_get("cache:feedback_metrics:v1")
    if cached:
        return cached
    metrics = await feedback_metrics()
    await cache_set("cache:feedback_metrics:v1", metrics, STATS_CACHE_SECONDS)
    return metrics


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
    return await state_weather_risk()

from fastapi import APIRouter
from services.gemini_service import gemini_service
from services.persistence_service import persistence_service
from datetime import datetime
from core.rate_limit import redis_client
import json


router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_stats():
    # Cache dashboard stats for 60 seconds to prevent DB saturation during traffic spikes
    if redis_client:
        cached = await redis_client.get("cache:dashboard_stats")
        if cached:
            return json.loads(cached)
            
    stats = await persistence_service.get_dashboard_stats()
    
    if redis_client:
        await redis_client.set("cache:dashboard_stats", json.dumps(stats), ex=60)
        
    return stats


@router.get("/report")
async def get_dashboard_report(language: str = 'en'):
    from fastapi import HTTPException
    from models.exceptions import ServiceUnavailableException
    
    stats = await persistence_service.get_dashboard_stats()
    report_data = {
        "stats": stats,
        "period": "Real-time",
        "focus_areas": ["Data driven from persistent state"],
    }
    try:
        report_text = gemini_service.generate_dashboard_report(report_data, language)
        return {
            "report_text": report_text,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "period": "Real-time (Current Data)",
        }
    except ServiceUnavailableException as e:
        raise HTTPException(status_code=503, detail={"error": "service_unavailable", "message": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "internal_error", "message": "Failed to generate report."})


@router.get("/outbreaks")
async def get_dashboard_outbreaks():
    return await persistence_service.get_outbreaks()


@router.get("/crop-health")
async def get_crop_health():
    # Earth Engine interactive real-time regional calculation is currently not feasible 
    # without a pre-computed batch pipeline. Do not fabricate values.
    return {
        "status": "unavailable",
        "message": "Regional crop health data is currently unavailable.",
        "regions": [],
        "overall_index": None,
        "measurement_date": None
    }


@router.get("/activity")
async def get_recent_activity():
    stats = await persistence_service.get_dashboard_stats()
    return stats.get("recent_activity", [])

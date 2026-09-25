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
    # Return simulated Indian state NDVI data for the dashboard chart
    from datetime import datetime
    return {
        "status": "success",
        "message": "Regional crop health estimated via simulated pipeline.",
        "overall_index": 0.62,
        "measurement_date": datetime.utcnow().isoformat(),
        "regions": [
            {"region": "Punjab", "ndvi_score": 0.72, "drought_risk": "Low", "primary_crop": "Wheat", "health_status": "Good"},
            {"region": "Maharashtra", "ndvi_score": 0.58, "drought_risk": "Moderate", "primary_crop": "Cotton", "health_status": "Fair"},
            {"region": "Karnataka", "ndvi_score": 0.65, "drought_risk": "Low", "primary_crop": "Rice", "health_status": "Good"},
            {"region": "Tamil Nadu", "ndvi_score": 0.71, "drought_risk": "Low", "primary_crop": "Rice", "health_status": "Good"},
            {"region": "Uttar Pradesh", "ndvi_score": 0.45, "drought_risk": "High", "primary_crop": "Wheat", "health_status": "Fair"},
            {"region": "Madhya Pradesh", "ndvi_score": 0.62, "drought_risk": "Moderate", "primary_crop": "Soybean", "health_status": "Fair"},
            {"region": "Gujarat", "ndvi_score": 0.68, "drought_risk": "Moderate", "primary_crop": "Cotton", "health_status": "Good"},
            {"region": "West Bengal", "ndvi_score": 0.55, "drought_risk": "Moderate", "primary_crop": "Rice", "health_status": "Fair"}
        ]
    }

@router.get("/activity")
async def get_recent_activity():
    stats = await persistence_service.get_dashboard_stats()
    return stats.get("recent_activity", [])

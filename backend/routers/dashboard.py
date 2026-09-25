from fastapi import APIRouter
from services.gemini_service import gemini_service
from services.persistence_service import persistence_service
from datetime import datetime


router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_stats():
    # Use real persistence aggregations
    return await persistence_service.get_dashboard_stats()


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
            "period": "August 14-21, 2026",
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
    return {
        "overall_index": 74.2,
        "measurement_date": "2026-08-20",
        "regions": [
            {"name": "Punjab", "ndvi": 0.72},
            {"name": "Maharashtra", "ndvi": 0.58},
            {"name": "Karnataka", "ndvi": 0.65},
            {"name": "Tamil Nadu", "ndvi": 0.71},
            {"name": "Uttar Pradesh", "ndvi": 0.45},
            {"name": "Madhya Pradesh", "ndvi": 0.62},
            {"name": "Gujarat", "ndvi": 0.68},
            {"name": "West Bengal", "ndvi": 0.55},
        ],
    }


@router.get("/activity")
async def get_recent_activity():
    stats = await persistence_service.get_dashboard_stats()
    return stats.get("recent_activity", [])

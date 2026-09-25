from fastapi import APIRouter, Depends
from core.security import require_system_role
from services.earth_engine_service import earth_engine_service, EE_AVAILABLE

router = APIRouter(prefix="/api/debug", tags=["Debug & Verification"])

@router.get("/earth-engine-status", dependencies=[Depends(require_system_role)])
async def get_ee_status():
    """Debug endpoint for hackathon judges to verify Earth Engine pipeline status."""
    return {
        "earth_engine_library_installed": EE_AVAILABLE,
        "earth_engine_authenticated": getattr(earth_engine_service, 'initialized', False),
        "pipeline_mode": "LIVE" if getattr(earth_engine_service, 'initialized', False) else "UNAVAILABLE",
        "note": "Requires ee.Initialize() with valid credentials to return LIVE mode."
    }

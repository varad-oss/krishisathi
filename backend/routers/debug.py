from fastapi import APIRouter, Depends

from core.security import require_system_role
from services.earth_engine_service import EE_AVAILABLE, earth_engine_service

router = APIRouter(prefix="/api/debug", tags=["Debug & Verification"], dependencies=[Depends(require_system_role)])


@router.get("/earth-engine-status")
async def get_ee_status():
    """Authenticated check of the Earth Engine pipeline status."""
    return {
        "earth_engine_library_installed": EE_AVAILABLE,
        "earth_engine_authenticated": earth_engine_service.initialized,
        "pipeline_mode": "LIVE" if earth_engine_service.initialized else "UNAVAILABLE",
        "note": "Requires Earth Engine service-account credentials to return LIVE mode.",
    }

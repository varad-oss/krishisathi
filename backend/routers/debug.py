from fastapi import APIRouter
from services.earth_engine_service import earth_engine_service, EE_AVAILABLE

router = APIRouter(prefix="/api/debug", tags=["Debug & Verification"])

@router.get("/earth-engine-status")
async def get_ee_status():
    """Debug endpoint for hackathon judges to verify Earth Engine pipeline status."""
    return {
        "earth_engine_library_installed": EE_AVAILABLE,
        "earth_engine_authenticated": earth_engine_service.initialized,
        "pipeline_mode": "LIVE" if earth_engine_service.initialized else "SIMULATED_FALLBACK",
        "demo_ndvi_score": earth_engine_service._simulate_ndvi(),
        "note": "For noncommercial / research use. Requires ee.Initialize() with valid credentials to return LIVE mode."
    }

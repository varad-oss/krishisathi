import logging
from fastapi import APIRouter, HTTPException
from services.kvk_service import kvk_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/kvk", tags=["KVK"])

@router.get("/nearest")
async def get_nearest_kvk(lat: float, lng: float):
    try:
        nearest = kvk_service.get_nearest_kvk(lat, lng)
        if not nearest:
            raise HTTPException(status_code=404, detail="No KVK locations available")
        return nearest
    except Exception as e:
        logger.error(f"Error in get_nearest_kvk: {e}")
        raise HTTPException(status_code=500, detail=str(e))

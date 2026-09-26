from fastapi import APIRouter, Query

from core.errors import ApiError
from services.kvk_service import KVK_PROVENANCE, kvk_service

router = APIRouter(prefix="/api/kvk", tags=["KVK"])


@router.get("/nearest")
async def get_nearest_kvk(lat: float = Query(..., ge=-90, le=90), lng: float = Query(..., ge=-180, le=180)):
    nearest = kvk_service.get_nearest_kvk(lat, lng)
    if not nearest:
        raise ApiError(404, "NOT_FOUND", "No Krishi Vigyan Kendra locations are available.")
    return {**nearest, "provenance": KVK_PROVENANCE}

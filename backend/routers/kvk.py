from fastapi import APIRouter, Query

from core.errors import ApiError
from services.kvk_service import KVK_PROVENANCE, MATCH_RADIUS_KM, kvk_service

router = APIRouter(prefix="/api/kvk", tags=["KVK"])


@router.get("/nearest")
async def get_nearest_kvk(lat: float = Query(..., ge=-90, le=90), lng: float = Query(..., ge=-180, le=180)):
    """KVK for the district nearest the location. `distance_km` is null unless the KVK site itself is verified."""
    nearest = kvk_service.get_nearest_kvk(lat, lng)
    if not nearest:
        raise ApiError(
            404,
            "NOT_FOUND",
            f"No listed Krishi Vigyan Kendra district is within {MATCH_RADIUS_KM:.0f} km of this location.",
        )
    return {**nearest, "provenance": KVK_PROVENANCE}

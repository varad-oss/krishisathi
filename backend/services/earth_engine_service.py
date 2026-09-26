import asyncio
import json
import logging
from datetime import date, timedelta

from config import settings

logger = logging.getLogger(__name__)

# Earth Engine is optional: without the library or credentials, crop-health endpoints
# report "unavailable" instead of producing estimates.
try:
    import ee
    EE_AVAILABLE = True
except ImportError:
    EE_AVAILABLE = False

PROVENANCE = {
    "source": "Sentinel-2 surface reflectance via Google Earth Engine",
    "source_url": "https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED",
    "kind": "satellite_observation",
    "resolution": "10 m (averaged over a 250 m radius)",
    "notes": "Median NDVI of low-cloud scenes. NDVI depends on crop type and growth stage; compare it with your own field over time, not with other crops.",
}
WINDOW_DAYS = 30
BUFFER_M = 250
TIMEOUT_S = 25


class EarthEngineService:
    def __init__(self):
        self.initialized = False
        if not EE_AVAILABLE:
            return
        try:
            if settings.EE_SERVICE_ACCOUNT_KEY_JSON:
                key = json.loads(settings.EE_SERVICE_ACCOUNT_KEY_JSON)
                credentials = ee.ServiceAccountCredentials(key["client_email"], key_data=settings.EE_SERVICE_ACCOUNT_KEY_JSON)
                ee.Initialize(credentials, project=key.get("project_id"))
            else:
                ee.Initialize()
            self.initialized = True
        except Exception as e:
            logger.info("Earth Engine not initialized (crop health will report unavailable): %s", e)

    def calculate_regional_ndvi(self, region_geometry, start_date: str, end_date: str) -> dict:
        """Mean of the median Sentinel-2 NDVI over a geometry and date window."""
        if not self.initialized:
            return {"status": "unavailable", "source": "google-earth-engine", "message": "Earth Engine credentials not initialized."}

        try:
            collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                          .filterBounds(region_geometry)
                          .filterDate(start_date, end_date)
                          .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))
            count = collection.size()
            median_ndvi = collection.map(lambda img: img.normalizedDifference(['B8', 'B4']).rename('NDVI')).median()
            mean_dict = median_ndvi.reduceRegion(reducer=ee.Reducer.mean(), geometry=region_geometry, scale=10, maxPixels=1e9)
            result = ee.Dictionary({"ndvi": mean_dict.get('NDVI'), "count": count}).getInfo()
            if result.get("ndvi") is None:
                return {"status": "no-data", "source": "google-earth-engine"}
            return {
                "status": "available",
                "value": result["ndvi"],
                "image_count": result.get("count"),
                "source": "sentinel-2",
                "provider": "google-earth-engine",
            }
        except Exception as e:
            logger.error("Earth Engine calculation error: %s", e)
            return {"status": "unavailable", "source": "google-earth-engine", "message": "Earth Engine data is temporarily unavailable."}

    def _point_ndvi(self, lat: float, lng: float, today: date) -> dict:
        geometry = ee.Geometry.Point([lng, lat]).buffer(BUFFER_M)
        cur_start = today - timedelta(days=WINDOW_DAYS)
        prev_start = cur_start - timedelta(days=WINDOW_DAYS)
        current = self.calculate_regional_ndvi(geometry, cur_start.isoformat(), today.isoformat())
        previous = self.calculate_regional_ndvi(geometry, prev_start.isoformat(), cur_start.isoformat())
        if current.get("status") != "available":
            return {"status": "no_data" if current.get("status") == "no-data" else "unavailable", "reason": "no_clear_imagery" if current.get("status") == "no-data" else "upstream_error"}
        prev_value = previous.get("value") if previous.get("status") == "available" else None
        return {
            "status": "available",
            "ndvi": round(current["value"], 3),
            "ndvi_previous": round(prev_value, 3) if prev_value is not None else None,
            "change": round(current["value"] - prev_value, 3) if prev_value is not None else None,
            "window": {"start": cur_start.isoformat(), "end": today.isoformat()},
            "previous_window": {"start": prev_start.isoformat(), "end": cur_start.isoformat()},
            "image_count": current.get("image_count"),
        }

    async def get_point_crop_health(self, lat: float, lng: float) -> dict:
        if not self.initialized:
            return {"status": "unavailable", "reason": "not_configured", "provenance": PROVENANCE}
        try:
            result = await asyncio.wait_for(asyncio.to_thread(self._point_ndvi, lat, lng, date.today()), timeout=TIMEOUT_S)
        except Exception as e:
            logger.error("Point NDVI failed: %s", e)
            result = {"status": "unavailable", "reason": "upstream_error"}
        result["provenance"] = PROVENANCE
        return result


earth_engine_service = EarthEngineService()

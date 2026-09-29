"""Sentinel-2 crop health (NDVI) from Google Earth Engine.

Dataset: COPERNICUS/S2_SR_HARMONIZED (Level-2A surface reflectance, 10 m). Credentials come from
EE_SERVICE_ACCOUNT_KEY_JSON (the service-account JSON key, raw or base64). Without them every
crop-health response is an explicit "unavailable"; no value is ever estimated in its place.
"""
import asyncio
import base64
import binascii
import json
import logging
import time
from datetime import date, datetime, timedelta, timezone

from config import settings

logger = logging.getLogger(__name__)

try:
    import ee
    EE_AVAILABLE = True
except ImportError:
    EE_AVAILABLE = False

DATASET = "COPERNICUS/S2_SR_HARMONIZED"
PROVENANCE = {
    "source": "Sentinel-2 surface reflectance via Google Earth Engine",
    "source_url": "https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED",
    "kind": "satellite_observation",
    "resolution": "10 m (averaged over a 250 m radius)",
    "notes": "Median NDVI of cloud-masked pixels. NDVI depends on crop type and growth stage; compare it with your own field over time, not with other crops.",
}
WINDOW_DAYS = 30
BUFFER_M = 250
TIMEOUT_S = 25
# Scene-level prefilter only; clouds are removed per pixel with the Scene Classification Layer below,
# so partly cloudy monsoon scenes still contribute their clear pixels.
MAX_SCENE_CLOUD_PCT = 60
# SCL classes kept: 4 vegetation, 5 bare soil, 6 water, 7 unclassified. Dropped: no data, saturated,
# dark/shadow, cloud shadow, clouds (medium, high), cirrus and snow.
CLEAR_SCL_CLASSES = (4, 5, 6, 7)
RETRY_AFTER_S = 300
REQUIRED_KEY_FIELDS = ("client_email", "private_key", "project_id")


def _iso_day(epoch_ms) -> str | None:
    return datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc).date().isoformat() if epoch_ms else None


class CredentialError(ValueError):
    """The configured key cannot be used. `code` is safe to show to operators."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def parse_service_account_key(raw: str) -> dict:
    """Accept the service-account JSON as-is or base64-encoded (easier to paste into hosting dashboards)."""
    text = raw.strip()
    if not text.startswith("{"):
        try:
            text = base64.b64decode(text, validate=True).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError):
            raise CredentialError("invalid_key_encoding") from None
    try:
        key = json.loads(text)
    except ValueError:
        raise CredentialError("invalid_key_json") from None
    if not isinstance(key, dict) or key.get("type", "service_account") != "service_account":
        raise CredentialError("not_a_service_account_key")
    if any(not key.get(f) for f in REQUIRED_KEY_FIELDS):
        raise CredentialError("key_missing_fields")
    # Keys pasted through some dashboards arrive with literal "\n" in the PEM.
    key["private_key"] = key["private_key"].replace("\\n", "\n")
    return key


class EarthEngineService:
    def __init__(self):
        self.initialized = False
        # "configured" | "not_configured" | "error"; `error` is a short code, never a raw exception.
        self.status = "not_configured"
        self.error: str | None = None
        self.project: str | None = None
        self._next_attempt = 0.0
        self._initialize()

    def _initialize(self) -> None:
        self._next_attempt = time.monotonic() + RETRY_AFTER_S
        if not EE_AVAILABLE:
            self.status, self.error = "error", "library_missing"
            logger.error("earthengine-api is not installed; Sentinel-2 crop health is unavailable.")
            return
        if not settings.EE_SERVICE_ACCOUNT_KEY_JSON:
            self.status, self.error = "not_configured", None
            logger.warning("EE_SERVICE_ACCOUNT_KEY_JSON is not set; Sentinel-2 crop health is unavailable.")
            return
        try:
            key = parse_service_account_key(settings.EE_SERVICE_ACCOUNT_KEY_JSON)
        except CredentialError as e:
            self.status, self.error = "error", e.code
            logger.error("Earth Engine key rejected (%s); Sentinel-2 crop health is unavailable.", e.code)
            return
        # The Cloud project must be registered for Earth Engine; it may differ from the key's own project.
        self.project = settings.EE_PROJECT or key["project_id"]
        try:
            credentials = ee.ServiceAccountCredentials(key["client_email"], key_data=json.dumps(key))
            ee.Initialize(credentials, project=self.project)
            ee.data.setDeadline(TIMEOUT_S * 1000)
            # Initialize() does not contact the API; one tiny request proves the account and project work.
            ee.Number(1).getInfo()
        except Exception as e:
            self.initialized = False
            self.status, self.error = "error", "authentication_failed"
            logger.error("Earth Engine initialization failed for %s in project %s: %s", key["client_email"], self.project, e)
            return
        self.initialized, self.status, self.error = True, "configured", None
        logger.info("Earth Engine ready (project %s, dataset %s).", self.project, DATASET)

    def ensure_initialized(self) -> bool:
        """Retry a failed start-up after a cool-down, so a transient outage does not disable the source for good."""
        if not self.initialized and self.status == "error" and self.error == "authentication_failed" \
                and time.monotonic() >= self._next_attempt:
            self._initialize()
        return self.initialized

    def describe(self) -> dict:
        return {"status": self.status, "error": self.error, "dataset": DATASET, "project": self.project if self.initialized else None}

    @staticmethod
    def _window_stats(geometry, start: str, end: str):
        """Server-side dictionary for one window: median NDVI of clear pixels, scene count, latest acquisition."""
        collection = (ee.ImageCollection(DATASET)
                      .filterBounds(geometry)
                      .filterDate(start, end)
                      .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", MAX_SCENE_CLOUD_PCT)))

        def clear_ndvi(img):
            clear = img.select("SCL").remap(list(CLEAR_SCL_CLASSES), [1] * len(CLEAR_SCL_CLASSES), 0)
            return img.normalizedDifference(["B8", "B4"]).rename("NDVI").updateMask(clear)

        # A fully masked NDVI band keeps the composite well-formed when no scene matches, so the
        # result is a null NDVI ("no clear imagery") instead of an Earth Engine error.
        empty = ee.Image.constant(0).toFloat().rename("NDVI").updateMask(0)
        composite = collection.map(clear_ndvi).merge(ee.ImageCollection([empty])).median()
        ndvi = composite.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=10, maxPixels=1e9).get("NDVI")
        return ee.Dictionary({"ndvi": ndvi, "count": collection.size(),
                              "latest_ms": collection.aggregate_max("system:time_start")})

    def calculate_regional_ndvi(self, region_geometry, start_date: str, end_date: str) -> dict:
        """Mean of the cloud-masked median Sentinel-2 NDVI over a geometry and date window."""
        if not self.ensure_initialized():
            return {"status": "unavailable", "source": "google-earth-engine", "message": "Earth Engine credentials not initialized."}
        try:
            result = self._window_stats(region_geometry, start_date, end_date).getInfo()
        except Exception as e:
            logger.error("Earth Engine calculation error: %s", e)
            return {"status": "unavailable", "source": "google-earth-engine", "message": "Earth Engine data is temporarily unavailable."}
        if result.get("ndvi") is None:
            return {"status": "no-data", "source": "google-earth-engine", "image_count": result.get("count")}
        return {
            "status": "available",
            "value": result["ndvi"],
            "image_count": result.get("count"),
            "latest_image_date": _iso_day(result.get("latest_ms")),
            "source": "sentinel-2",
            "provider": "google-earth-engine",
        }

    def _point_ndvi(self, lat: float, lng: float, today: date) -> dict:
        geometry = ee.Geometry.Point([lng, lat]).buffer(BUFFER_M)
        cur_start = today - timedelta(days=WINDOW_DAYS)
        prev_start = cur_start - timedelta(days=WINDOW_DAYS)
        # Both windows in one request: halves latency against the Earth Engine API.
        stats = ee.Dictionary({
            "current": self._window_stats(geometry, cur_start.isoformat(), today.isoformat()),
            "previous": self._window_stats(geometry, prev_start.isoformat(), cur_start.isoformat()),
        }).getInfo()
        current, previous = stats["current"], stats["previous"]
        if current.get("ndvi") is None:
            return {"status": "no_data", "reason": "no_clear_imagery", "image_count": current.get("count"),
                    "window": {"start": cur_start.isoformat(), "end": today.isoformat()}}
        prev_value = previous.get("ndvi")
        return {
            "status": "available",
            "ndvi": round(current["ndvi"], 3),
            "ndvi_previous": round(prev_value, 3) if prev_value is not None else None,
            "change": round(current["ndvi"] - prev_value, 3) if prev_value is not None else None,
            "window": {"start": cur_start.isoformat(), "end": today.isoformat()},
            "previous_window": {"start": prev_start.isoformat(), "end": cur_start.isoformat()},
            "image_count": current.get("count"),
            "latest_image_date": _iso_day(current.get("latest_ms")),
        }

    async def get_point_crop_health(self, lat: float, lng: float) -> dict:
        if not await asyncio.to_thread(self.ensure_initialized):
            reason = "not_configured" if self.status == "not_configured" else "configuration_error"
            return {"status": "unavailable", "reason": reason, "provenance": PROVENANCE}
        try:
            result = await asyncio.wait_for(asyncio.to_thread(self._point_ndvi, lat, lng, date.today()), timeout=TIMEOUT_S)
        except Exception as e:
            logger.error("Point NDVI failed: %s", e)
            result = {"status": "unavailable", "reason": "upstream_error"}
        result["provenance"] = PROVENANCE
        return result


earth_engine_service = EarthEngineService()

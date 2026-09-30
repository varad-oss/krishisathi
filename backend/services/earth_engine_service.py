"""Sentinel-2 crop health (NDVI) from Google Earth Engine.

Dataset: COPERNICUS/S2_SR_HARMONIZED (Level-2A surface reflectance, 10 m). Credentials come from
EE_SERVICE_ACCOUNT_KEY_JSON (the service-account JSON key, raw or base64). Without them every
crop-health response is an explicit "unavailable"; no value is ever estimated in its place.

Status is only "available" after Earth Engine accepted the credentials AND answered a metadata read
of the dataset. Failures carry a short code (see docs/EARTH_ENGINE.md); raw exceptions are only logged.
"""
import asyncio
import base64
import binascii
import json
import logging
import math
import threading
import time
from datetime import date, datetime, timedelta, timezone

from config import settings

logger = logging.getLogger(__name__)

try:
    import ee
    from google.auth.exceptions import RefreshError, TransportError
    EE_AVAILABLE = True
except ImportError:
    EE_AVAILABLE = False
    RefreshError = TransportError = type("_Unavailable", (Exception,), {})

DATASET = "COPERNICUS/S2_SR_HARMONIZED"
PROVENANCE = {
    "source": "Sentinel-2 via Google Earth Engine (COPERNICUS/S2_SR_HARMONIZED)",
    "source_url": "https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED",
    "dataset": DATASET,
    "provider": "Copernicus / ESA",
    "processing": "Level-2A surface reflectance (harmonized)",
    "signal": "Satellite-derived vegetation signal (NDVI), not ground-truth crop health",
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
# Below this share of clear 10 m pixels in the circle, a mean would describe a few scattered pixels,
# not the field, so the window is reported as having no suitable observation.
ROI_PIXELS = math.pi * BUFFER_M ** 2 / 100
MIN_CLEAR_FRACTION = 0.1
RETRY_AFTER_S = 300
REQUIRED_KEY_FIELDS = ("client_email", "private_key", "project_id")
POINT_CACHE_TTL_S = 6 * 3600
# (lat, lng, day) -> (expires_at monotonic, result); in-flight queries shared by concurrent callers
_point_cache: dict[tuple, tuple[float, dict]] = {}
_point_inflight: dict[tuple, asyncio.Future] = {}

# Failure codes, safe to show to operators and clients.
AUTH_FAILED = "auth_failed"                                   # Google rejected the service-account key
PROJECT_CONFIGURATION_ERROR = "project_configuration_error"   # project not registered, API disabled, missing role
EARTH_ENGINE_UNAVAILABLE = "earth_engine_unavailable"         # network or Earth Engine server error
DATASET_QUERY_FAILED = "dataset_query_failed"                 # the Sentinel-2 query itself failed
TIMEOUT = "timeout"
NO_SUITABLE_OBSERVATION = "no_suitable_observation"
RETRYABLE = (EARTH_ENGINE_UNAVAILABLE, TIMEOUT)
# Only these can fix themselves (or be fixed in the Cloud console) without a redeploy, so only these are retried.
RETRY_INIT = (AUTH_FAILED, PROJECT_CONFIGURATION_ERROR, EARTH_ENGINE_UNAVAILABLE, DATASET_QUERY_FAILED, TIMEOUT)
_PROJECT_HINTS = ("project", "not signed up", "not registered", "has not been used", "disabled", "permission", "forbidden")
_UNAVAILABLE_HINTS = ("unavailable", "internal error", "backend error", "connection", "503", "502", "500")


def classify_error(exc: BaseException, default: str = EARTH_ENGINE_UNAVAILABLE) -> str:
    """Map an Earth Engine / google-auth exception to a failure code. Order matters: most specific first."""
    text = str(exc).lower()
    if isinstance(exc, TimeoutError) or "timed out" in text or "deadline" in text or "timeout" in text:
        return TIMEOUT
    if isinstance(exc, RefreshError) or "invalid_grant" in text or "unauthenticated" in text or "invalid jwt" in text:
        return AUTH_FAILED
    if any(h in text for h in _PROJECT_HINTS):
        return PROJECT_CONFIGURATION_ERROR
    if isinstance(exc, (TransportError, ConnectionError)) or any(h in text for h in _UNAVAILABLE_HINTS):
        return EARTH_ENGINE_UNAVAILABLE
    return default


def _iso_day(epoch_ms) -> str | None:
    return datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc).date().isoformat() if epoch_ms else None


def _first(values):
    return values[0] if values else None


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
        self.configured = False     # a key is set
        self.authenticated = False  # Google accepted the key for the project
        self.initialized = False    # authenticated and the Sentinel-2 dataset answered: the source is usable
        # "available" | "unavailable" | "not_configured"; `error` is a short code, never a raw exception.
        self.status = "not_configured"
        self.error: str | None = None
        self.project: str | None = None
        self.checked_at: str | None = None
        self._next_attempt = 0.0
        self._lock = threading.Lock()
        self._initialize()

    def _fail(self, code: str) -> None:
        self.initialized = False
        self.status, self.error = "unavailable", code

    def _initialize(self) -> None:
        self._next_attempt = time.monotonic() + RETRY_AFTER_S
        self.checked_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.initialized = self.authenticated = False
        # Configured means credentials were supplied: a service-account key, or EE_PROJECT alone for local
        # Application Default Credentials (`gcloud auth application-default login`) or a platform service account.
        self.configured = bool(settings.EE_SERVICE_ACCOUNT_KEY_JSON or settings.EE_PROJECT)
        if not self.configured:
            self.status, self.error = "not_configured", None
            logger.warning("Earth Engine not configured (EE_SERVICE_ACCOUNT_KEY_JSON or EE_PROJECT); Sentinel-2 crop health is unavailable.")
            return
        if not EE_AVAILABLE:
            self._fail("library_missing")
            logger.error("earthengine-api is not installed; Sentinel-2 crop health is unavailable.")
            return

        key = None
        if settings.EE_SERVICE_ACCOUNT_KEY_JSON:
            try:
                key = parse_service_account_key(settings.EE_SERVICE_ACCOUNT_KEY_JSON)
            except CredentialError as e:
                self._fail(e.code)
                logger.error("Earth Engine key rejected (%s); Sentinel-2 crop health is unavailable.", e.code)
                return
        # The Cloud project must be registered for Earth Engine; it may differ from the key's own project.
        self.project = settings.EE_PROJECT or (key and key["project_id"])
        account = key["client_email"] if key else "application default credentials"
        logger.info("Earth Engine credentials configured (%s, project %s); verifying access.", account, self.project)
        try:
            if key:
                ee.Initialize(ee.ServiceAccountCredentials(key["client_email"], key_data=json.dumps(key)), project=self.project)
            else:
                ee.Initialize(project=self.project)
            ee.data.setDeadline(TIMEOUT_S * 1000)
            # Initialize() does not contact the API; one tiny request proves the credentials and project work.
            ee.Number(1).getInfo()
        except Exception as e:
            self._fail(classify_error(e))
            logger.error("Earth Engine authentication failed (%s) for %s in project %s: %s", self.error, account, self.project, e)
            return
        self.authenticated = True
        try:
            # Cheap metadata read (no computation) proving this project can read the Sentinel-2 collection.
            ee.data.getAsset(DATASET)
        except Exception as e:
            self._fail(classify_error(e, DATASET_QUERY_FAILED))
            logger.error("Earth Engine dataset check failed (%s) for %s in project %s: %s", self.error, DATASET, self.project, e)
            return
        self.initialized, self.status, self.error = True, "available", None
        logger.info("Earth Engine ready (project %s, dataset %s).", self.project, DATASET)

    def ensure_initialized(self) -> bool:
        """Retry a failed start-up after a cool-down, so a transient outage does not disable the source for good."""
        with self._lock:
            if not self.initialized and self.error in RETRY_INIT and time.monotonic() >= self._next_attempt:
                self._initialize()
        return self.initialized

    def describe(self) -> dict:
        return {
            "status": self.status, "error": self.error,
            "configured": self.configured, "authenticated": self.authenticated, "available": self.initialized,
            "dataset": DATASET, "project": self.project if self.authenticated else None, "checked_at": self.checked_at,
        }

    @staticmethod
    def _window_stats(geometry, start: str, end: str):
        """Server-side dictionary for one window: median NDVI of clear pixels, scene count, latest acquisition."""
        collection = (ee.ImageCollection(DATASET)
                      .filterBounds(geometry)
                      .filterDate(start, end)
                      .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", MAX_SCENE_CLOUD_PCT)))

        def clear_ndvi(img):
            clear = img.select("SCL").remap(list(CLEAR_SCL_CLASSES), [1] * len(CLEAR_SCL_CLASSES), 0)
            return img.normalizedDifference(["B8", "B4"]).toFloat().rename("NDVI").updateMask(clear)

        # A fully masked NDVI band keeps the composite well-formed when no scene matches, so the
        # result is a null NDVI ("no clear imagery") instead of an Earth Engine error.
        empty = ee.Image.constant(0).toFloat().rename("NDVI").updateMask(0)
        composite = collection.map(clear_ndvi).merge(ee.ImageCollection([empty])).median()
        stats = composite.reduceRegion(reducer=ee.Reducer.mean().combine(ee.Reducer.count(), sharedInputs=True),
                                       geometry=geometry, scale=10, maxPixels=1e9)
        # Lists of zero or one element, so an empty window is not an error.
        latest = collection.limit(1, "system:time_start", False)
        return ee.Dictionary({"ndvi": stats.get("NDVI_mean"), "clear_px": stats.get("NDVI_count"), "count": collection.size(),
                              "latest_ms": collection.aggregate_max("system:time_start"),
                              "latest_id": latest.aggregate_array("system:index"),
                              "latest_cloud_pct": latest.aggregate_array("CLOUDY_PIXEL_PERCENTAGE")})

    @staticmethod
    def _clear_fraction(stats: dict) -> float:
        return min(1.0, (stats.get("clear_px") or 0) / ROI_PIXELS)

    @classmethod
    def _usable_ndvi(cls, stats: dict) -> float | None:
        """NDVI of a window only when enough of the circle had clear pixels; None otherwise."""
        return stats.get("ndvi") if stats.get("ndvi") is not None and cls._clear_fraction(stats) >= MIN_CLEAR_FRACTION else None

    @staticmethod
    def _observation(stats: dict) -> dict | None:
        """Metadata of the newest scene in the window that passed the scene-cloud prefilter."""
        scene_id = _first(stats.get("latest_id"))
        if not scene_id:
            return None
        ms, cloud = stats.get("latest_ms"), _first(stats.get("latest_cloud_pct"))
        return {
            "image_id": f"{DATASET}/{scene_id}",
            "sensed_at": datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat(timespec="seconds") if ms else None,
            "scene_cloud_pct": round(cloud, 1) if cloud is not None else None,
        }

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
        common = {
            "window": {"start": cur_start.isoformat(), "end": today.isoformat()},
            "image_count": current.get("count"),
            "clear_pixel_fraction": round(self._clear_fraction(current), 2),
            "observation": self._observation(current),
            "roi": {"lat": lat, "lng": lng, "radius_m": BUFFER_M},
        }
        value, prev_value = self._usable_ndvi(current), self._usable_ndvi(previous)
        if value is None:
            return {"status": "no_data", "reason": NO_SUITABLE_OBSERVATION, **common}
        return {
            "status": "available",
            "ndvi": round(value, 3),
            "ndvi_previous": round(prev_value, 3) if prev_value is not None else None,
            "change": round(value - prev_value, 3) if prev_value is not None else None,
            "previous_window": {"start": prev_start.isoformat(), "end": cur_start.isoformat()},
            "latest_image_date": _iso_day(current.get("latest_ms")),
            **common,
        }

    async def get_point_crop_health(self, lat: float, lng: float) -> dict:
        """Crop health at a point. Successful and no-imagery answers are cached for POINT_CACHE_TTL_S (a new
        Sentinel-2 pass is at most every few days), and concurrent callers for the same point share one query,
        so a caller that stops waiting (see farm intelligence time budgets) still warms the cache."""
        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            raise ValueError("coordinates out of range")
        key = (round(lat, 3), round(lng, 3), date.today().isoformat())
        cached = _point_cache.get(key)
        if cached and time.monotonic() < cached[0]:
            return cached[1]
        pending = _point_inflight.get(key)
        if pending is None:
            pending = asyncio.ensure_future(self._query_point(lat, lng))
            _point_inflight[key] = pending
            pending.add_done_callback(lambda _f, k=key: _point_inflight.pop(k, None))
        result = await asyncio.shield(pending)
        if result["status"] in ("available", "no_data"):
            if len(_point_cache) > 2000:
                _point_cache.clear()
            _point_cache[key] = (time.monotonic() + POINT_CACHE_TTL_S, result)
        return result

    async def _query_point(self, lat: float, lng: float) -> dict:
        if not await asyncio.to_thread(self.ensure_initialized):
            reason = "not_configured" if self.status == "not_configured" else self.error
            return {"status": "unavailable", "reason": reason, "retryable": reason in RETRYABLE, "provenance": PROVENANCE}
        try:
            result = await asyncio.wait_for(asyncio.to_thread(self._point_ndvi, lat, lng, date.today()), timeout=TIMEOUT_S)
        except Exception as e:
            code = classify_error(e, DATASET_QUERY_FAILED)
            logger.error("Sentinel-2 point query failed (%s): %s", code, e)
            if code in (AUTH_FAILED, PROJECT_CONFIGURATION_ERROR):
                self._fail(code)  # the key or project broke after start-up: report it in /api/sources too
            result = {"status": "unavailable", "reason": code, "retryable": code in RETRYABLE}
        result["provenance"] = PROVENANCE
        return result


earth_engine_service = EarthEngineService()

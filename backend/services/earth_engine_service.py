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
BASELINE_YEARS = 3        # the same 30-day window in each of the previous 3 years
MIN_BASELINE_YEARS = 2    # fewer usable years cannot describe a normal range
HISTORY_WINDOWS = 6       # consecutive 30-day windows for the history series (~6 months)

# Sentinel-1 C-band SAR sees through cloud. Ground Range Detected scenes in Earth Engine are already
# calibrated, terrain-corrected backscatter in dB.
S1_DATASET = "COPERNICUS/S1_GRD"
S1_WINDOW_DAYS = 12       # Sentinel-1 revisits a point within about 6-12 days
# UN-SPIDER Recommended Practice (flood mapping with Sentinel-1 in GEE): a later/earlier VH dB ratio above
# 1.25 marks a strong drop in backscatter, typical of new open water. Here it is applied to the circle's mean,
# so it is a screening signal for standing water, not a flood map.
S1_WATER_RATIO = 1.25
S1_PROVENANCE = {
    "source": "Sentinel-1 via Google Earth Engine (COPERNICUS/S1_GRD)",
    "source_url": "https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD",
    "dataset": S1_DATASET,
    "provider": "Copernicus / ESA",
    "processing": "Ground Range Detected, IW mode, calibrated and terrain-corrected backscatter (dB)",
    "signal": "Radar backscatter (VV, VH), not a measurement of soil moisture or crop health",
    "kind": "satellite_observation",
    "resolution": "10 m (averaged over a 250 m radius)",
    "notes": "Radar works through clouds. A strong drop in VH backscatter can indicate standing water; VH also changes with "
             "canopy growth, harvest and tillage, so changes are shown, not interpreted as crop condition.",
    "references": [{"source": "UN-SPIDER Recommended Practice: flood mapping and damage assessment using Sentinel-1 SAR data in GEE",
                    "url": "https://www.un-spider.org/advisory-support/recommended-practices/recommended-practice-google-earth-engine-flood-mapping"}],
}
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


def _round(v, digits: int = 3):
    return round(v, digits) if v is not None else None


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
        self.sar_available = False  # Sentinel-1 answered its metadata check
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
        try:
            # Radar is optional on top of Sentinel-2: without it, crop health still works and radar says "unavailable".
            ee.data.getAsset(S1_DATASET)
            self.sar_available = True
        except Exception as e:
            self.sar_available = False
            logger.warning("Sentinel-1 dataset check failed (%s); radar signals are unavailable: %s", classify_error(e, DATASET_QUERY_FAILED), e)

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
            "dataset": DATASET, "radar_available": self.sar_available,
            "project": self.project if self.authenticated else None, "checked_at": self.checked_at,
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

    @staticmethod
    def _sar_stats(geometry, start: str, end: str):
        """Mean VV/VH backscatter (dB) per orbit direction; ascending and descending passes see the field at different
        angles, so only like with like is compared."""
        collection = (ee.ImageCollection(S1_DATASET).filterBounds(geometry).filterDate(start, end)
                      .filter(ee.Filter.eq("instrumentMode", "IW"))
                      .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
                      .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VH")))
        empty = ee.Image.constant([0, 0]).toFloat().rename(["VV", "VH"]).updateMask(0)

        def per_pass(orbit_pass):
            c = collection.filter(ee.Filter.eq("orbitProperties_pass", orbit_pass))
            mean = c.select(["VV", "VH"]).map(lambda i: i.toFloat()).merge(ee.ImageCollection([empty])).mean()
            stats = mean.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=10, maxPixels=1e9)
            return ee.Dictionary({"vv_db": stats.get("VV"), "vh_db": stats.get("VH"), "count": c.size(),
                                  "latest_ms": c.aggregate_max("system:time_start")})

        return ee.Dictionary({"ASCENDING": per_pass("ASCENDING"), "DESCENDING": per_pass("DESCENDING")})

    @staticmethod
    def _sar_summary(current: dict | None, previous: dict | None, window: dict, previous_window: dict) -> dict:
        """Picks the orbit pass seen in both windows (else the one seen now) and reports levels and change."""
        current, previous = current or {}, previous or {}

        def usable(d):
            return bool(d) and d.get("count") and isinstance(d.get("vh_db"), (int, float)) and isinstance(d.get("vv_db"), (int, float))

        both = [p for p in ("ASCENDING", "DESCENDING") if usable(current.get(p)) and usable(previous.get(p))]
        now_only = [p for p in ("ASCENDING", "DESCENDING") if usable(current.get(p))]
        candidates = both or now_only
        if not candidates:
            return {"status": "no_data", "reason": "no_radar_scene", "window": window, "provenance": S1_PROVENANCE}
        orbit = max(candidates, key=lambda p: current[p].get("latest_ms") or 0)
        cur = current[orbit]
        out = {"status": "available", "orbit_pass": orbit, "window": window, "image_count": cur["count"],
               "latest_image_date": _iso_day(cur.get("latest_ms")),
               "vv_db": round(cur["vv_db"], 2), "vh_db": round(cur["vh_db"], 2),
               "previous_window": None, "vv_db_previous": None, "vh_db_previous": None, "vh_change_db": None, "water_signal": None,
               "provenance": S1_PROVENANCE}
        if orbit in both:
            prev = previous[orbit]
            out.update(previous_window=previous_window, vv_db_previous=round(prev["vv_db"], 2), vh_db_previous=round(prev["vh_db"], 2),
                       vh_change_db=round(cur["vh_db"] - prev["vh_db"], 2),
                       water_signal=prev["vh_db"] < 0 and cur["vh_db"] / prev["vh_db"] > S1_WATER_RATIO)
        return out

    def _baseline(self, stats: dict, value: float | None, today: date) -> dict:
        years = []
        for y in range(1, BASELINE_YEARS + 1):
            w = stats.get(f"baseline_{y}") or {}
            years.append({"year": (today - timedelta(days=365 * y)).year, "ndvi": _round(self._usable_ndvi(w)),
                          "clear_pixel_fraction": round(self._clear_fraction(w), 2), "image_count": w.get("count")})
        values = [y["ndvi"] for y in years if y["ndvi"] is not None]
        if len(values) < MIN_BASELINE_YEARS:
            return {"status": "insufficient_data", "years": years, "minimum_years": MIN_BASELINE_YEARS}
        lo, hi = min(values), max(values)
        position = None if value is None else "below_range" if value < lo else "above_range" if value > hi else "within_range"
        return {"status": "available", "years": years, "mean": round(sum(values) / len(values), 3), "min": lo, "max": hi,
                "position": position, "minimum_years": MIN_BASELINE_YEARS,
                "method": "Same 30-day window in each previous year; range of the usable years"}

    def _point_series(self, lat: float, lng: float, today: date) -> dict:
        geometry = ee.Geometry.Point([lng, lat]).buffer(BUFFER_M)
        windows = [(today - timedelta(days=WINDOW_DAYS * (i + 1)), today - timedelta(days=WINDOW_DAYS * i)) for i in range(HISTORY_WINDOWS)]
        stats = ee.Dictionary({str(i): self._window_stats(geometry, s.isoformat(), e.isoformat()) for i, (s, e) in enumerate(windows)}).getInfo()
        series = []
        for i, (start, end) in reversed(list(enumerate(windows))):
            w = stats.get(str(i)) or {}
            series.append({"start": start.isoformat(), "end": end.isoformat(), "ndvi": _round(self._usable_ndvi(w)),
                           "clear_pixel_fraction": round(self._clear_fraction(w), 2), "image_count": w.get("count"),
                           "latest_image_date": _iso_day(w.get("latest_ms"))})
        usable = sum(p["ndvi"] is not None for p in series)
        return {"status": "available" if usable >= 2 else "insufficient_data", "series": series, "usable_windows": usable,
                "window_days": WINDOW_DAYS, "roi": {"lat": lat, "lng": lng, "radius_m": BUFFER_M}}

    def _point_ndvi(self, lat: float, lng: float, today: date) -> dict:
        geometry = ee.Geometry.Point([lng, lat]).buffer(BUFFER_M)
        cur_start = today - timedelta(days=WINDOW_DAYS)
        prev_start = cur_start - timedelta(days=WINDOW_DAYS)
        sar_start = today - timedelta(days=S1_WINDOW_DAYS)
        sar_prev_start = sar_start - timedelta(days=S1_WINDOW_DAYS)
        # Every window in one request: one round trip to the Earth Engine API.
        windows = {
            "current": self._window_stats(geometry, cur_start.isoformat(), today.isoformat()),
            "previous": self._window_stats(geometry, prev_start.isoformat(), cur_start.isoformat()),
        }
        sar_enabled = getattr(self, "sar_available", False)
        if sar_enabled:
            windows["sar_current"] = self._sar_stats(geometry, sar_start.isoformat(), today.isoformat())
            windows["sar_previous"] = self._sar_stats(geometry, sar_prev_start.isoformat(), sar_start.isoformat())
        for y in range(1, BASELINE_YEARS + 1):
            shift = timedelta(days=365 * y)
            windows[f"baseline_{y}"] = self._window_stats(geometry, (cur_start - shift).isoformat(), (today - shift).isoformat())
        stats = ee.Dictionary(windows).getInfo()
        current, previous = stats["current"], stats["previous"]
        value, prev_value = self._usable_ndvi(current), self._usable_ndvi(previous)
        common = {
            "window": {"start": cur_start.isoformat(), "end": today.isoformat()},
            "image_count": current.get("count"),
            "clear_pixel_fraction": round(self._clear_fraction(current), 2),
            "observation": self._observation(current),
            "roi": {"lat": lat, "lng": lng, "radius_m": BUFFER_M},
            "baseline": self._baseline(stats, value, today),
            # Radar is reported even when clouds hide the field from Sentinel-2.
            "sar": self._sar_summary(stats.get("sar_current"), stats.get("sar_previous"),
                                     {"start": sar_start.isoformat(), "end": today.isoformat()},
                                     {"start": sar_prev_start.isoformat(), "end": sar_start.isoformat()})
            if sar_enabled else {"status": "unavailable", "reason": "radar_dataset_unavailable", "provenance": S1_PROVENANCE},
        }
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
        """Crop health at a point: NDVI now and 30 days earlier, the same-season baseline and Sentinel-1 radar."""
        return await self._cached("health", lat, lng, self._point_ndvi)

    async def get_point_history(self, lat: float, lng: float) -> dict:
        """NDVI for the last HISTORY_WINDOWS consecutive 30-day windows (null where no clear observation)."""
        return await self._cached("history", lat, lng, self._point_series)

    async def _cached(self, kind: str, lat: float, lng: float, query) -> dict:
        """Successful and no-imagery answers are cached for POINT_CACHE_TTL_S (a new pass is at most every few days),
        and concurrent callers for the same point share one query, so a caller that stops waiting (see farm
        intelligence time budgets) still warms the cache."""
        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            raise ValueError("coordinates out of range")
        key = (kind, round(lat, 3), round(lng, 3), date.today().isoformat())
        cached = _point_cache.get(key)
        if cached and time.monotonic() < cached[0]:
            return cached[1]
        pending = _point_inflight.get(key)
        if pending is None:
            pending = asyncio.ensure_future(self._query(query, lat, lng))
            _point_inflight[key] = pending
            pending.add_done_callback(lambda _f, k=key: _point_inflight.pop(k, None))
        result = await asyncio.shield(pending)
        if result["status"] in ("available", "no_data", "insufficient_data"):
            if len(_point_cache) > 2000:
                _point_cache.clear()
            _point_cache[key] = (time.monotonic() + POINT_CACHE_TTL_S, result)
        return result

    async def _query(self, query, lat: float, lng: float) -> dict:
        if not await asyncio.to_thread(self.ensure_initialized):
            reason = "not_configured" if self.status == "not_configured" else self.error
            return {"status": "unavailable", "reason": reason, "retryable": reason in RETRYABLE, "provenance": PROVENANCE}
        try:
            result = await asyncio.wait_for(asyncio.to_thread(query, lat, lng, date.today()), timeout=TIMEOUT_S)
        except Exception as e:
            code = classify_error(e, DATASET_QUERY_FAILED)
            logger.error("Sentinel point query failed (%s): %s", code, e)
            if code in (AUTH_FAILED, PROJECT_CONFIGURATION_ERROR):
                self._fail(code)  # the key or project broke after start-up: report it in /api/sources too
            result = {"status": "unavailable", "reason": code, "retryable": code in RETRYABLE}
        result["provenance"] = PROVENANCE
        return result


earth_engine_service = EarthEngineService()

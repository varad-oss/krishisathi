"""Soil properties from ISRIC SoilGrids 2.0 (modelled, 250 m resolution).

SoilGrids values are statistical predictions, not a field soil test. The response
always says so, and recommends a Soil Health Card test for decisions.
"""
import asyncio
import logging
import time
from datetime import datetime, timezone

import httpx

from config import settings
from core.cache import cache_get, cache_set

logger = logging.getLogger(__name__)

BASE_URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"
PROPERTIES = ["phh2o", "soc", "nitrogen", "clay", "sand"]
DEPTHS = {"0-5cm": 5, "5-15cm": 10}  # label -> thickness (cm), weighted to a 0-15 cm average
CACHE_TTL_SECONDS = 24 * 3600

PROVENANCE = {
    "source": "ISRIC SoilGrids 2.0",
    "source_url": "https://soilgrids.org/",
    "kind": "model",
    "resolution": "250 m",
    "depth": "0-15 cm",
    "notes": "Predicted from global soil models, not measured on your field. Use a Soil Health Card lab test before changing fertilizer or amendments.",
}
SHC = {"name": "Soil Health Card scheme ratings (Govt. of India)", "url": "https://soilhealth.dac.gov.in/"}

RETRY_DELAY_SECONDS = 1.0
SHARED_CACHE_TTL_SECONDS = 7 * 24 * 3600
RATE_LIMIT_BACKOFF_SECONDS = 60

# key -> (expires_at monotonic, value)
_cache: dict[tuple, tuple[float, dict]] = {}
_inflight: dict[tuple, asyncio.Future] = {}


def rate_ph(ph: float | None) -> str | None:
    if ph is None:
        return None
    if ph < 5.5:
        return "strongly_acidic"
    if ph < 6.5:
        return "acidic"
    if ph <= 7.5:
        return "neutral"
    if ph <= 8.5:
        return "alkaline"
    return "strongly_alkaline"


def rate_organic_carbon(oc_pct: float | None) -> str | None:
    """Soil Health Card organic-carbon classes: <0.5 % low, 0.5–0.75 % medium, >0.75 % high."""
    if oc_pct is None:
        return None
    if oc_pct < 0.5:
        return "low"
    if oc_pct <= 0.75:
        return "medium"
    return "high"


def parse_soilgrids(data: dict) -> dict:
    layers = {layer.get("name"): layer for layer in (data.get("properties") or {}).get("layers", [])}
    values: dict[str, float | None] = {}
    for name in PROPERTIES:
        layer = layers.get(name)
        if not layer:
            values[name] = None
            continue
        d_factor = (layer.get("unit_measure") or {}).get("d_factor") or 1
        total, weight = 0.0, 0
        for depth in layer.get("depths", []):
            thickness = DEPTHS.get(depth.get("label"))
            mean = (depth.get("values") or {}).get("mean")
            if thickness and isinstance(mean, (int, float)):
                total += (mean / d_factor) * thickness
                weight += thickness
        values[name] = round(total / weight, 2) if weight else None

    if all(v is None for v in values.values()):
        return {"status": "no_data"}

    soc_g_kg = values["soc"]
    oc_pct = round(soc_g_kg / 10, 2) if soc_g_kg is not None else None
    return {
        "status": "available",
        "properties": {
            "ph": values["phh2o"],
            "organic_carbon_pct": oc_pct,
            "total_nitrogen_g_per_kg": values["nitrogen"],
            # after d_factor: clay/sand are % (g/100 g), soc is g/kg, nitrogen is g/kg
            "clay_pct": values["clay"],
            "sand_pct": values["sand"],
        },
        "ratings": {
            "ph": rate_ph(values["phh2o"]),
            "organic_carbon": rate_organic_carbon(oc_pct),
            "source": SHC,
        },
    }


def _failure(reason: str, retryable: bool = True) -> dict:
    return {"status": "unavailable", "reason": reason, "retryable": retryable, "provenance": PROVENANCE}


async def _fetch(lat: float, lng: float) -> dict:
    """One SoilGrids query, with one retry for transient failures. Never raises."""
    params = [("lon", lng), ("lat", lat), ("value", "mean")]
    params += [("property", p) for p in PROPERTIES] + [("depth", d) for d in DEPTHS]
    reason = "upstream_error"
    for attempt in range(2):
        try:
            async with httpx.AsyncClient(timeout=settings.EXTERNAL_API_TIMEOUT_SECONDS + 5) as client:
                response = await client.get(BASE_URL, params=params)
        except httpx.TimeoutException:
            reason = "timeout"
        except httpx.HTTPError as e:
            logger.warning("SoilGrids network error at (%.3f, %.3f): %s", lat, lng, e)
            reason = "network_error"
        except Exception as e:  # never let an unexpected client error escape as a 500
            logger.exception("SoilGrids request failed unexpectedly: %s", e)
            reason = "unknown_error"
        else:
            if response.status_code == 429:
                # SoilGrids is a fair-use service (about 5 queries per minute per client); retrying now only makes it worse.
                logger.warning("SoilGrids rate limit reached")
                return _failure("rate_limited")
            if response.status_code >= 500:
                logger.warning("SoilGrids HTTP %s at (%.3f, %.3f)", response.status_code, lat, lng)
                reason = "upstream_error"
            elif response.status_code >= 400:
                logger.error("SoilGrids rejected the query (HTTP %s): %s", response.status_code, response.text[:200])
                return _failure("request_rejected", retryable=False)
            else:
                try:
                    result = parse_soilgrids(response.json())
                except (ValueError, TypeError, AttributeError) as e:
                    logger.error("SoilGrids response could not be parsed: %s", e)
                    return _failure("bad_response")
                if result["status"] == "no_data":
                    # SoilGrids masks built-up land and water; a city-centre point often has no prediction.
                    return {"status": "no_data", "reason": "no_coverage", "provenance": PROVENANCE}
                result["provenance"] = {**PROVENANCE, "retrieved_at": datetime.now(timezone.utc).isoformat()}
                return result
        if attempt == 0:
            await asyncio.sleep(RETRY_DELAY_SECONDS)
    logger.warning("SoilGrids unavailable at (%.3f, %.3f): %s", lat, lng, reason)
    return _failure(reason)


class SoilService:
    async def get_soil(self, lat: float, lng: float) -> dict:
        """Returns an availability-tagged dict with a specific `reason` on failure; never raises for upstream failures.

        Successful and no-coverage answers are cached (in-process and, when configured, Redis) because soil
        predictions do not change. A rate-limit answer is cached briefly so repeated page loads do not keep
        hitting the fair-use limit. Concurrent requests for the same point share one upstream call.
        """
        key = (round(lat, 2), round(lng, 2))
        cached = _cache.get(key)
        if cached and time.monotonic() < cached[0]:
            return cached[1]
        redis_key = f"cache:soil:v2:{key[0]}:{key[1]}"
        shared = await cache_get(redis_key)
        if shared:
            _remember(key, shared, CACHE_TTL_SECONDS)
            return shared

        pending = _inflight.get(key)
        if pending is None:
            pending = asyncio.ensure_future(_fetch(lat, lng))
            _inflight[key] = pending
            pending.add_done_callback(lambda _f, k=key: _inflight.pop(k, None))
        result = await asyncio.shield(pending)

        if result["status"] in ("available", "no_data"):
            _remember(key, result, CACHE_TTL_SECONDS)
            await cache_set(redis_key, result, SHARED_CACHE_TTL_SECONDS)
        elif result.get("reason") == "rate_limited":
            _remember(key, result, RATE_LIMIT_BACKOFF_SECONDS)
        return result


def _remember(key: tuple, value: dict, ttl: int) -> None:
    if len(_cache) > 2000:
        _cache.clear()
    _cache[key] = (time.monotonic() + ttl, value)


soil_service = SoilService()

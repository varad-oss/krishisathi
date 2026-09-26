"""Soil properties from ISRIC SoilGrids 2.0 (modelled, 250 m resolution).

SoilGrids values are statistical predictions, not a field soil test. The response
always says so, and recommends a Soil Health Card test for decisions.
"""
import logging
import time
from datetime import datetime, timezone

import httpx

from config import settings

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

_cache: dict[tuple, tuple[float, dict]] = {}


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


class SoilService:
    async def get_soil(self, lat: float, lng: float) -> dict:
        """Returns an availability-tagged dict; never raises for upstream failures."""
        key = (round(lat, 2), round(lng, 2))
        cached = _cache.get(key)
        if cached and time.monotonic() - cached[0] < CACHE_TTL_SECONDS:
            return cached[1]

        params = [("lon", lng), ("lat", lat), ("value", "mean")]
        params += [("property", p) for p in PROPERTIES] + [("depth", d) for d in DEPTHS]
        try:
            async with httpx.AsyncClient(timeout=settings.EXTERNAL_API_TIMEOUT_SECONDS + 5) as client:
                response = await client.get(BASE_URL, params=params)
                response.raise_for_status()
                result = parse_soilgrids(response.json())
        except Exception as e:
            logger.warning("SoilGrids unavailable: %s", e)
            return {"status": "unavailable", "reason": "upstream_error", "provenance": PROVENANCE}

        result["provenance"] = {**PROVENANCE, "retrieved_at": datetime.now(timezone.utc).isoformat()}
        if len(_cache) > 2000:
            _cache.clear()
        _cache[key] = (time.monotonic(), result)
        return result


soil_service = SoilService()

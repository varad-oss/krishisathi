"""Topsoil water status: modelled soil moisture read against modelled soil texture.

Open-Meteo gives volumetric soil moisture (m³/m³) at 3-9 cm. Whether a value is "dry" or "wet" depends on
the soil, so the field capacity (-33 kPa) and wilting point (-1500 kPa) of the SoilGrids texture are
estimated with the Saxton & Rawls (2006) pedotransfer equations, and the moisture is expressed as the
fraction of plant-available water. Following FAO-56, water is treated as readily available down to a
depletion of p = 0.5 (a common value across crops), so below half of the available water the topsoil is
reported "dry"; at or above field capacity it is "wet".

Both inputs are models (weather model and global soil map), so the result is always low confidence.
"""
from typing import Optional

REFERENCES = [
    {"source": "Saxton & Rawls (2006), Soil Sci. Soc. Am. J. 70:1569-1578", "url": "https://doi.org/10.2136/sssaj2005.0117"},
    {"source": "FAO Irrigation and Drainage Paper 56, Chapter 8 (depletion fraction p)", "url": "https://www.fao.org/4/x0490e/x0490e0e.htm"},
]
OC_TO_OM = 1.724  # van Bemmelen factor: organic matter = organic carbon x 1.724
READILY_AVAILABLE_FRACTION = 0.5


def water_limits(sand_pct: float, clay_pct: float, organic_carbon_pct: float) -> tuple[float, float]:
    """(wilting point, field capacity) in m³/m³ from Saxton & Rawls (2006), equations 1 and 2."""
    s, c = sand_pct / 100, clay_pct / 100
    om = organic_carbon_pct * OC_TO_OM
    t1500 = -0.024 * s + 0.487 * c + 0.006 * om + 0.005 * (s * om) - 0.013 * (c * om) + 0.068 * (s * c) + 0.031
    wp = t1500 + (0.14 * t1500 - 0.02)
    t33 = -0.251 * s + 0.195 * c + 0.011 * om + 0.006 * (s * om) - 0.027 * (c * om) + 0.452 * (s * c) + 0.299
    fc = t33 + (1.283 * t33 ** 2 - 0.374 * t33 - 0.015)
    return wp, fc


def topsoil_water(moisture: Optional[float], soil: dict) -> dict:
    """{"status": dry | adequate | wet | unavailable, "available_water_fraction", "reason"} — never guessed."""
    props = (soil.get("properties") or {}) if soil.get("status") == "available" else {}
    sand, clay, oc = props.get("sand_pct"), props.get("clay_pct"), props.get("organic_carbon_pct")
    if not isinstance(moisture, (int, float)):
        return {"status": "unavailable", "reason": "soil_moisture_unavailable"}
    if not all(isinstance(v, (int, float)) for v in (sand, clay, oc)):
        return {"status": "unavailable", "reason": "soil_texture_unavailable"}
    wp, fc = water_limits(sand, clay, oc)
    if fc - wp <= 0.01:  # outside the equations' useful range (e.g. extreme sands); do not divide by ~0
        return {"status": "unavailable", "reason": "texture_out_of_range"}
    fraction = (moisture - wp) / (fc - wp)
    status = "wet" if fraction >= 1 else "dry" if fraction < READILY_AVAILABLE_FRACTION else "adequate"
    return {
        "status": status,
        "available_water_fraction": round(fraction, 2),
        "field_capacity": round(fc, 3),
        "wilting_point": round(wp, 3),
        "confidence": "low",
    }

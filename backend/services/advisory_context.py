"""Builds the DATA blocks that ground advisory answers.

Sources are fetched concurrently; each one is either included with its provenance
or explicitly marked UNAVAILABLE, and the list of sources actually used is returned
so the UI can show "Based on: ...".
"""
import asyncio
import math

from models.exceptions import ServiceUnavailableException
from services import agro_rules
from services.disease_reference_service import disease_reference_service
from services.kvk_service import kvk_service
from services.persistence_service import persistence_service
from services.soil_service import soil_service
from services.weather_service import weather_service

NEARBY_OUTBREAK_KM = 100


def _haversine(lat1, lon1, lat2, lon2):
    r = 6371.0
    d_lat, d_lon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


async def _weather(lat, lng):
    try:
        return await weather_service.get_conditions(lat, lng)
    except ServiceUnavailableException:
        return None


async def _outbreaks(lat, lng):
    try:
        found = await persistence_service.get_outbreaks()
    except Exception:
        return None
    return [o for o in found if _haversine(lat, lng, o["lat"], o["lng"]) <= NEARBY_OUTBREAK_KM]


def _weather_text(c: dict) -> str:
    cur = c["current"]
    lines = [
        f"[DATA: weather — Open-Meteo numerical model estimate, valid at {cur.get('valid_at')} local time]",
        f"Now: {cur.get('temperature_c')} °C, humidity {cur.get('humidity_pct')} %, wind {cur.get('wind_kmh')} km/h, "
        f"precipitation {cur.get('precipitation_mm')} mm, soil moisture 3-9 cm {cur.get('soil_moisture_3_9cm')} m³/m³",
        "Forecast:",
    ]
    for d in c["daily"][:5]:
        lines.append(
            f"- {d['date']}: {d.get('temp_min_c')}–{d.get('temp_max_c')} °C, rain {d.get('precipitation_mm')} mm "
            f"(chance {d.get('precipitation_probability_pct')} %), mean humidity {d.get('humidity_mean_pct')} %, ET0 {d.get('et0_mm')} mm"
        )
    insights = agro_rules.evaluate(c)
    if insights:
        lines.append("Rule-based alerts: " + "; ".join(f"{i['id']} ({i['severity']}, {i.get('date') or 'now'}, {i['params']})" for i in insights))
    return "\n".join(lines)


def _soil_text(s: dict) -> str:
    p, r = s["properties"], s["ratings"]
    return (
        "[DATA: soil — ISRIC SoilGrids modelled estimate for 0-15 cm, 250 m resolution, NOT a field test]\n"
        f"pH {p.get('ph')} ({r.get('ph')}), organic carbon {p.get('organic_carbon_pct')} % ({r.get('organic_carbon')}), "
        f"clay {p.get('clay_pct')} %, sand {p.get('sand_pct')} %"
    )


async def build_context(lat: float, lng: float, crop: str | None) -> tuple[str, list[dict]]:
    weather, soil, outbreaks = await asyncio.gather(_weather(lat, lng), soil_service.get_soil(lat, lng), _outbreaks(lat, lng))
    kvk = kvk_service.get_nearest_kvk(lat, lng)
    blocks, sources = [], []

    if weather:
        blocks.append(_weather_text(weather))
        sources.append({"id": "weather", "status": "used"})
    else:
        blocks.append("[UNAVAILABLE: weather — the weather service could not be reached]")
        sources.append({"id": "weather", "status": "unavailable"})

    if soil.get("status") == "available":
        blocks.append(_soil_text(soil))
        sources.append({"id": "soil", "status": "used"})
    else:
        blocks.append("[UNAVAILABLE: soil properties]")
        sources.append({"id": "soil", "status": "unavailable"})

    if outbreaks is None:
        blocks.append("[UNAVAILABLE: community outbreak reports]")
        sources.append({"id": "outbreaks", "status": "unavailable"})
    elif outbreaks:
        lines = [f"- {o['disease']} ({o['severity']}), {o['report_count']} reports, {o['location']}" for o in outbreaks[:5]]
        blocks.append("[DATA: nearby outbreak clusters — aggregated AI-classified farmer photos, not lab-confirmed]\n" + "\n".join(lines))
        sources.append({"id": "outbreaks", "status": "used"})
    else:
        blocks.append(f"[DATA: no active outbreak clusters reported within {NEARBY_OUTBREAK_KM} km]")
        sources.append({"id": "outbreaks", "status": "none_found"})

    reference = disease_reference_service.get_grounding_context(crop, None) if crop else ""
    if reference and not reference.startswith("No specific"):
        blocks.append("[DATA: verified disease reference — ICAR institutes]\n" + reference)
        sources.append({"id": "disease_reference", "status": "used"})

    if kvk:
        blocks.append(f"[DATA: nearest Krishi Vigyan Kendra (approximate location)] {kvk['name']}, {kvk.get('district')}, about {round(kvk['distance_km'])} km")
        sources.append({"id": "kvk", "status": "used"})

    blocks.append("[NOT INCLUDED: satellite crop health is not part of chat answers]")
    return "\n\n".join(blocks), sources

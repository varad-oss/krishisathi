"""Crop trade-offs from verified sources only.

Shown per crop: typical seasonal water need (FAO), typical season length (FAO-56 Table 11), how many curated ICAR
disease entries cover it, and nearby AI-classified disease clusters. Market prices, input costs and profit have no
connected verified source, so they are reported as unavailable rather than estimated. Crops are listed, never ranked.
"""
from services.crop_stage import CALENDARS, REFERENCE as FAO56
from services.crops import CROPS
from services.disease_reference_service import disease_reference_service
from services.kvk_service import haversine_km
from services.persistence_service import nearby_outbreaks, persistence_service
from services.regions import INDIAN_STATES

# FAO, Irrigation Water Management Training Manual No. 3 (Brouwer & Heibloem, 1986), Chapter 3, Table 13:
# approximate seasonal crop water needs (mm). The rice value excludes water lost to flooding and percolation.
WATER_NEED_MM: dict[str, tuple[int, int]] = {
    "Wheat": (450, 650), "Rice": (450, 700), "Maize": (500, 800), "Sorghum": (450, 650), "Pearl millet": (450, 650),
    "Finger millet": (450, 650), "Soybean": (450, 700), "Groundnut": (500, 700), "Cotton": (700, 1300),
    "Sugarcane": (1500, 2500), "Potato": (500, 700), "Tomato": (400, 800), "Onion": (350, 550),
}
WATER_SOURCE = {"source": "FAO Irrigation Water Management Training Manual No. 3, Table 13 (Brouwer & Heibloem, 1986)",
                "url": "https://www.fao.org/4/s2022e/s2022e00.htm"}
REGION_MAX_KM = 400  # beyond this from every state reference point, no "commonly grown" list is assumed


def _nearest_state(lat: float, lng: float) -> dict | None:
    best = min(INDIAN_STATES, key=lambda s: haversine_km(lat, lng, s["lat"], s["lng"]))
    return best if haversine_km(lat, lng, best["lat"], best["lng"]) <= REGION_MAX_KM else None


async def crop_options(lat: float, lng: float, crop: str | None) -> dict:
    state = _nearest_state(lat, lng)
    names = ([crop] if crop else []) + [c for c in (state["primary_crops"] if state else CROPS) if c != crop]
    try:
        outbreaks = await persistence_service.get_outbreaks()
    except Exception:
        outbreaks = None

    rows = []
    for name in names:
        water = WATER_NEED_MM.get(name)
        calendar = CALENDARS.get(name)
        rows.append({
            "crop": name,
            "group": CROPS.get(name),
            "is_current": name == crop,
            "water_need_mm": {"min": water[0], "max": water[1]} if water else None,
            "season_length_days": sum(calendar[0]) if calendar else None,
            "season_calendar": calendar[1] if calendar else None,
            "verified_disease_entries": len(disease_reference_service.entries_for(name)),
            "nearby_disease_clusters": len(nearby_outbreaks(outbreaks, lat, lng, name)) if outbreaks is not None else None,
        })
    return {
        "basis": "farm_crop_and_state_list" if state else "all_supported_crops",
        "state": state["code"] if state else None,
        "crops": rows,
        "market": {"status": "unavailable", "reason": "no_market_data_source"},
        "input_costs": {"status": "unavailable", "reason": "no_verified_cost_data"},
        "ranking": None,
        "sources": {"water_need": WATER_SOURCE, "season_length": {"source": FAO56["source"], "url": FAO56["url"]},
                    "disease_entries": {"source": "KrishiSathi curated reference (ICAR institutes)"},
                    "nearby_clusters": {"source": "KrishiSathi community reports", "kind": "ai_classified_user_reports"},
                    "state_list": {"source": "KrishiSathi deployment configuration (typical crops per state)"} if state else None},
    }

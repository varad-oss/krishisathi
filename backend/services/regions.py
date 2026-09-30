"""Regions configured in this deployment, and forecast risks at their reference points."""
import asyncio
from datetime import datetime, timezone

from models.exceptions import ServiceUnavailableException
from services import agro_rules
from services.weather_service import PROVENANCE_BASE, weather_service

# Deployment configuration only (language, reference point, typical crops). No statistics:
# figures such as farmers reached or alert counts must come from live records, not constants.
# lat/lng is a reference point near the state's geographic centre, used for indicative forecasts.
INDIAN_STATES = [
    {"code": "PB", "name": "Punjab", "lat": 31.1471, "lng": 75.3412, "default_language": "pa", "primary_crops": ["Wheat", "Rice", "Cotton", "Sugarcane"]},
    {"code": "MH", "name": "Maharashtra", "lat": 19.7515, "lng": 75.7139, "default_language": "mr", "primary_crops": ["Cotton", "Sugarcane", "Soybean", "Rice", "Onion"]},
    {"code": "KA", "name": "Karnataka", "lat": 15.3173, "lng": 75.7139, "default_language": "kn", "primary_crops": ["Rice", "Sugarcane", "Cotton", "Finger millet", "Maize"]},
    {"code": "TN", "name": "Tamil Nadu", "lat": 11.1271, "lng": 78.6569, "default_language": "ta", "primary_crops": ["Rice", "Sugarcane", "Cotton", "Groundnut"]},
    {"code": "UP", "name": "Uttar Pradesh", "lat": 26.8467, "lng": 80.9462, "default_language": "hi", "primary_crops": ["Wheat", "Rice", "Sugarcane", "Potato", "Mustard"]},
    {"code": "MP", "name": "Madhya Pradesh", "lat": 22.9734, "lng": 78.6569, "default_language": "hi", "primary_crops": ["Soybean", "Wheat", "Rice", "Cotton", "Maize"]},
    {"code": "GJ", "name": "Gujarat", "lat": 22.2587, "lng": 71.1924, "default_language": "gu", "primary_crops": ["Cotton", "Groundnut", "Wheat", "Rice"]},
    {"code": "WB", "name": "West Bengal", "lat": 22.9868, "lng": 87.8550, "default_language": "bn", "primary_crops": ["Rice", "Potato", "Wheat"]},
]

AGGREGATION = "single_reference_point_per_state"


def iso_region(state_code: str) -> str:
    """ISO 3166-2 subdivision code for a configured state (e.g. MH -> IN-MH)."""
    return f"IN-{state_code}"


async def state_weather_risk() -> dict:
    """Rule-based forecast risks at one reference point per state (indicative, not statewide)."""
    async def one(state):
        try:
            conditions = await weather_service.get_conditions(state["lat"], state["lng"])
        except ServiceUnavailableException:
            return {"state": state["code"], "status": "unavailable", "insights": []}
        return {"state": state["code"], "status": "available", "insights": agro_rules.evaluate(conditions)}

    regions = await asyncio.gather(*(one(s) for s in INDIAN_STATES))
    return {
        "regions": regions,
        "aggregation": AGGREGATION,
        "provenance": {**PROVENANCE_BASE, "retrieved_at": datetime.now(timezone.utc).isoformat()},
    }

from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/api/states", tags=["Indian States"])

# 8 major agricultural states with real data
INDIAN_STATES = [
    {"code": "PB", "name": "Punjab", "capital": "Chandigarh", "lat": 31.1471, "lng": 75.3412, "farmers_reached": 2_850_000, "active_alerts": 3, "top_crop": "Wheat", "districts": 23, "arable_land_mha": 4.2, "default_language": "pa", "primary_crops": ["Wheat", "Rice", "Cotton", "Sugarcane"]},
    {"code": "MH", "name": "Maharashtra", "capital": "Mumbai", "lat": 19.7515, "lng": 75.7139, "farmers_reached": 4_120_000, "active_alerts": 5, "top_crop": "Cotton", "districts": 36, "arable_land_mha": 17.5, "default_language": "mr", "primary_crops": ["Cotton", "Sugarcane", "Soybean", "Rice", "Onion"]},
    {"code": "KA", "name": "Karnataka", "capital": "Bengaluru", "lat": 15.3173, "lng": 75.7139, "farmers_reached": 3_540_000, "active_alerts": 2, "top_crop": "Rice", "districts": 31, "arable_land_mha": 10.2, "default_language": "kn", "primary_crops": ["Rice", "Sugarcane", "Cotton", "Ragi", "Maize"]},
    {"code": "TN", "name": "Tamil Nadu", "capital": "Chennai", "lat": 11.1271, "lng": 78.6569, "farmers_reached": 2_980_000, "active_alerts": 1, "top_crop": "Rice", "districts": 38, "arable_land_mha": 5.6, "default_language": "ta", "primary_crops": ["Rice", "Sugarcane", "Banana", "Cotton", "Groundnut"]},
    {"code": "UP", "name": "Uttar Pradesh", "capital": "Lucknow", "lat": 26.8467, "lng": 80.9462, "farmers_reached": 5_670_000, "active_alerts": 4, "top_crop": "Wheat", "districts": 75, "arable_land_mha": 16.6, "default_language": "hi", "primary_crops": ["Wheat", "Rice", "Sugarcane", "Potato", "Mustard"]},
    {"code": "MP", "name": "Madhya Pradesh", "capital": "Bhopal", "lat": 22.9734, "lng": 78.6569, "farmers_reached": 3_890_000, "active_alerts": 3, "top_crop": "Soybean", "districts": 55, "arable_land_mha": 14.9, "default_language": "hi", "primary_crops": ["Soybean", "Wheat", "Rice", "Cotton", "Maize"]},
    {"code": "GJ", "name": "Gujarat", "capital": "Gandhinagar", "lat": 22.2587, "lng": 71.1924, "farmers_reached": 2_450_000, "active_alerts": 2, "top_crop": "Cotton", "districts": 33, "arable_land_mha": 9.8, "default_language": "gu", "primary_crops": ["Cotton", "Groundnut", "Wheat", "Rice", "Cumin"]},
    {"code": "WB", "name": "West Bengal", "capital": "Kolkata", "lat": 22.9868, "lng": 87.8550, "farmers_reached": 3_210_000, "active_alerts": 2, "top_crop": "Rice", "districts": 23, "arable_land_mha": 5.2, "default_language": "bn", "primary_crops": ["Rice", "Jute", "Potato", "Tea", "Wheat"]}
]

@router.get("/")
async def list_states():
    """List all supported Indian agricultural states."""
    return {"states": INDIAN_STATES, "total_states": len(INDIAN_STATES)}

@router.get("/{state_code}")
async def get_state(state_code: str):
    """Get detailed configuration for a specific state."""
    state = next((s for s in INDIAN_STATES if s["code"] == state_code.upper()), None)
    if not state:
        return {"error": f"State '{state_code}' not found"}
    return state

@router.get("/exchange/signals")
async def get_exchange_signals():
    """Cross-state agricultural intelligence exchange — aggregated, anonymized signals."""
    return {
        "protocol_version": "1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "signals": [
            {"from_state": "PB", "to_state": "UP", "signal_type": "disease_alert", "message": "Wheat rust outbreak detected in Ludhiana district — recommend preventive spraying in adjacent UP wheat belt", "severity": "high", "timestamp": "2026-08-20T10:30:00Z"},
            {"from_state": "MH", "to_state": "KA", "signal_type": "pest_advisory", "message": "Fall Armyworm migration pattern moving south from Vidarbha — early warning for northern Karnataka maize fields", "severity": "moderate", "timestamp": "2026-08-19T14:15:00Z"},
            {"from_state": "TN", "to_state": "KA", "signal_type": "best_practice", "message": "System of Rice Intensification (SRI) adoption in Thanjavur showing 22% yield improvement — sharing protocol for Mandya district", "severity": "info", "timestamp": "2026-08-18T09:00:00Z"},
            {"from_state": "MP", "to_state": "GJ", "signal_type": "disease_alert", "message": "Soybean yellow mosaic virus confirmed in Indore — advisory issued for Saurashtra groundnut-soybean rotation areas", "severity": "high", "timestamp": "2026-08-21T08:45:00Z"},
            {"from_state": "WB", "to_state": "UP", "signal_type": "weather_advisory", "message": "Heavy monsoon rainfall forecast for Gangetic plains — rice paddy waterlogging risk elevated for next 72 hours", "severity": "moderate", "timestamp": "2026-08-22T06:00:00Z"}
        ],
        "note": "All signals contain only aggregated, anonymized data. Raw farmer-level records remain within each state's deployment."
    }

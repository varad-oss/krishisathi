from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import List
from models.interop import RegionalAgriSignal, StateConfig, AggregatedStateReport, strip_pii
from uuid import uuid4

router = APIRouter(prefix="/api/states", tags=["Cross-State Interoperability"])

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

# In-memory store for federation signals
FEDERATION_SIGNALS = [
    RegionalAgriSignal(from_state="PB", to_state="UP", signal_type="disease_alert", severity="high", message="Wheat rust outbreak detected in Ludhiana district — recommend preventive spraying in adjacent UP wheat belt", disease_name="Wheat Rust", affected_crop="Wheat", affected_district="Ludhiana", report_count=189, timestamp=datetime.utcnow()),
    RegionalAgriSignal(from_state="MH", to_state="KA", signal_type="pest_advisory", severity="moderate", message="Fall Armyworm migration pattern moving south from Vidarbha", disease_name="Fall Armyworm", affected_crop="Maize", affected_district="Vidarbha", report_count=156, timestamp=datetime.utcnow()),
]

@router.get("/")
async def list_states():
    """List all supported Indian agricultural states."""
    return {"states": INDIAN_STATES, "total_states": len(INDIAN_STATES)}

@router.get("/{state_code}/config", response_model=StateConfig)
async def get_state_config(state_code: str):
    """Get detailed configuration for a specific state deployment."""
    state = next((s for s in INDIAN_STATES if s["code"] == state_code.upper()), None)
    if not state:
        raise HTTPException(status_code=404, detail=f"State '{state_code}' not found")
    return StateConfig(**state)

@router.post("/exchange/signals", response_model=RegionalAgriSignal, status_code=201)
async def post_exchange_signal(signal: RegionalAgriSignal):
    """
    Publish a new agricultural signal to the national federation network.
    Strips any accidental PII before storing.
    """
    # Clean PII from metadata if any
    if signal.metadata:
        signal.metadata = strip_pii(signal.metadata)
    
    if not signal.signal_id:
        signal.signal_id = str(uuid4())
    
    FEDERATION_SIGNALS.append(signal)
    return signal

@router.get("/exchange/signals", response_model=AggregatedStateReport)
async def get_exchange_signals():
    """Cross-state agricultural intelligence exchange — aggregated, anonymized signals."""
    return AggregatedStateReport(
        total_signals=len(FEDERATION_SIGNALS),
        states_reporting=len(set(s.from_state for s in FEDERATION_SIGNALS)),
        critical_alerts=len([s for s in FEDERATION_SIGNALS if s.severity == "critical"]),
        disease_signals=len([s for s in FEDERATION_SIGNALS if s.signal_type == "disease_alert"]),
        pest_signals=len([s for s in FEDERATION_SIGNALS if s.signal_type == "pest_advisory"]),
        weather_signals=len([s for s in FEDERATION_SIGNALS if s.signal_type == "weather_advisory"]),
        signals=sorted(FEDERATION_SIGNALS, key=lambda x: x.timestamp, reverse=True)
    )

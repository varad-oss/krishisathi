from uuid import uuid4

from fastapi import APIRouter, Depends

from core.errors import ApiError
from core.security import Principal, require_system_role
from models.interop import AggregatedStateReport, RegionalAgriSignal, StateConfig, strip_pii
from services.persistence_service import persistence_service

router = APIRouter(prefix="/api/states", tags=["Cross-State Interoperability"])

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


@router.get("")
@router.get("/", include_in_schema=False)
async def list_states():
    """States configured in this deployment."""
    return {"states": INDIAN_STATES, "total_states": len(INDIAN_STATES)}


@router.get("/{state_code}/config", response_model=StateConfig)
async def get_state_config(state_code: str):
    state = next((s for s in INDIAN_STATES if s["code"] == state_code.upper()), None)
    if not state:
        raise ApiError(404, "NOT_FOUND", f"State '{state_code[:4]}' is not configured.")
    return StateConfig(**state)


@router.post("/exchange/signals", response_model=RegionalAgriSignal, status_code=201)
async def post_exchange_signal(signal: RegionalAgriSignal, principal: Principal = Depends(require_system_role)):
    """Publish an aggregated signal to the federation. PII keys are stripped before storage."""
    if signal.metadata:
        signal.metadata = strip_pii(signal.metadata)
    signal.signal_id = str(uuid4())  # server-assigned; client ids could collide with existing records
    await persistence_service.save_federation_signal(signal)
    return signal


@router.get("/exchange/signals", response_model=AggregatedStateReport)
async def get_exchange_signals():
    """Cross-state exchange: aggregated, anonymized signals published by authenticated state systems."""
    signals = await persistence_service.get_federation_signals()
    return AggregatedStateReport(
        total_signals=len(signals),
        states_reporting=len({s.from_state for s in signals}),
        critical_alerts=len([s for s in signals if s.severity == "critical"]),
        disease_signals=len([s for s in signals if s.signal_type == "disease_alert"]),
        pest_signals=len([s for s in signals if s.signal_type == "pest_advisory"]),
        weather_signals=len([s for s in signals if s.signal_type == "weather_advisory"]),
        signals=signals,
    )

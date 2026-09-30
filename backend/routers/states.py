from uuid import uuid4

from fastapi import APIRouter, Depends

from core.errors import ApiError
from core.security import Principal, require_system_role
from models.interop import AggregatedStateReport, RegionalAgriSignal, StateConfig, strip_pii
from services.persistence_service import persistence_service
from services.regions import INDIAN_STATES

router = APIRouter(prefix="/api/states", tags=["Cross-State Interoperability"])

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

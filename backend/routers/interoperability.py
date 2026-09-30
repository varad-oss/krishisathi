"""BRICS interoperability API: versioned, country-neutral, privacy-aware agricultural signals.

Catalogues (crops, diseases, schemas, adapters, models) are public. Signals require a partner token
(role partner | system | admin). Every list is paginated with an opaque cursor, and every item carries
its provenance. No farm, farmer or exact location is ever served here.
"""
import base64
import binascii
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request

from core.errors import ApiError
from core.events import log_event
from core.rate_limit import rate_limit
from core.security import Principal, require_partner_role
from models.interop_v1 import SCHEMA_VERSION, PageV1, json_schemas
from services import federation
from services.interop import adapter as adapters
from services.interop.india import IndiaAdapter

adapters.register(IndiaAdapter())

MAX_LOOKBACK_DAYS = 90


async def interop_limit(request: Request):
    await rate_limit(request, limit=60, window_seconds=60)


router = APIRouter(prefix="/api/interoperability", tags=["BRICS interoperability"], dependencies=[Depends(interop_limit)])

Country = Query("IN", pattern=r"^[A-Za-z]{2}$", description="ISO 3166-1 alpha-2 country whose adapter answers")
Limit = Query(50, ge=1, le=200)
Cursor = Query(None, max_length=64)
Since = Query(None, description=f"Start date (default and maximum: {MAX_LOOKBACK_DAYS} days ago)")


def _adapter(country: str):
    found = adapters.get(country)
    if not found:
        raise ApiError(404, "NOT_FOUND", f"No adapter is registered for country '{country.upper()}'.")
    return found


def _offset(cursor: Optional[str]) -> int:
    if not cursor:
        return 0
    try:
        value = int(base64.urlsafe_b64decode(cursor.encode()).decode())
    except (binascii.Error, ValueError, UnicodeDecodeError):
        raise ApiError(422, "INVALID_INPUT", "Invalid cursor.")
    if value < 0:
        raise ApiError(422, "INVALID_INPUT", "Invalid cursor.")
    return value


def _page(adapter, items: list, limit: int, cursor: Optional[str], notes: Optional[str] = None, privacy: bool = True) -> PageV1:
    start = _offset(cursor)
    chunk = items[start:start + limit]
    nxt = base64.urlsafe_b64encode(str(start + limit).encode()).decode() if start + limit < len(items) else None
    return PageV1(country_code=adapter.country_code, generated_at=datetime.now(timezone.utc), count=len(chunk), next_cursor=nxt,
                  items=chunk, privacy=adapter.privacy if privacy else None, notes=notes)


def _since(value: Optional[date]) -> date:
    floor = date.today() - timedelta(days=MAX_LOOKBACK_DAYS)
    return max(value, floor) if value else floor


def _served(kind: str, adapter, page: PageV1, principal: Optional[Principal] = None):
    log_event("interoperability_signals_served", kind=kind, country=adapter.country_code, count=page.count,
              partner=principal.user_id if principal else None)
    return page


@router.get("/schemas")
async def get_schemas():
    """JSON Schema of every v1.0 shape."""
    return {"schema_version": SCHEMA_VERSION, "schemas": json_schemas()}


@router.get("/adapters")
async def get_adapters():
    """Registered country adapters: sources, coverage, privacy rules and limitations."""
    return {"schema_version": SCHEMA_VERSION, "adapters": [a.describe() for a in adapters.registered()]}


@router.get("/models")
async def get_models():
    """Model versions in use and the federation status. No federated training runs in this deployment."""
    return federation.registry()


@router.get("/crops")
async def get_crops(country: str = Country, limit: int = Limit, cursor: Optional[str] = Cursor):
    a = _adapter(country)
    return _page(a, await a.crops(), limit, cursor, privacy=False)


@router.get("/diseases")
async def get_diseases(country: str = Country, limit: int = Limit, cursor: Optional[str] = Cursor):
    a = _adapter(country)
    return _page(a, await a.diseases(), limit, cursor, privacy=False)


@router.get("/weather-signals")
async def get_weather_signals(country: str = Country, limit: int = Limit, cursor: Optional[str] = Cursor,
                              principal: Principal = Depends(require_partner_role)):
    a = _adapter(country)
    page = _page(a, await a.weather_signals(), limit, cursor, notes="Forecast rule evaluations at one reference point per region.")
    return _served("weather_signals", a, page, principal)


@router.get("/agricultural-observations")
async def get_observations(country: str = Country, since: Optional[date] = Since, limit: int = Limit, cursor: Optional[str] = Cursor,
                           principal: Principal = Depends(require_partner_role)):
    a = _adapter(country)
    page = _page(a, await a.observations(_since(since)), limit, cursor)
    return _served("observations", a, page, principal)


@router.get("/risk-signals")
async def get_risk_signals(country: str = Country, since: Optional[date] = Since, limit: int = Limit, cursor: Optional[str] = Cursor,
                           principal: Principal = Depends(require_partner_role)):
    a = _adapter(country)
    page = _page(a, await a.risk_signals(_since(since)), limit, cursor,
                 notes="Signals describe evidence in a region; they never assert that a pest or pathogen moved between regions.")
    return _served("risk_signals", a, page, principal)

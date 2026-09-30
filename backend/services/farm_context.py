"""Builds the normalized FarmContext: every signal the intelligence engine reasons over, fetched
concurrently, each with an explicit status. A slow source is given a time budget; when it runs out the
signal is "pending" (the upstream query keeps running and fills its cache for the next request) instead
of blocking the whole farm view or being replaced by an estimate.
"""
import asyncio
import time
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Optional

from models.exceptions import ServiceUnavailableException
from services import agro_rules
from services.crop_stage import estimate_stage
from services.crops import normalize_crop
from services.earth_engine_service import earth_engine_service
from services.persistence_service import nearby_outbreaks, persistence_service
from services.soil_service import soil_service
from services.soil_water import topsoil_water
from services.weather_service import weather_service

SOIL_BUDGET_S = 12.0
SATELLITE_BUDGET_S = 8.0


@dataclass
class Signal:
    """One input to the engine. status: available | unavailable | not_configured | no_data | not_provided | pending."""
    status: str
    data: Any = None
    reason: Optional[str] = None
    latency_ms: Optional[float] = None

    @property
    def ok(self) -> bool:
        return self.status == "available"


@dataclass
class FarmContext:
    lat: float
    lng: float
    crop: Optional[str]
    sowing_date: Optional[date]
    today: date
    weather: Signal
    soil: Signal
    crop_health: Signal
    outbreaks: Signal
    crop_stage: dict
    soil_water: dict
    insights: list[dict] = field(default_factory=list)
    history: dict = field(default_factory=dict)  # recent farm diagnoses / actions from the digital twin
    # What the satellite numbers describe: {"mode": "polygon", "area_ha": ...} for a drawn field, else the point circle.
    field_geometry: dict = field(default_factory=lambda: {"mode": "point"})

    def insight(self, insight_id: str) -> Optional[dict]:
        return next((i for i in self.insights if i["id"] == insight_id), None)

    def timings(self) -> dict:
        return {name: getattr(self, name).latency_ms for name in ("weather", "soil", "crop_health", "outbreaks")}


async def _timed(make, budget: float | None = None) -> tuple[Any, Optional[float], bool]:
    """(result, latency_ms, timed_out). The underlying task is shielded so a timeout never cancels it."""
    start = time.perf_counter()
    task = asyncio.ensure_future(make())
    if budget is None:
        result = await task
        return result, round((time.perf_counter() - start) * 1000, 1), False
    try:
        result = await asyncio.wait_for(asyncio.shield(task), budget)
    except asyncio.TimeoutError:
        return None, round(budget * 1000, 1), True
    return result, round((time.perf_counter() - start) * 1000, 1), False


async def _weather(lat, lng) -> Signal:
    try:
        data, ms, _ = await _timed(lambda: weather_service.get_conditions(lat, lng))
    except ServiceUnavailableException as e:
        return Signal("unavailable", reason="weather_unavailable", data={"message": e.message})
    return Signal("available", data, latency_ms=ms)


async def _soil(lat, lng) -> Signal:
    data, ms, timed_out = await _timed(lambda: soil_service.get_soil(lat, lng), SOIL_BUDGET_S)
    if timed_out:
        return Signal("pending", reason="still_loading", latency_ms=ms)
    return Signal(data["status"], data, reason=data.get("reason"), latency_ms=ms)


async def _satellite(lat, lng, plot=None) -> Signal:
    try:
        data, ms, timed_out = await _timed(lambda: earth_engine_service.get_crop_health(lat, lng, plot), SATELLITE_BUDGET_S)
    except Exception:  # the service reports its own failures; anything else must not break the farm view
        return Signal("unavailable", reason="dataset_query_failed")
    if timed_out:
        return Signal("pending", reason="still_loading", latency_ms=ms)
    status = "not_configured" if data.get("reason") == "not_configured" else data["status"]
    return Signal(status, data, reason=data.get("reason"), latency_ms=ms)


async def _outbreaks(lat, lng, crop) -> Signal:
    try:
        found, ms, _ = await _timed(persistence_service.get_outbreaks)
    except Exception:
        return Signal("unavailable", reason="database_unavailable")
    return Signal("available", nearby_outbreaks(found, lat, lng, crop), latency_ms=ms)


async def build_farm_context(lat: float, lng: float, crop: str | None = None, sowing_date: date | None = None,
                             history: dict | None = None, today: date | None = None, plot: dict | None = None) -> FarmContext:
    """`plot` ({"geometry", "area_ha"}) makes satellite statistics field-specific; without it the point circle is used."""
    canonical = normalize_crop(crop)
    weather, soil, crop_health, outbreaks = await asyncio.gather(
        _weather(lat, lng), _soil(lat, lng), _satellite(lat, lng, plot), _outbreaks(lat, lng, canonical),
    )
    insights = agro_rules.evaluate(weather.data) if weather.ok else []
    moisture = weather.data["current"].get("soil_moisture_3_9cm") if weather.ok else None
    return FarmContext(
        lat=lat, lng=lng, crop=canonical, sowing_date=sowing_date, today=today or date.today(),
        weather=weather, soil=soil, crop_health=crop_health, outbreaks=outbreaks,
        crop_stage=estimate_stage(canonical, sowing_date, today or date.today()),
        soil_water=topsoil_water(moisture, soil.data or {}),
        insights=insights, history=history or {},
        field_geometry={"mode": "polygon", "area_ha": plot["area_ha"]} if plot else {"mode": "point"},
    )

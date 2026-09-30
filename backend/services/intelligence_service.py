"""Farm Intelligence: context -> risks -> top action, with data quality and provenance for every input."""
import time
from datetime import date, datetime, timezone

from core.events import log_event
from models.intelligence import DataQuality, FarmIntelligence
from services import risk_engine
from services.earth_engine_service import PROVENANCE as SATELLITE_PROVENANCE
from services.farm_context import FarmContext, build_farm_context
from services.soil_water import REFERENCES as SOIL_WATER_REFERENCES
from services.weather_service import PROVENANCE_BASE as WEATHER_PROVENANCE

LOCATION_DECIMALS = 3  # ~110 m: enough to identify the field for the farmer, returned only to them


def data_quality(ctx: FarmContext) -> list[DataQuality]:
    w, s, c, o = ctx.weather, ctx.soil, ctx.crop_health, ctx.outbreaks
    stage = ctx.crop_stage
    stage_status = {"estimated": "available", "beyond_season": "available", "no_calendar": "no_data"}.get(stage["status"], "not_provided")
    return [
        DataQuality(source="weather", status=w.status, kind="model", provider=WEATHER_PROVENANCE["source"], reason=w.reason,
                    as_of=w.data["current"]["valid_at"] if w.ok else None),
        DataQuality(source="soil", status=s.status, kind="model", provider="ISRIC SoilGrids 2.0", reason=s.reason,
                    as_of=(s.data.get("provenance") or {}).get("retrieved_at") if s.ok else None),
        DataQuality(source="satellite", status=c.status, kind="satellite_observation", provider="Sentinel-2 (Copernicus)", reason=c.reason,
                    as_of=c.data.get("latest_image_date") if c.ok else None),
        DataQuality(source="crop_stage", status=stage_status, kind="rule", provider="FAO-56 Table 11",
                    reason=None if stage_status == "available" else stage["status"]),
        DataQuality(source="outbreaks", status=o.status, kind="ai_classified_user_reports", provider="KrishiSathi community reports", reason=o.reason),
    ]


def _weather_summary(ctx: FarmContext) -> dict | None:
    if not ctx.weather.ok:
        return None
    w = ctx.weather.data
    return {
        "current": {k: w["current"].get(k) for k in ("valid_at", "temperature_c", "humidity_pct", "wind_kmh", "condition", "soil_moisture_3_9cm")},
        "next_days": [{k: d.get(k) for k in ("date", "condition", "temp_max_c", "temp_min_c", "precipitation_mm", "precipitation_probability_pct")}
                      for d in w["daily"][:3]],
        "provenance": w["provenance"],
    }


def _soil_summary(ctx: FarmContext) -> dict | None:
    if not ctx.soil.ok:
        return None
    return {k: ctx.soil.data.get(k) for k in ("properties", "ratings", "provenance")}


def _crop_health_summary(ctx: FarmContext) -> dict | None:
    if not ctx.crop_health.data:
        return None
    return {**ctx.crop_health.data, "provenance": SATELLITE_PROVENANCE}


def assemble(ctx: FarmContext) -> FarmIntelligence:
    risks = risk_engine.assess(ctx)
    top = risk_engine.top_action(risks, ctx)
    soil_water = {**ctx.soil_water, "references": SOIL_WATER_REFERENCES} if ctx.soil_water["status"] != "unavailable" else ctx.soil_water
    return FarmIntelligence(
        generated_at=datetime.now(timezone.utc).isoformat(),
        farm={
            "crop": ctx.crop,
            "sowing_date": ctx.sowing_date.isoformat() if ctx.sowing_date else None,
            "location": {"lat": round(ctx.lat, LOCATION_DECIMALS), "lng": round(ctx.lng, LOCATION_DECIMALS)},
            "crop_stage": ctx.crop_stage,
        },
        top_action=top,
        risks=risks,
        weather=_weather_summary(ctx),
        soil=_soil_summary(ctx),
        soil_water=soil_water,
        crop_health=_crop_health_summary(ctx),
        nearby_outbreaks=ctx.outbreaks.data if ctx.outbreaks.ok else None,
        data_quality=data_quality(ctx),
        engine=risk_engine.ENGINE,
    )


async def farm_intelligence(lat: float, lng: float, crop: str | None, sowing_date: date | None, history: dict | None = None,
                            farm_id: str | None = None) -> FarmIntelligence:
    start = time.perf_counter()
    ctx = await build_farm_context(lat, lng, crop, sowing_date, history)
    result = assemble(ctx)
    log_event(
        "farm_intelligence_generated",
        farm_id=farm_id,
        crop=ctx.crop,
        crop_stage=ctx.crop_stage.get("stage"),
        top_action=result.top_action.action,
        top_severity=result.top_action.severity,
        risks={r.category: r.severity for r in result.risks},
        sources={q.source: q.status for q in result.data_quality},
        source_ms=ctx.timings(),
        latency_ms=round((time.perf_counter() - start) * 1000, 1),
        engine=risk_engine.ENGINE["version"],
    )
    return result

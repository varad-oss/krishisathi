"""Farm digital twin: persistent farm record, intelligence snapshots, recommendations and self-reported outcomes.

A farm is identified by an id plus a random bearer token given once at creation; only its SHA-256 is stored.
Nothing here identifies a person. Follow-through and outcomes are what the farmer says happened: they are
recorded as feedback signals and never presented as proof that a recommendation worked.
"""
import hashlib
import hmac
import secrets
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select

from core.database import AsyncSessionLocal
from core.errors import ApiError
from models.intelligence import FarmIntelligence
from models.schema import AdvisoryActionRecord, DiagnosisRecord, FarmRecord, FarmSnapshotRecord
from services.crops import normalize_crop

LOCATION_DECIMALS = 3          # ~110 m
SNAPSHOT_MIN_INTERVAL = timedelta(hours=1)
HISTORY_LIMIT = 30
FOLLOWED = ("yes", "partial", "no", "not_applicable")
OUTCOMES = ("improved", "same", "worse", "diagnosis_wrong", "not_sure")


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _iso(dt: Optional[datetime]) -> Optional[str]:
    return dt.replace(tzinfo=timezone.utc).isoformat() if dt else None


def farm_view(f: FarmRecord) -> dict:
    return {
        "farm_id": f.id, "crop": f.crop, "sowing_date": f.sowing_date.isoformat() if f.sowing_date else None,
        "area_ha": f.area_ha, "country_code": f.country_code,
        "location": {"lat": f.lat, "lng": f.lng}, "created_at": _iso(f.created_at), "updated_at": _iso(f.updated_at),
    }


def action_view(a: AdvisoryActionRecord) -> dict:
    return {
        "action_id": a.id, "created_at": _iso(a.created_at), "source_type": a.source_type, "source_ref": a.source_ref,
        "action": a.action, "category": a.category, "severity": a.severity, "confidence": a.confidence, "crop": a.crop,
        "followed": a.followed, "followed_at": _iso(a.followed_at), "outcome": a.outcome, "outcome_at": _iso(a.outcome_at),
    }


async def create_farm(lat: float, lng: float, crop: Optional[str], sowing_date: Optional[date], area_ha: Optional[float]) -> tuple[dict, str]:
    token = secrets.token_urlsafe(32)
    now = datetime.utcnow()
    async with AsyncSessionLocal() as session:
        farm = FarmRecord(token_hash=_hash(token), lat=round(lat, LOCATION_DECIMALS), lng=round(lng, LOCATION_DECIMALS),
                          crop=normalize_crop(crop), sowing_date=sowing_date, area_ha=area_ha, created_at=now, updated_at=now)
        session.add(farm)
        await session.commit()
        return farm_view(farm), token


async def authorize(farm_id: str, token: Optional[str]) -> FarmRecord:
    """The farm, if the token matches. Unknown farm and wrong token give the same answer."""
    async with AsyncSessionLocal() as session:
        farm = await session.get(FarmRecord, farm_id)
    if not token or not farm or not hmac.compare_digest(farm.token_hash, _hash(token)):
        raise ApiError(404, "NOT_FOUND", "Farm not found.")
    return farm


async def update_farm(farm_id: str, lat: float, lng: float, crop: Optional[str], sowing_date: Optional[date], area_ha: Optional[float]) -> dict:
    async with AsyncSessionLocal() as session:
        farm = await session.get(FarmRecord, farm_id)
        farm.lat, farm.lng = round(lat, LOCATION_DECIMALS), round(lng, LOCATION_DECIMALS)
        farm.crop, farm.sowing_date, farm.area_ha = normalize_crop(crop), sowing_date, area_ha
        farm.updated_at = datetime.utcnow()
        await session.commit()
        return farm_view(farm)


async def recent_diagnoses(farm_id: str, days: int = 30) -> list[dict]:
    since = datetime.utcnow() - timedelta(days=days)
    async with AsyncSessionLocal() as session:
        rows = (await session.execute(
            select(DiagnosisRecord).where(DiagnosisRecord.farm_id == farm_id, DiagnosisRecord.timestamp >= since)
            .order_by(DiagnosisRecord.timestamp.desc()).limit(10)
        )).scalars().all()
    now = datetime.utcnow()
    return [{"diagnosis_id": d.id, "status": d.diagnosis_status, "disease": d.disease if d.diagnosis_status == "disease_detected" else None,
             "certainty": d.certainty, "crop": d.crop, "date": d.timestamp.date().isoformat(), "age_days": (now - d.timestamp).days}
            for d in rows]


def _observations(intel: FarmIntelligence) -> dict:
    w, h, sw = intel.weather or {}, intel.crop_health or {}, intel.soil_water or {}
    return {
        "temperature_c": (w.get("current") or {}).get("temperature_c"),
        "rain_next_3_days_mm": [d.get("precipitation_mm") for d in w.get("next_days", [])],
        "soil_water_status": sw.get("status"),
        "ndvi": h.get("ndvi") if h.get("status") == "available" else None,
        "ndvi_image_date": h.get("latest_image_date"),
    }


async def record_intelligence(farm: FarmRecord, intel: FarmIntelligence) -> dict:
    """Stores a snapshot (at most one per SNAPSHOT_MIN_INTERVAL unless the top action changed) and one
    recommendation record per farm, action and day, so feedback always refers to what was shown."""
    now = datetime.utcnow()
    top = intel.top_action
    async with AsyncSessionLocal() as session:
        last = (await session.execute(
            select(FarmSnapshotRecord).where(FarmSnapshotRecord.farm_id == farm.id).order_by(FarmSnapshotRecord.created_at.desc()).limit(1)
        )).scalar_one_or_none()
        snapshot_id = last.id if last else None
        if not last or now - last.created_at >= SNAPSHOT_MIN_INTERVAL or last.top_action != top.action:
            snap = FarmSnapshotRecord(
                farm_id=farm.id, created_at=now, crop=intel.farm.get("crop"), crop_stage=intel.farm["crop_stage"].get("stage"),
                top_action=top.action, top_severity=top.severity,
                risks={r.category: r.severity for r in intel.risks}, data_quality={q.source: q.status for q in intel.data_quality},
                observations=_observations(intel),
            )
            session.add(snap)
            await session.flush()  # assigns the id
            snapshot_id = snap.id

        action = None
        if top.status == "action" and top.action:
            day_start = datetime(now.year, now.month, now.day)
            action = (await session.execute(
                select(AdvisoryActionRecord).where(
                    AdvisoryActionRecord.farm_id == farm.id, AdvisoryActionRecord.source_type == "intelligence",
                    AdvisoryActionRecord.action == top.action, AdvisoryActionRecord.created_at >= day_start)
            )).scalar_one_or_none()
            if not action:
                action = AdvisoryActionRecord(farm_id=farm.id, created_at=now, source_type="intelligence", source_ref=snapshot_id,
                                              action=top.action, category=top.category, severity=top.severity,
                                              confidence=top.confidence, crop=intel.farm.get("crop"))
                session.add(action)
        await session.commit()
        return {"snapshot_id": snapshot_id, "action": action_view(action) if action else None}


async def record_action(farm: FarmRecord, source_type: str, source_ref: Optional[str], action: str, category: Optional[str] = None,
                        severity: Optional[str] = None, confidence: Optional[str] = None) -> dict:
    async with AsyncSessionLocal() as session:
        rec = AdvisoryActionRecord(farm_id=farm.id, created_at=datetime.utcnow(), source_type=source_type, source_ref=source_ref,
                                   action=action, category=category, severity=severity, confidence=confidence, crop=farm.crop)
        session.add(rec)
        await session.commit()
        return action_view(rec)


async def submit_feedback(farm_id: str, action_id: str, followed: Optional[str], outcome: Optional[str]) -> dict:
    async with AsyncSessionLocal() as session:
        rec = await session.get(AdvisoryActionRecord, action_id)
        if not rec or rec.farm_id != farm_id:
            raise ApiError(404, "NOT_FOUND", "Recommendation not found.")
        if outcome == "diagnosis_wrong" and rec.source_type != "diagnosis":
            raise ApiError(422, "INVALID_INPUT", "'diagnosis_wrong' only applies to a photo diagnosis.")
        now = datetime.utcnow()
        if followed:
            rec.followed, rec.followed_at = followed, now
        if outcome:
            rec.outcome, rec.outcome_at = outcome, now
        await session.commit()
        return action_view(rec)


async def history(farm: FarmRecord) -> dict:
    async with AsyncSessionLocal() as session:
        snaps = (await session.execute(
            select(FarmSnapshotRecord).where(FarmSnapshotRecord.farm_id == farm.id)
            .order_by(FarmSnapshotRecord.created_at.desc()).limit(HISTORY_LIMIT)
        )).scalars().all()
        actions = (await session.execute(
            select(AdvisoryActionRecord).where(AdvisoryActionRecord.farm_id == farm.id)
            .order_by(AdvisoryActionRecord.created_at.desc()).limit(HISTORY_LIMIT)
        )).scalars().all()
    return {
        "farm": farm_view(farm),
        "snapshots": [{"snapshot_id": s.id, "created_at": _iso(s.created_at), "crop": s.crop, "crop_stage": s.crop_stage,
                       "top_action": s.top_action, "top_severity": s.top_severity, "risks": s.risks,
                       "data_quality": s.data_quality, "observations": s.observations} for s in snaps],
        "actions": [action_view(a) for a in actions],
        "diagnoses": await recent_diagnoses(farm.id, days=365),
        "provenance": {"kind": "farm_record", "notes": "Snapshots are what KrishiSathi concluded at the time. Follow-through and "
                       "outcomes are reported by the farmer and are not evidence that a recommendation caused the result."},
    }

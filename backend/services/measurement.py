"""App-derived feedback signals: how often recommendations are followed and what farmers report afterwards.

These describe KrishiSathi users only. They are not official agricultural statistics, and an "improved"
report after a recommendation does not show that the recommendation caused the improvement. Groups with
fewer than MIN_GROUP records are suppressed so small groups cannot identify a farm.
"""
import math
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from sqlalchemy import func, select

from core.database import AsyncSessionLocal
from models.schema import AdvisoryActionRecord, DiagnosisRecord, FarmRecord

WINDOW_DAYS = 90
MIN_GROUP = 5
REGION_GRID_DEG = 1.0  # region = 1° grid cell of the farm (~110 km)

PROVENANCE = {
    "source": "KrishiSathi farm records",
    "kind": "app_derived_feedback",
    "notes": "Self-reported by farmers who use KrishiSathi. Not official statistics and not evidence that a "
             "recommendation caused an outcome. Groups smaller than the minimum size are suppressed.",
}


def _summary(rows: list) -> dict:
    """rows: (followed, outcome). Rates are over answered questions only."""
    followed = Counter(r[0] for r in rows if r[0])
    outcomes = Counter(r[1] for r in rows if r[1])
    answered = sum(followed.values())
    applicable = answered - followed.get("not_applicable", 0)
    return {
        "recommendations": len(rows),
        "follow_through_answers": answered,
        "followed_rate": round((followed.get("yes", 0) + followed.get("partial", 0)) / applicable, 2) if applicable else None,
        "followed": dict(followed),
        "outcome_answers": sum(outcomes.values()),
        "outcomes": dict(outcomes),
    }


def _grouped(rows: list, key_index: int) -> dict:
    groups = defaultdict(list)
    for r in rows:
        groups[r[key_index] or "unknown"].append(r[:2])
    out, suppressed = {}, 0
    for key, items in groups.items():
        if len(items) < MIN_GROUP:
            suppressed += 1
            continue
        out[key] = _summary(items)
    return {"groups": out, "suppressed_groups": suppressed}


def _cell(lat: float, lng: float) -> str:
    return f"{math.floor(lat / REGION_GRID_DEG) * REGION_GRID_DEG:g},{math.floor(lng / REGION_GRID_DEG) * REGION_GRID_DEG:g}"


async def feedback_metrics() -> dict:
    since = datetime.utcnow() - timedelta(days=WINDOW_DAYS)
    async with AsyncSessionLocal() as session:
        rows = (await session.execute(
            select(AdvisoryActionRecord.followed, AdvisoryActionRecord.outcome, AdvisoryActionRecord.source_type,
                   AdvisoryActionRecord.crop, AdvisoryActionRecord.confidence, FarmRecord.lat, FarmRecord.lng)
            .join(FarmRecord, FarmRecord.id == AdvisoryActionRecord.farm_id)
            .where(AdvisoryActionRecord.created_at >= since)
        )).all()
        repeat = (await session.execute(
            select(DiagnosisRecord.farm_id).where(DiagnosisRecord.farm_id.is_not(None), DiagnosisRecord.timestamp >= since,
                                                  DiagnosisRecord.diagnosis_status == "disease_detected")
            .group_by(DiagnosisRecord.farm_id).having(func.count(DiagnosisRecord.id) >= 2)
        )).all()
        farms_with_diagnoses = await session.scalar(
            select(func.count(func.distinct(DiagnosisRecord.farm_id))).where(DiagnosisRecord.farm_id.is_not(None), DiagnosisRecord.timestamp >= since)
        ) or 0

    rows = [(r[0], r[1], r[2], r[3], r[4], _cell(r[5], r[6])) for r in rows]
    diagnosis_rows = [r for r in rows if r[2] == "diagnosis"]
    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "window_days": WINDOW_DAYS,
        "minimum_group_size": MIN_GROUP,
        "overall": _summary(rows),
        "by_source": _grouped([(r[0], r[1], r[2]) for r in rows], 2),
        "by_crop": _grouped([(r[0], r[1], r[3]) for r in rows], 2),
        "by_region": {**_grouped([(r[0], r[1], r[5]) for r in rows], 2), "region": f"{REGION_GRID_DEG:g}° grid cell (south-west corner lat,lng)"},
        # Does the model's stated certainty match what farmers later report? ("diagnosis_wrong" per certainty level)
        "diagnosis_certainty_vs_feedback": _grouped([(r[0], r[1], r[4]) for r in diagnosis_rows], 2),
        "repeat_diagnosis": {"farms_with_diagnoses": farms_with_diagnoses, "farms_with_repeat_disease_detections": len(repeat)}
        if farms_with_diagnoses >= MIN_GROUP else {"status": "insufficient_data", "minimum": MIN_GROUP},
        "provenance": PROVENANCE,
    }

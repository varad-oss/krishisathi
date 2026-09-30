"""App-derived feedback signals: how often recommendations are followed and what farmers report afterwards.

These describe KrishiSathi users only. They are not official agricultural statistics, and an "improved"
report after a recommendation does not show that the recommendation caused the improvement. Groups with
fewer than MIN_GROUP records are suppressed so small groups cannot identify a farm.
"""
import hashlib
import math
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from sqlalchemy import func, select

from core.database import AsyncSessionLocal
from models.schema import AdvisoryActionRecord, DiagnosisRecord, FarmRecord, FarmSnapshotRecord

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


# --- Evaluation (M11.5): prediction vs farmer feedback vs later app observation ---------------------------------
#
# Everything here is "KrishiSathi self-reported feedback": what farmers told the app after a recommendation or a
# photo diagnosis. It is a candidate evaluation signal. It is not a success rate, not a yield effect and not a
# calibration curve, and nothing here trains or adjusts a production model.

EVALUATION_LABEL = "KrishiSathi self-reported feedback"
EVALUATION_PROVENANCE = {
    "source": "KrishiSathi farm records",
    "kind": "farmer_reported",
    "label": EVALUATION_LABEL,
    "does_not_show": ["causal effect of a recommendation", "yield change", "farm success", "laboratory-confirmed accuracy"],
    "notes": "Farmers who answer are not a random sample; a 'diagnosis_wrong' report is the farmer's judgement, not a "
             "confirmed error. Groups smaller than the minimum size are suppressed.",
}
CERTAINTY_TIERS = ("low", "moderate", "high")
FOLLOW_KEYS = ("yes", "partial", "no")


def _suppress(groups: dict[str, list], summarize) -> dict:
    out, suppressed = {}, 0
    for key, items in groups.items():
        if len(items) < MIN_GROUP:
            suppressed += 1
        else:
            out[key] = summarize(items)
    return {"groups": out, "suppressed_groups": suppressed}


def _group(rows: list, key) -> dict[str, list]:
    groups = defaultdict(list)
    for r in rows:
        groups[str(key(r) or "unknown")].append(r)
    return groups


def _diagnosis_feedback(rows: list) -> dict:
    """rows: dicts with 'outcome'. Counts only answered outcomes; the rate is wrong / answered."""
    answered = [r for r in rows if r["outcome"]]
    wrong = sum(r["outcome"] == "diagnosis_wrong" for r in answered)
    return {"feedback_count": len(answered), "diagnosis_wrong": wrong,
            "diagnosis_wrong_rate": round(wrong / len(answered), 2) if answered else None,
            "outcomes": dict(Counter(r["outcome"] for r in answered))}


def _advisory_feedback(rows: list) -> dict:
    followed = Counter(r["followed"] for r in rows if r["followed"])
    applicable = sum(followed[k] for k in FOLLOW_KEYS)
    outcomes = Counter(r["outcome"] for r in rows if r["outcome"])
    rate = lambda k: round(followed[k] / applicable, 2) if applicable else None
    return {"recommendations": len(rows), "follow_through_answers": applicable,
            "followed_rate": rate("yes"), "partial_rate": rate("partial"), "not_followed_rate": rate("no"),
            "not_applicable": followed.get("not_applicable", 0),
            "outcome_answers": sum(outcomes.values()), "outcome_distribution": dict(outcomes)}


async def _diagnosis_rows(since: datetime) -> tuple[list[dict], list[dict]]:
    """(diagnoses in the window, diagnosis recommendations with their feedback and the diagnosis they refer to)."""
    async with AsyncSessionLocal() as session:
        diagnoses = (await session.execute(
            select(DiagnosisRecord.id, DiagnosisRecord.crop, DiagnosisRecord.diagnosis_status, DiagnosisRecord.certainty,
                   DiagnosisRecord.image_quality, DiagnosisRecord.guidance_level)
            .where(DiagnosisRecord.timestamp >= since)
        )).all()
        feedback = (await session.execute(
            select(AdvisoryActionRecord.id, AdvisoryActionRecord.followed, AdvisoryActionRecord.outcome, AdvisoryActionRecord.created_at,
                   AdvisoryActionRecord.outcome_at, AdvisoryActionRecord.farm_id,
                   DiagnosisRecord.crop, DiagnosisRecord.diagnosis_status, DiagnosisRecord.certainty, DiagnosisRecord.image_quality,
                   DiagnosisRecord.guidance_level, DiagnosisRecord.disease, DiagnosisRecord.differential, DiagnosisRecord.model_version,
                   FarmRecord.lat, FarmRecord.lng)
            .join(DiagnosisRecord, DiagnosisRecord.id == AdvisoryActionRecord.source_ref)
            .join(FarmRecord, FarmRecord.id == AdvisoryActionRecord.farm_id)
            .where(AdvisoryActionRecord.source_type == "diagnosis", AdvisoryActionRecord.created_at >= since)
        )).all()
    keys = ("id", "crop", "status", "certainty", "image_quality", "guidance_level")
    fkeys = ("action_id", "followed", "outcome", "created_at", "outcome_at", "farm_id", "crop", "status", "certainty", "image_quality",
             "guidance_level", "disease", "differential", "model_version", "lat", "lng")
    return [dict(zip(keys, r)) for r in diagnoses], [dict(zip(fkeys, r)) for r in feedback]


async def evaluation_metrics() -> dict:
    """Aggregate, privacy-safe evaluation of photo diagnoses and advisories from self-reported feedback."""
    since = datetime.utcnow() - timedelta(days=WINDOW_DAYS)
    diagnoses, feedback = await _diagnosis_rows(since)
    async with AsyncSessionLocal() as session:
        advisory = (await session.execute(
            select(AdvisoryActionRecord.followed, AdvisoryActionRecord.outcome, AdvisoryActionRecord.source_type, AdvisoryActionRecord.category,
                   AdvisoryActionRecord.crop, FarmRecord.lat, FarmRecord.lng)
            .join(FarmRecord, FarmRecord.id == AdvisoryActionRecord.farm_id)
            .where(AdvisoryActionRecord.created_at >= since, AdvisoryActionRecord.source_type != "diagnosis")
        )).all()
    advisory = [dict(zip(("followed", "outcome", "source_type", "category", "crop", "lat", "lng"), r)) for r in advisory]

    def by_tier(rows):
        # "Observed app feedback by model confidence": every tier is always listed, suppressed or not.
        groups = _group(rows, lambda r: r["certainty"])
        return {tier: (_diagnosis_feedback(groups[tier]) if len(groups.get(tier, [])) >= MIN_GROUP
                       else {"status": "suppressed" if groups.get(tier) else "no_data", "minimum": MIN_GROUP})
                for tier in CERTAINTY_TIERS}

    answered = [r for r in feedback if r["outcome"]]
    uncertainty = Counter((d["status"] or "unknown", d["certainty"] or "unknown") for d in diagnoses)
    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "label": EVALUATION_LABEL,
        "window_days": WINDOW_DAYS,
        "minimum_group_size": MIN_GROUP,
        "diagnosis": {
            "diagnoses": len(diagnoses),
            "diagnosis_feedback_count": len(answered),
            **({k: v for k, v in _diagnosis_feedback(feedback).items() if k != "feedback_count"}
               if len(answered) >= MIN_GROUP else {"status": "insufficient_data"}),
            # Share of diagnoses by status and certainty, independent of feedback.
            "uncertainty_distribution": [{"status": s, "certainty": c, "count": n} for (s, c), n in sorted(uncertainty.items()) if n >= MIN_GROUP],
            "uncertainty_cells_suppressed": sum(1 for n in uncertainty.values() if n < MIN_GROUP),
            "observed_feedback_by_model_confidence": {
                "label": "Observed app feedback by model confidence (not a calibration curve)",
                "tiers": by_tier(answered),
            },
            "by_crop": _suppress(_group(answered, lambda r: r["crop"]), _diagnosis_feedback),
            "by_image_quality": _suppress(_group(answered, lambda r: r["image_quality"]), _diagnosis_feedback),
            "by_guidance_level": _suppress(_group(answered, lambda r: r["guidance_level"]), _diagnosis_feedback),
        },
        "advisory": {
            "overall": _advisory_feedback(advisory) if len(advisory) >= MIN_GROUP else {"status": "insufficient_data", "recommendations": len(advisory)},
            "by_category": _suppress(_group(advisory, lambda r: r["category"] or r["source_type"]), _advisory_feedback),
            "by_crop": _suppress(_group(advisory, lambda r: r["crop"]), _advisory_feedback),
            "by_region": {**_suppress(_group(advisory, lambda r: _cell(r["lat"], r["lng"])), _advisory_feedback),
                          "region": f"{REGION_GRID_DEG:g}° grid cell (south-west corner lat,lng)"},
        },
        "provenance": EVALUATION_PROVENANCE,
    }


# Evaluation data contract. One record per recommendation or diagnosis the farmer answered: the prediction, the
# farmer's feedback and, where one exists, a later app observation of the same farm. For offline analysis only.
EVALUATION_CONTRACT_VERSION = "1.0"
EVALUATION_USE_POLICY = ("evaluation_only: candidate signal for offline analysis. Never used to retrain or tune production models "
                         "automatically; farmer feedback is unverified.")
LATER_OBSERVATION_MIN_DAYS = 3


def _record_ref(action_id: str) -> str:
    """Pseudonymous, per-record reference; the farm id and action id are not exported."""
    return hashlib.sha256(f"evaluation:{action_id}".encode()).hexdigest()[:16]


async def evaluation_records(limit: int = 500) -> dict:
    """Records under the evaluation contract (admin only). Location is a 1° cell; no farm id, token or free text."""
    since = datetime.utcnow() - timedelta(days=WINDOW_DAYS)
    _, feedback = await _diagnosis_rows(since)
    async with AsyncSessionLocal() as session:
        advisory = (await session.execute(
            select(AdvisoryActionRecord, FarmRecord.lat, FarmRecord.lng)
            .join(FarmRecord, FarmRecord.id == AdvisoryActionRecord.farm_id)
            .where(AdvisoryActionRecord.created_at >= since, AdvisoryActionRecord.source_type != "diagnosis",
                   (AdvisoryActionRecord.followed.is_not(None)) | (AdvisoryActionRecord.outcome.is_not(None)))
            .order_by(AdvisoryActionRecord.created_at.desc()).limit(limit)
        )).all()
        farm_ids = {a.farm_id for a, _, _ in advisory} | {f["farm_id"] for f in feedback}
        snaps = (await session.execute(
            select(FarmSnapshotRecord.farm_id, FarmSnapshotRecord.created_at, FarmSnapshotRecord.risks, FarmSnapshotRecord.observations)
            .where(FarmSnapshotRecord.farm_id.in_(farm_ids), FarmSnapshotRecord.created_at >= since)
            .order_by(FarmSnapshotRecord.created_at)
        )).all() if farm_ids else []
    by_farm = defaultdict(list)
    for s in snaps:
        by_farm[s.farm_id].append(s)

    def later(farm_id: str, after: datetime, category: str | None) -> dict | None:
        """First app assessment of the same farm at least LATER_OBSERVATION_MIN_DAYS after the recommendation."""
        s = next((s for s in by_farm.get(farm_id, []) if s.created_at >= after + timedelta(days=LATER_OBSERVATION_MIN_DAYS)), None)
        if not s:
            return None
        return {"observed_at": s.created_at.date().isoformat(), "kind": "later_app_assessment",
                "risk_level": (s.risks or {}).get(category) if category else None,
                "ndvi": (s.observations or {}).get("ndvi"), "satellite_quality": (s.observations or {}).get("satellite_quality"),
                "notes": "What KrishiSathi concluded later from its own inputs; not a field measurement."}

    records = []
    for a, lat, lng in advisory:
        records.append({
            "record_ref": _record_ref(a.id), "record_type": "advisory", "created_on": a.created_at.date().isoformat(),
            "crop": a.crop, "region": _cell(lat, lng),
            "prediction": {"kind": a.source_type, "action": a.action, "category": a.category, "risk_level": a.severity,
                           "evidence_confidence": a.confidence, "model": "krishisathi-farm-risk-engine" if a.source_type == "intelligence" else None},
            "farmer_feedback": {"followed": a.followed, "outcome": a.outcome, "kind": "farmer_reported"},
            "later_observation": later(a.farm_id, a.created_at, a.category),
        })
    for f in feedback:
        if not (f["followed"] or f["outcome"]):
            continue
        records.append({
            "record_ref": _record_ref(f["action_id"]), "record_type": "diagnosis", "created_on": f["created_at"].date().isoformat(),
            "crop": f["crop"], "region": _cell(f["lat"], f["lng"]),
            "prediction": {"kind": "photo_diagnosis", "status": f["status"], "disease": f["disease"] if f["status"] == "disease_detected" else None,
                           "certainty": f["certainty"], "differential": f["differential"] or [], "image_quality": f["image_quality"],
                           "guidance_level": f["guidance_level"], "model": f["model_version"]},
            "farmer_feedback": {"followed": f["followed"], "outcome": f["outcome"], "diagnosis_wrong": f["outcome"] == "diagnosis_wrong",
                                "kind": "farmer_reported"},
            "later_observation": later(f["farm_id"], f["created_at"], "disease"),
        })
    return {"contract_version": EVALUATION_CONTRACT_VERSION, "generated_at": datetime.utcnow().isoformat() + "Z", "use_policy": EVALUATION_USE_POLICY,
            "label": EVALUATION_LABEL, "count": len(records), "records": records[:limit], "provenance": EVALUATION_PROVENANCE}

"""Rules the diagnosis model cannot override: treatment gating, guidance level and expert escalation.

Thresholds are configurable (settings.DIAGNOSIS_*), but never below "moderate": a low-certainty or
uncertain photo check never produces chemical options and always recommends expert review.
"""
from datetime import datetime, timezone
from typing import Optional, Protocol
from uuid import uuid4

from config import settings
from models.diagnosis import AIDiagnosis
from services.disease_reference_service import disease_reference_service
from services.kvk_service import KVK_PROVENANCE

RANK = {"low": 0, "moderate": 1, "high": 2}
CASE_SCHEMA_VERSION = "1.0"
CASE_LOCATION_DECIMALS = 2  # ~1 km: enough for a KVK to know the locality, not the field


def _at_least(level: Optional[str], minimum: str) -> bool:
    return level is not None and RANK[level] >= RANK[minimum]


def apply_safety_rules(ai: AIDiagnosis, crop: str | None) -> tuple[AIDiagnosis, dict | None]:
    """Post-validation rules. Chemical options survive only with a verified reference and enough certainty."""
    reference = disease_reference_service.get(ai.reference_id, crop)

    if ai.diagnosis_status in ("not_a_plant", "healthy"):
        ai.disease_name = ai.disease_name_en = ai.scientific_name = None
        ai.severity = ai.spread_risk = None
        ai.treatment.chemical = []
        ai.differential = []
        if ai.diagnosis_status == "not_a_plant":
            ai.treatment.immediate = ai.treatment.organic = ai.treatment.prevention = []

    if ai.diagnosis_status == "uncertain" and ai.certainty == "high":
        ai.certainty = "moderate"

    # The UI always shows a "confirm product and dose with your KVK" warning next to chemical options.
    if not reference or ai.diagnosis_status != "disease_detected" or not _at_least(ai.certainty, settings.DIAGNOSIS_CHEMICAL_MIN_CERTAINTY):
        ai.treatment.chemical = []
    return ai, reference


def guidance(ai: AIDiagnosis, reference: dict | None) -> dict:
    """supported: act on the steps shown; cautious: act carefully and verify; escalate: get an expert to look first."""
    thresholds = {"chemical_min_certainty": settings.DIAGNOSIS_CHEMICAL_MIN_CERTAINTY,
                  "supported_min_certainty": settings.DIAGNOSIS_SUPPORTED_MIN_CERTAINTY}
    if ai.diagnosis_status in ("healthy", "not_a_plant"):
        return {"level": "none", "reasons": [], "thresholds": thresholds}
    reasons = []
    if ai.diagnosis_status == "uncertain":
        reasons.append("cause_uncertain")
    if ai.certainty == "low":
        reasons.append("low_certainty")
    if ai.image_quality == "poor":
        reasons.append("poor_photo")
    if reasons:
        return {"level": "escalate", "reasons": reasons, "thresholds": thresholds}
    if not reference:
        reasons.append("no_verified_reference")
    if not _at_least(ai.certainty, settings.DIAGNOSIS_SUPPORTED_MIN_CERTAINTY):
        reasons.append("moderate_certainty")
    if ai.severity == "high":
        reasons.append("high_severity")
    return {"level": "cautious" if reasons else "supported", "reasons": reasons, "thresholds": thresholds}


def build_case(ai: AIDiagnosis, reference: dict | None, crop: str | None, crop_stage: dict | None, lat: float | None, lng: float | None,
               weather: dict | None, nearby: list[dict] | None, guidance_level: str) -> dict:
    """Structured case for an agricultural expert. It carries the AI result labelled as such and never the photo:
    the farmer attaches it when sharing, so no image leaves the device without their action."""
    return {
        "schema_version": CASE_SCHEMA_VERSION,
        "case_id": str(uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "country_code": "IN",
        "crop": crop,
        "crop_stage": (crop_stage or {}).get("stage"),
        "location": {"lat": round(lat, CASE_LOCATION_DECIMALS), "lng": round(lng, CASE_LOCATION_DECIMALS)} if lat is not None and lng is not None else None,
        "ai_diagnosis": {
            "kind": "ai_generated", "model": settings.GEMINI_DIAGNOSIS_MODEL, "status": ai.diagnosis_status,
            "possible_disease": (reference or {}).get("name") or ai.disease_name_en, "scientific_name": ai.scientific_name,
            "certainty": ai.certainty, "certainty_reason": ai.certainty_reason, "severity": ai.severity,
            "observed_symptoms": ai.observed_symptoms, "alternative_causes": ai.alternative_causes,
            "differential": [d.model_dump() for d in ai.differential], "guidance_level": guidance_level,
            "verified_reference_id": (reference or {}).get("id"),
        },
        "weather": {k: weather.get(k) for k in ("temp", "humidity", "rainfall", "valid_at")} | {"kind": "model_estimate"} if weather else None,
        "nearby_reports": [{"disease": o["disease"], "report_count": o["report_count"], "distance_km": o["distance_km"],
                            "kind": "ai_classified_user_reports"} for o in (nearby or [])[:3]],
        "image_included": False,
        "note": "AI-generated assessment for expert review. Not a confirmed diagnosis.",
    }


class EscalationSink(Protocol):
    """Where a case goes. A KVK or state extension system implements `submit` and returns its own case reference."""
    name: str

    async def submit(self, case: dict) -> dict: ...


class NotConnectedSink:
    """No extension system is integrated yet: the case is returned to the farmer to share themselves."""
    name = "none"

    async def submit(self, case: dict) -> dict:
        return {"status": "not_submitted", "reason": "no_kvk_integration", "channel": "farmer_shares_case"}


escalation_sink: EscalationSink = NotConnectedSink()


async def escalation(level: str, reasons: list[str], kvk: dict | None, case: dict) -> dict | None:
    """Expert review is advised for 'escalate', and for 'cautious' results of high severity."""
    if level != "escalate" and not (level == "cautious" and "high_severity" in reasons):
        return None
    return {
        "recommended": True,
        "reason": "expert_review_needed" if level == "escalate" else "high_severity_unconfirmed",
        "kvk": {**kvk, "provenance": KVK_PROVENANCE} if kvk else None,
        "kvk_portal": KVK_PROVENANCE["verify_url"],
        "case": case,
        "submission": await escalation_sink.submit(case),
    }

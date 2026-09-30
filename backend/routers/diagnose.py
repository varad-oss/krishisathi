import asyncio
import base64
import logging
import time
from datetime import date

from fastapi import APIRouter, Depends, File, Form, Header, UploadFile

from config import settings
from core.errors import ApiError
from core.idempotency import get_idempotency_result, set_idempotency_result
from core.events import log_event
from core.rate_limit import ai_rate_limit
from models.diagnosis import MAX_IMAGE_BYTES, DiagnosisRequest, DiagnosisResponse, DiseaseReference, Language
from models.exceptions import ServiceUnavailableException
from services.bigquery_service import bq_service
from services import farm_twin
from services.crop_stage import estimate_stage
from services.crops import normalize_crop
from services.diagnosis_policy import apply_safety_rules, build_case, escalation, guidance
from services.disease_reference_service import disease_reference_service
from services.earth_engine_service import earth_engine_service
from services.gemini_service import gemini_service, one_line
from services.images import sniff_image
from services.kvk_service import kvk_service
from services.persistence_service import nearby_outbreaks, persistence_service
from services.weather_service import weather_service

router = APIRouter(dependencies=[Depends(ai_rate_limit)], prefix="/api/diagnose", tags=["Diagnose"])
logger = logging.getLogger(__name__)


def _weather_block(weather: dict | None) -> str:
    if not weather:
        return "UNAVAILABLE"
    return (
        f"Temperature {weather.get('temp')} °C, humidity {weather.get('humidity')} %, "
        f"precipitation {weather.get('rainfall')} mm (model estimate valid at {weather.get('valid_at')})"
    )


def _farm_block(stage: dict, nearby: list[dict] | None, satellite: dict | None) -> str:
    """Context lines for the model. Names from stored reports are collapsed to one line (they came from earlier model output)."""
    lines = []
    if stage.get("status") == "estimated":
        lines.append(f"Crop stage: {stage['stage']} (estimated from the sowing date with FAO-56 typical stage lengths, "
                     f"day {stage['days_since_sowing']})")
    if nearby is None:
        lines.append("Nearby reports: UNAVAILABLE")
    elif nearby:
        lines.append("Nearby reports (AI-classified farmer photos, not lab-confirmed): " + "; ".join(
            f"{one_line(o['disease'], 80)}, {o['report_count']} reports within about {o['distance_km']} km" for o in nearby[:3]))
    if satellite and satellite.get("status") == "available" and satellite.get("change") is not None:
        lines.append(f"Satellite NDVI (Sentinel-2): {satellite['ndvi']}, change {satellite['change']} over the previous 30 days")
    return "\n".join(lines)


async def safe_log_diagnosis(log_data: dict):
    try:
        await bq_service.log_diagnosis(log_data)
    except Exception as e:
        logger.error("Failed to log diagnosis telemetry to BigQuery (non-durable): %s", e)


async def _weather(latitude, longitude):
    try:
        return await weather_service.get_current_weather(latitude, longitude), "used"
    except ServiceUnavailableException:
        return None, "unavailable"


async def _nearby(latitude, longitude, crop):
    try:
        return nearby_outbreaks(await persistence_service.get_outbreaks(), latitude, longitude, crop)
    except Exception:
        return None


async def _farm(farm_id: str | None, token: str | None):
    if not farm_id:
        return None, "not_provided"
    try:
        return await farm_twin.authorize(farm_id, token), "linked"
    except ApiError:
        return None, "not_linked"  # a stale token must not block a diagnosis


async def process_diagnosis(image_bytes: bytes, crop_type: str | None, latitude: float | None, longitude: float | None, language: str,
                            sowing_date: date | None = None, farm_id: str | None = None, farm_token: str | None = None) -> dict:
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise ApiError(413, "PAYLOAD_TOO_LARGE", "Image too large (max 5 MB).")
    mime_type = sniff_image(image_bytes)
    start = time.perf_counter()

    farm, farm_status = await _farm(farm_id, farm_token)
    if farm:  # the farm record fills what the request left out
        crop_type = crop_type or farm.crop
        sowing_date = sowing_date or farm.sowing_date
        if latitude is None or longitude is None:
            latitude, longitude = farm.lat, farm.lng
    crop = normalize_crop(crop_type)
    has_location = latitude is not None and longitude is not None

    weather, weather_status, nearby = None, "not_provided", None
    if has_location:
        (weather, weather_status), nearby = await asyncio.gather(_weather(latitude, longitude), _nearby(latitude, longitude, crop))
    stage = estimate_stage(crop, sowing_date, date.today())
    satellite = earth_engine_service.peek_point_crop_health(latitude, longitude) if has_location else None

    ai = await gemini_service.diagnose_crop_disease(
        image_bytes, mime_type, crop, language,
        disease_reference_service.get_grounding_context(crop, None),
        _weather_block(weather),
        _farm_block(stage, nearby if has_location else [], satellite),
    )
    ai, reference = apply_safety_rules(ai, crop)
    advice = guidance(ai, reference)
    kvk = kvk_service.get_nearest_kvk(latitude, longitude) if has_location else None
    case = build_case(ai, reference, crop, stage, latitude, longitude, weather, nearby, advice["level"])
    referral = await escalation(advice["level"], advice["reasons"], kvk, case)

    canonical_name = (reference or {}).get("name") or ai.disease_name_en
    recorded, diagnosis_id = True, None
    try:
        diagnosis_id = await persistence_service.save_diagnosis(
            {
                "disease_name": canonical_name,
                "diagnosis_status": ai.diagnosis_status,
                "certainty": ai.certainty,
                "severity": ai.severity,
                "spread_risk": ai.spread_risk,
                "image_quality": ai.image_quality,
                "guidance_level": advice["level"],
                "differential": [{"name": d.name, "likelihood": d.likelihood} for d in ai.differential],
                "model_version": settings.GEMINI_DIAGNOSIS_MODEL,
            },
            crop, latitude, longitude, language, farm_id=farm.id if farm else None,
        )
    except Exception as e:
        # The farmer still gets the diagnosis; the response says it was not recorded.
        logger.error("Failed to persist diagnosis: %s", e)
        recorded = False

    twin = None
    if farm and recorded and ai.diagnosis_status != "not_a_plant":
        # Lets the farmer later say what they did and whether the diagnosis was right.
        action = "consult_expert" if referral else "routine_monitoring" if advice["level"] == "none" else "treat_as_advised"
        try:
            twin = {"action": await farm_twin.record_action(farm, "diagnosis", str(diagnosis_id), action, category="disease",
                                                             severity=ai.severity, confidence=ai.certainty)}
        except Exception as e:
            logger.error("Failed to record diagnosis action: %s", e)

    asyncio.create_task(safe_log_diagnosis({
        "crop_type": crop,
        "disease_name": canonical_name,
        "diagnosis_status": ai.diagnosis_status,
        "certainty": ai.certainty,
        "severity": ai.severity,
    }))
    log_event("diagnosis_performed", farm_id=farm.id if farm else None, crop=crop, status=ai.diagnosis_status, certainty=ai.certainty,
              guidance=advice["level"], escalated=bool(referral), reference_matched=bool(reference), model=settings.GEMINI_DIAGNOSIS_MODEL,
              latency_ms=round((time.perf_counter() - start) * 1000, 1))

    return DiagnosisResponse(
        status=ai.diagnosis_status,
        certainty=ai.certainty,
        certainty_reason=ai.certainty_reason,
        image_quality=ai.image_quality,
        disease_name=ai.disease_name,
        scientific_name=ai.scientific_name,
        affected_part=ai.affected_part,
        observed_symptoms=ai.observed_symptoms,
        alternative_causes=ai.alternative_causes,
        severity=ai.severity,
        spread_risk=ai.spread_risk,
        urgency=ai.urgency,
        treatment=ai.treatment,
        summary=ai.summary,
        reference=DiseaseReference(**{k: reference.get(k) for k in DiseaseReference.model_fields}) if reference else None,
        differential=ai.differential,
        guidance=advice,
        escalation=referral,
        context_used={
            "crop": "provided" if crop else "not_provided",
            "location": "provided" if has_location else "not_provided",
            "weather": weather_status,
            "reference": "matched" if reference else "none_found",
            "crop_stage": "used" if stage["status"] == "estimated" else "not_provided",
            "nearby_reports": "not_provided" if not has_location else "unavailable" if nearby is None else "used" if nearby else "none_found",
            "satellite": "used" if satellite and satellite.get("status") == "available" and satellite.get("change") is not None else "not_provided",
            "farm": farm_status,
        },
        recorded=recorded,
        language=language,
        generated_by={"kind": "ai_model", "model": settings.GEMINI_DIAGNOSIS_MODEL},
        twin=twin,
    ).model_dump()


async def _with_idempotency(key: str | None, work):
    if key:
        cached = await get_idempotency_result(key)
        if cached:
            return cached
    result = await work()
    if key:
        await set_idempotency_result(key, result)
    return result


@router.post("", response_model=DiagnosisResponse)
async def diagnose_multipart(
    file: UploadFile = File(...),
    crop_type: str | None = Form(None, max_length=40),
    latitude: float | None = Form(None, ge=-90, le=90),
    longitude: float | None = Form(None, ge=-180, le=180),
    language: Language = Form("en"),
    sowing_date: date | None = Form(None),
    farm_id: str | None = Form(None, min_length=36, max_length=36),
    idempotency_key: str | None = Header(None, alias="Idempotency-Key", max_length=100),
    farm_token: str | None = Header(None, alias="X-Farm-Token", max_length=100),
):
    contents = bytearray()
    while chunk := await file.read(1024 * 1024):
        contents.extend(chunk)
        if len(contents) > MAX_IMAGE_BYTES:
            raise ApiError(413, "PAYLOAD_TOO_LARGE", "Image too large (max 5 MB).")
    return await _with_idempotency(
        idempotency_key,
        lambda: process_diagnosis(bytes(contents), crop_type, latitude, longitude, language, sowing_date, farm_id, farm_token),
    )


@router.post("/base64", response_model=DiagnosisResponse)
async def diagnose_base64(request: DiagnosisRequest, idempotency_key: str | None = Header(None, alias="Idempotency-Key", max_length=100),
                          farm_token: str | None = Header(None, alias="X-Farm-Token", max_length=100)):
    contents = base64.b64decode(request.image)
    return await _with_idempotency(
        idempotency_key,
        lambda: process_diagnosis(contents, request.crop_type, request.latitude, request.longitude, request.language,
                                  request.sowing_date, request.farm_id, farm_token),
    )

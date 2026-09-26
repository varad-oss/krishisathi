import asyncio
import base64
import logging

from fastapi import APIRouter, Depends, File, Form, Header, UploadFile

from config import settings
from core.errors import ApiError
from core.idempotency import get_idempotency_result, set_idempotency_result
from core.rate_limit import ai_rate_limit
from models.diagnosis import MAX_IMAGE_BYTES, AIDiagnosis, DiagnosisRequest, DiagnosisResponse, DiseaseReference, Language
from models.exceptions import ServiceUnavailableException
from services.bigquery_service import bq_service
from services.crops import normalize_crop
from services.disease_reference_service import disease_reference_service
from services.gemini_service import gemini_service
from services.images import sniff_image
from services.persistence_service import persistence_service
from services.weather_service import weather_service

router = APIRouter(dependencies=[Depends(ai_rate_limit)], prefix="/api/diagnose", tags=["Diagnose"])
logger = logging.getLogger(__name__)

def apply_safety_rules(ai: AIDiagnosis, crop: str | None) -> tuple[AIDiagnosis, dict | None]:
    """Post-validation rules that the model cannot override."""
    reference = disease_reference_service.get(ai.reference_id, crop)

    if ai.diagnosis_status in ("not_a_plant", "healthy"):
        ai.disease_name = ai.disease_name_en = ai.scientific_name = None
        ai.severity = ai.spread_risk = None
        ai.treatment.chemical = []
        if ai.diagnosis_status == "not_a_plant":
            ai.treatment.immediate = ai.treatment.organic = ai.treatment.prevention = []

    # Chemical options are only shown when they come from a verified reference entry and
    # the model is not unsure. Otherwise the UI directs the farmer to the local KVK. The UI
    # always shows a localized "confirm product and dose with your KVK" warning next to them.
    if not reference or ai.diagnosis_status == "uncertain" or ai.certainty == "low":
        ai.treatment.chemical = []

    if ai.diagnosis_status == "uncertain" and ai.certainty == "high":
        ai.certainty = "moderate"
    return ai, reference


def _weather_block(weather: dict | None) -> str:
    if not weather:
        return "UNAVAILABLE"
    return (
        f"Temperature {weather.get('temp')} °C, humidity {weather.get('humidity')} %, "
        f"precipitation {weather.get('rainfall')} mm (model estimate valid at {weather.get('valid_at')})"
    )


async def safe_log_diagnosis(log_data: dict):
    try:
        await bq_service.log_diagnosis(log_data)
    except Exception as e:
        logger.error("Failed to log diagnosis telemetry to BigQuery (non-durable): %s", e)


async def process_diagnosis(image_bytes: bytes, crop_type: str | None, latitude: float | None,
                            longitude: float | None, language: str) -> dict:
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise ApiError(413, "PAYLOAD_TOO_LARGE", "Image too large (max 5 MB).")
    mime_type = sniff_image(image_bytes)
    crop = normalize_crop(crop_type)
    has_location = latitude is not None and longitude is not None

    weather, weather_status = None, "not_provided"
    if has_location:
        try:
            weather = await weather_service.get_current_weather(latitude, longitude)
            weather_status = "used"
        except ServiceUnavailableException:
            weather_status = "unavailable"

    ai = await gemini_service.diagnose_crop_disease(
        image_bytes, mime_type, crop, language,
        disease_reference_service.get_grounding_context(crop, None),
        _weather_block(weather),
    )
    ai, reference = apply_safety_rules(ai, crop)

    canonical_name = (reference or {}).get("name") or ai.disease_name_en
    recorded = True
    try:
        await persistence_service.save_diagnosis(
            {
                "disease_name": canonical_name,
                "diagnosis_status": ai.diagnosis_status,
                "certainty": ai.certainty,
                "severity": ai.severity,
                "spread_risk": ai.spread_risk,
            },
            crop, latitude, longitude, language,
        )
    except Exception as e:
        # The farmer still gets the diagnosis; the response says it was not recorded.
        logger.error("Failed to persist diagnosis: %s", e)
        recorded = False

    asyncio.create_task(safe_log_diagnosis({
        "crop_type": crop,
        "disease_name": canonical_name,
        "diagnosis_status": ai.diagnosis_status,
        "certainty": ai.certainty,
        "severity": ai.severity,
    }))

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
        context_used={
            "crop": "provided" if crop else "not_provided",
            "location": "provided" if has_location else "not_provided",
            "weather": weather_status,
            "reference": "matched" if reference else "none_found",
        },
        recorded=recorded,
        language=language,
        generated_by={"kind": "ai_model", "model": settings.GEMINI_DIAGNOSIS_MODEL},
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
    idempotency_key: str | None = Header(None, alias="Idempotency-Key", max_length=100),
):
    contents = bytearray()
    while chunk := await file.read(1024 * 1024):
        contents.extend(chunk)
        if len(contents) > MAX_IMAGE_BYTES:
            raise ApiError(413, "PAYLOAD_TOO_LARGE", "Image too large (max 5 MB).")
    return await _with_idempotency(
        idempotency_key,
        lambda: process_diagnosis(bytes(contents), crop_type, latitude, longitude, language),
    )


@router.post("/base64", response_model=DiagnosisResponse)
async def diagnose_base64(request: DiagnosisRequest, idempotency_key: str | None = Header(None, alias="Idempotency-Key", max_length=100)):
    contents = base64.b64decode(request.image)
    return await _with_idempotency(
        idempotency_key,
        lambda: process_diagnosis(contents, request.crop_type, request.latitude, request.longitude, request.language),
    )

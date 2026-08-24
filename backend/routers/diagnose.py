import base64
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from models.diagnosis import DiagnosisRequest, DiagnosisResponse
from services.gemini_service import gemini_service
from services.weather_service import weather_service
from services.translation import translation_service
from services.bigquery_service import bq_service
import asyncio

router = APIRouter(prefix="/api/diagnose", tags=["Diagnose"])

@router.post("", response_model=DiagnosisResponse)
async def diagnose_multipart(
    file: UploadFile = File(...),
    crop_type: str = Form(None),
    latitude: float = Form(...),
    longitude: float = Form(...),
    language: str = Form('en')
):
    try:
        contents = await file.read()
        return await process_diagnosis(contents, crop_type, latitude, longitude, language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/base64", response_model=DiagnosisResponse)
async def diagnose_base64(request: DiagnosisRequest):
    try:
        if "," in request.image:
            image_data = request.image.split(",")[1]
        else:
            image_data = request.image
        
        contents = base64.b64decode(image_data)
        return await process_diagnosis(
            contents, request.crop_type, request.latitude, request.longitude, request.language
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_diagnosis(image_bytes: bytes, crop_type: str, latitude: float, longitude: float, language: str) -> dict:
    weather = await weather_service.get_current_weather(latitude, longitude)
    context = {
        "location": {"lat": latitude, "lng": longitude},
        "weather": weather
    }
    
    diagnosis_data = gemini_service.diagnose_crop_disease(image_bytes, crop_type, context)
    
    # Translate strings if language is not English
    if language != 'en':
        diagnosis_data["disease_name"] = translation_service.translate_text(diagnosis_data["disease_name"], 'en', language)
        diagnosis_data["affected_part"] = translation_service.translate_text(diagnosis_data["affected_part"], 'en', language)
        diagnosis_data["severity"] = translation_service.translate_text(diagnosis_data["severity"], 'en', language)
        diagnosis_data["spread_risk"] = translation_service.translate_text(diagnosis_data["spread_risk"], 'en', language)
        diagnosis_data["image_analysis_summary"] = translation_service.translate_text(diagnosis_data["image_analysis_summary"], 'en', language)
        diagnosis_data["advisory_text"] = translation_service.translate_text(diagnosis_data["advisory_text"], 'en', language)
        
        for key in diagnosis_data.get("treatment", {}):
            diagnosis_data["treatment"][key] = [
                translation_service.translate_text(step, 'en', language)
                for step in diagnosis_data["treatment"][key]
            ]
            
    diagnosis_data["language"] = language
    
    # Log to BigQuery (fire and forget)
    log_data = {
        "crop_type": crop_type,
        "disease_name": diagnosis_data.get("disease_name"),
        "confidence": diagnosis_data.get("confidence"),
        "severity": diagnosis_data.get("severity"),
        "latitude": latitude,
        "longitude": longitude
    }
    asyncio.create_task(bq_service.log_diagnosis(log_data))
    
    return diagnosis_data

from fastapi import APIRouter, HTTPException
from models.advisory import AdvisoryRequest, AdvisoryResponse, VoiceAdvisoryRequest, VoiceAdvisoryResponse
from services.gemini_service import gemini_service
from services.weather_service import weather_service
from services.translation import translation_service
import base64

router = APIRouter(prefix="/api/advisory", tags=["Advisory"])

@router.post("", response_model=AdvisoryResponse)
async def get_advisory(request: AdvisoryRequest):
    try:
        # Get weather context
        weather = await weather_service.get_current_weather(request.latitude, request.longitude)
        
        # Translate query to English if needed
        query_en = request.query
        if request.language != 'en':
            query_en = translation_service.translate_text(request.query, request.language, 'en')
            
        context = {
            "weather": weather,
            "crop_type": request.crop_type,
            "location": {"lat": request.latitude, "lng": request.longitude}
        }
        
        # Get advisory from Gemini
        advisory_en = gemini_service.generate_advisory(query_en, context)
        
        # Translate back if needed
        advisory_final = advisory_en
        translated_text = None
        if request.language != 'en':
            advisory_final = translation_service.translate_text(advisory_en, 'en', request.language)
            translated_text = advisory_final
            
        return AdvisoryResponse(
            advisory_text=advisory_final,
            advisory_type="general",
            data_sources=["weather", "gemini"],
            language=request.language,
            translated_text=translated_text
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import StreamingResponse
import io
from gtts import gTTS

@router.post("/voice", response_model=VoiceAdvisoryResponse)
async def get_voice_advisory(request: VoiceAdvisoryRequest):
    # In a real app, use Google Cloud Speech-to-Text here (needs billing)
    # For zero-billing constraint, we mock STT or could use local models
    mock_transcription = "What is the best time to water my wheat crops?"
    
    # Process like normal text advisory
    advisory_req = AdvisoryRequest(
        query=mock_transcription,
        latitude=request.latitude,
        longitude=request.longitude,
        language=request.language
    )
    
    advisory_response = await get_advisory(advisory_req)
    
    # Generate audio using gTTS
    tts = gTTS(text=advisory_response.advisory_text, lang=request.language if request.language in ['en', 'hi', 'mr', 'ta', 'te', 'bn', 'pt', 'ru', 'zh'] else 'en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    audio_b64 = base64.b64encode(fp.getvalue()).decode('utf-8')
    
    return VoiceAdvisoryResponse(
        transcribed_text=mock_transcription,
        advisory=advisory_response,
        audio_response_base64=audio_b64
    )

@router.get("/tts")
async def text_to_speech(text: str, lang: str = "en"):
    """Generate audio file for WhatsApp webhook media URLs"""
    try:
        # Check if lang is supported by gTTS, fallback to en
        safe_lang = lang if lang in ['en', 'hi', 'mr', 'ta', 'te', 'bn', 'pt', 'ru', 'zh'] else 'en'
        tts = gTTS(text=text, lang=safe_lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return StreamingResponse(fp, media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@router.post("/voice", response_model=VoiceAdvisoryResponse)
async def get_voice_advisory(request: VoiceAdvisoryRequest):
    # In a real app, use Google Cloud Speech-to-Text here
    # For demo purposes, we'll mock the STT step
    mock_transcription = "What is the best time to water my wheat crops?"
    
    # Process like normal text advisory
    advisory_req = AdvisoryRequest(
        query=mock_transcription,
        latitude=request.latitude,
        longitude=request.longitude,
        language=request.language
    )
    
    advisory_response = await get_advisory(advisory_req)
    
    # In a real app, use Google Cloud Text-to-Speech here
    # For demo, return dummy base64 string
    dummy_audio_b64 = base64.b64encode(b"dummy audio content").decode('utf-8')
    
    return VoiceAdvisoryResponse(
        transcribed_text=mock_transcription,
        advisory=advisory_response,
        audio_response_base64=dummy_audio_b64
    )

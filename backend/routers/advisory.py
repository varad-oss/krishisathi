import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import io
import base64
from gtts import gTTS
from google import genai
from google.genai import types

from models.advisory import AdvisoryRequest, AdvisoryResponse, VoiceAdvisoryRequest, VoiceAdvisoryResponse
from services.gemini_service import gemini_service
from services.weather_service import weather_service
from services.translation import translation_service
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/advisory", tags=["Advisory"])

def get_audio_mime_type(audio_bytes: bytes) -> str:
    if audio_bytes.startswith(b'RIFF'):
        return 'audio/wav'
    elif audio_bytes.startswith(b'\x1A\x45\xdf\xa3'):
        return 'audio/webm'
    elif audio_bytes.startswith(b'OggS'):
        return 'audio/ogg'
    else:
        return 'audio/mp3'


from pydantic import BaseModel
class TranscribeRequest(BaseModel):
    audio_base64: str
    language: str = 'en'

@router.post("/transcribe")
async def transcribe_audio(request: TranscribeRequest):
    try:
        audio_bytes = base64.b64decode(request.audio_base64)
        mime_type = get_audio_mime_type(audio_bytes)
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
        
        response = client.models.generate_content(
            model='gemini-flash-lite-latest',
            contents=[
                audio_part, 
                f"Transcribe the audio exactly. You MUST output the text in the native script of the language code '{request.language}' (e.g. use Devanagari for hi/mr, Gujarati script for gu, Tamil script for ta, etc). Do NOT romanize or use English letters unless the user actually spoke English. Return only the transcribed text, nothing else."
            ]
        )
        
        transcribed_text = response.text.strip()
        return {"text": transcribed_text}
    except Exception as e:
        logger.error(f"Error in transcribe_audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=AdvisoryResponse)
async def get_advisory(request: AdvisoryRequest):
    try:
        weather = await weather_service.get_current_weather(request.latitude, request.longitude)
        
        query_en = request.query
        if request.language != 'en':
            query_en = translation_service.translate_text(request.query, request.language, 'en')
            
        context = {
            "weather": weather,
            "crop_type": request.crop_type,
            "location": {"lat": request.latitude, "lng": request.longitude}
        }
        
        # Try agent first (Task T1.3)
        try:
            from services.agent_service import agent_service
            advisory_en = agent_service.process_advisory(query_en, context, image_base64=request.image_base64)
        except Exception as e:
            logger.warning(f"Agent service failed, falling back to deterministic generation: {e}")
            advisory_en = gemini_service.generate_advisory(query_en, context, image_base64=request.image_base64)
        
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
        logger.error(f"Error in get_advisory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/followup")
async def get_followup_advisory(request: AdvisoryRequest, disease_name: str = '', severity: str = '', crop_type: str = ''):
    """
    Follow-up advisory that includes disease reference grounding.
    Unlike the generic advisory, this NEVER returns a silent mock fallback — 
    it raises an HTTP error so the frontend can show a real error state.
    """
    try:
        from services.disease_reference_service import disease_reference_service
        
        # Get grounding context from the orphaned disease reference data
        grounding = disease_reference_service.get_grounding_context(crop_type, '')
        
        # Build enriched query with diagnosis context
        context_prefix = f"The farmer's crop has been diagnosed with {disease_name} (severity: {severity}). "
        context_prefix += f"Reference data: {grounding}\n\n"
        enriched_query = context_prefix + "Farmer's follow-up question: " + request.query
        
        weather = await weather_service.get_current_weather(request.latitude, request.longitude)
        
        query_en = enriched_query
        if request.language != 'en':
            query_en = translation_service.translate_text(enriched_query, request.language, 'en')
        
        context = {
            "weather": weather,
            "crop_type": crop_type or request.crop_type,
            "location": {"lat": request.latitude, "lng": request.longitude},
            "diagnosis_context": f"{disease_name} ({severity})"
        }
        
        advisory_en = gemini_service.generate_advisory(query_en, context, image_base64=request.image_base64)
        
        advisory_final = advisory_en
        if request.language != 'en':
            advisory_final = translation_service.translate_text(advisory_en, 'en', request.language)
        
        return AdvisoryResponse(
            advisory_text=advisory_final,
            advisory_type="followup",
            data_sources=["weather", "gemini", "disease_reference"],
            language=request.language,
            translated_text=advisory_final if request.language != 'en' else None
        )
    except Exception as e:
        logger.error(f"Error in followup advisory: {e}")
        raise HTTPException(status_code=500, detail=f"Advisory service unavailable: {str(e)}")

@router.post("/voice", response_model=VoiceAdvisoryResponse)
async def get_voice_advisory(request: VoiceAdvisoryRequest):
    try:
        audio_bytes = base64.b64decode(request.audio_base64)
        mime_type = get_audio_mime_type(audio_bytes)
        
        # 1. Native Gemini Audio Transcription
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
        
        response = client.models.generate_content(
            model='gemini-flash-lite-latest',
            contents=[
                audio_part, 
                "Transcribe the audio exactly. Return only the transcribed text, nothing else."
            ]
        )
        
        transcribed_text = response.text.strip()
        logger.info(f"Transcribed audio to: {transcribed_text}")
        
        advisory_req = AdvisoryRequest(
            query=transcribed_text,
            latitude=request.latitude,
            longitude=request.longitude,
            language=request.language
        )
        
        advisory_response = await get_advisory(advisory_req)
        
        tts_lang = request.language if request.language in ['en', 'hi', 'mr', 'ta', 'te', 'bn', 'pt', 'ru', 'zh'] else 'en'
        tts = gTTS(text=advisory_response.advisory_text, lang=tts_lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        audio_b64 = base64.b64encode(fp.getvalue()).decode('utf-8')
        
        return VoiceAdvisoryResponse(
            transcribed_text=transcribed_text,
            advisory=advisory_response,
            audio_response_base64=audio_b64
        )
    except Exception as e:
        logger.error(f"Error in get_voice_advisory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tts")
async def text_to_speech(text: str, lang: str = "en"):
    try:
        from fastapi import Response
        safe_lang = lang if lang in ['en', 'hi', 'mr', 'ta', 'te', 'bn', 'pt', 'ru', 'zh'] else 'en'
        tts = gTTS(text=text, lang=safe_lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        audio_data = fp.getvalue()
        return Response(content=audio_data, media_type="audio/mpeg")
    except Exception as e:
        logger.error(f"Error in text_to_speech: {e}")
        raise HTTPException(status_code=500, detail=str(e))

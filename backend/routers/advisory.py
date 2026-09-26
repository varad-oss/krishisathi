import asyncio
import base64
import io
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from gtts import gTTS

from core.errors import ApiError
from core.rate_limit import ai_rate_limit, tts_rate_limit
from models.advisory import (
    AdvisoryRequest,
    AdvisoryResponse,
    FollowUpRequest,
    TranscribeRequest,
    VoiceAdvisoryRequest,
    VoiceAdvisoryResponse,
)
from models.diagnosis import Language
from services.advisory_context import build_context
from services.crops import normalize_crop
from services.gemini_service import gemini_service, one_line
from services.images import sniff_image
from services.persistence_service import persistence_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/advisory", tags=["Advisory"])
ai_limited = [Depends(ai_rate_limit)]

TTS_MAX_CHARS = 1500


def get_audio_mime_type(audio_bytes: bytes) -> str:
    if audio_bytes.startswith(b"RIFF"):
        return "audio/wav"
    if audio_bytes.startswith(b"\x1A\x45\xdf\xa3"):
        return "audio/webm"
    if audio_bytes.startswith(b"OggS"):
        return "audio/ogg"
    if audio_bytes.startswith((b"ID3", b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")):
        return "audio/mp3"
    if audio_bytes[4:8] == b"ftyp":
        return "audio/mp4"
    raise ApiError(415, "UNSUPPORTED_MEDIA_TYPE", "Unsupported audio format")


def _decode_image(image_base64: str | None) -> tuple[bytes | None, str | None]:
    if not image_base64:
        return None, None
    data = base64.b64decode(image_base64)
    return data, sniff_image(data)


async def _answer(request: AdvisoryRequest, advisory_type: str, diagnosis_context: str | None = None) -> AdvisoryResponse:
    crop = normalize_crop(request.crop_type)
    image_bytes, image_mime = _decode_image(request.image_base64)
    context_block, sources = await build_context(request.latitude, request.longitude, crop)
    text = await gemini_service.generate_advisory(
        request.query, context_block, request.language, crop,
        image_bytes=image_bytes, image_mime=image_mime, diagnosis_context=diagnosis_context,
    )

    recorded = True
    try:
        await persistence_service.save_advisory(
            request.query, text, crop, request.latitude, request.longitude, request.language,
            [s["id"] for s in sources if s["status"] == "used"],
        )
    except Exception as e:
        logger.error("Failed to persist advisory: %s", e)
        recorded = False

    return AdvisoryResponse(
        advisory_text=text,
        advisory_type=advisory_type,
        data_sources=sources,
        language=request.language,
        generated_at=datetime.now(timezone.utc).isoformat(),
        recorded=recorded,
    )


@router.post("", response_model=AdvisoryResponse, dependencies=ai_limited)
async def get_advisory(request: AdvisoryRequest):
    return await _answer(request, "general")


@router.post("/followup", response_model=AdvisoryResponse, dependencies=ai_limited)
async def get_followup_advisory(request: FollowUpRequest):
    """Follow-up question about an earlier photo diagnosis, grounded with disease reference data."""
    context = None
    if request.disease_name:
        context = one_line(request.disease_name)
        if request.severity:
            context += f" (severity: {request.severity})"
    return await _answer(request, "followup", diagnosis_context=context)


@router.post("/transcribe", dependencies=ai_limited)
async def transcribe_audio(request: TranscribeRequest):
    audio_bytes = base64.b64decode(request.audio_base64)
    text = await gemini_service.transcribe(audio_bytes, get_audio_mime_type(audio_bytes), request.language)
    return {"text": text}


async def _speak(text: str, lang: str) -> bytes:
    def render() -> bytes:
        fp = io.BytesIO()
        gTTS(text=text, lang=lang).write_to_fp(fp)
        return fp.getvalue()
    try:
        return await asyncio.wait_for(asyncio.to_thread(render), timeout=30)
    except Exception as e:
        logger.error("Text-to-speech failed: %s", e)
        raise ApiError(503, "SERVICE_UNAVAILABLE", "Text-to-speech is temporarily unavailable.")


@router.post("/voice", response_model=VoiceAdvisoryResponse, dependencies=ai_limited)
async def get_voice_advisory(request: VoiceAdvisoryRequest):
    audio_bytes = base64.b64decode(request.audio_base64)
    transcribed = await gemini_service.transcribe(audio_bytes, get_audio_mime_type(audio_bytes), request.language)
    if not transcribed:
        raise ApiError(422, "NO_SPEECH", "No speech was detected in the recording.")
    advisory = await _answer(
        AdvisoryRequest(query=transcribed[:2000], latitude=request.latitude, longitude=request.longitude,
                        crop_type=request.crop_type, language=request.language),
        "voice",
    )
    audio = await _speak(advisory.advisory_text[:TTS_MAX_CHARS], request.language)
    return VoiceAdvisoryResponse(
        transcribed_text=transcribed,
        advisory=advisory,
        audio_response_base64=base64.b64encode(audio).decode("utf-8"),
    )


@router.get("/tts", dependencies=[Depends(tts_rate_limit)])
async def text_to_speech(text: str = Query(..., min_length=1, max_length=TTS_MAX_CHARS), lang: Language = "en"):
    audio = await _speak(text, lang)
    return Response(content=audio, media_type="audio/mpeg", headers={"Cache-Control": "private, max-age=3600"})

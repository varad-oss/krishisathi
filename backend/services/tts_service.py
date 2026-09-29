"""Text-to-speech with a native-language voice for every supported language.

Provider order:
1. Gemini speech generation (natural, conversational voice) for the languages listed in
   settings.GEMINI_TTS_LANGUAGES, when a Gemini key is configured.
2. Google Translate TTS (gTTS). It has a native voice for all ten app languages, so a
   Hindi answer is never read by an English voice. English uses the Indian accent (co.in).

If both fail the endpoint returns 503; there is no silent fallback to a wrong-language voice.
"""
import asyncio
import hashlib
import io
import logging
import re
import wave
from collections import OrderedDict

from gtts import gTTS

from config import settings
from core.errors import ApiError
from models.exceptions import ServiceUnavailableException
from services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

LOCALES = {
    "en": "en-IN", "hi": "hi-IN", "mr": "mr-IN", "ta": "ta-IN", "te": "te-IN",
    "bn": "bn-IN", "kn": "kn-IN", "gu": "gu-IN", "pa": "pa-IN", "ml": "ml-IN",
}
# gTTS uses the language code for the voice; the top-level domain only changes the English accent.
GTTS_TLD = {"en": "co.in"}

_MARKUP = re.compile(r"[*_`#>|~]+")
_cache: "OrderedDict[str, tuple[bytes, str, str]]" = OrderedDict()
_CACHE_ENTRIES = 64


def speech_text(text: str) -> str:
    """Drops Markdown symbols that voices would otherwise read out ("asterisk", "hash")."""
    return " ".join(_MARKUP.sub(" ", text).split())


def gemini_languages() -> set[str]:
    return {c.strip() for c in settings.GEMINI_TTS_LANGUAGES.split(",") if c.strip()}


def pcm_to_wav(pcm: bytes, rate: int = 24_000) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)
    return buf.getvalue()


async def _gtts(text: str, lang: str) -> bytes:
    def render() -> bytes:
        fp = io.BytesIO()
        gTTS(text=text, lang=lang, tld=GTTS_TLD.get(lang, "com")).write_to_fp(fp)
        return fp.getvalue()
    return await asyncio.wait_for(asyncio.to_thread(render), timeout=30)


async def synthesize(text: str, lang: str) -> tuple[bytes, str, str]:
    """Returns (audio bytes, MIME type, provider id)."""
    text = speech_text(text)
    if not text:
        raise ApiError(422, "INVALID_INPUT", "There is no text to read aloud.")
    key = hashlib.sha256(f"{lang}\x00{text}".encode()).hexdigest()
    if key in _cache:
        _cache.move_to_end(key)
        return _cache[key]

    result = None
    if settings.GEMINI_TTS_MODEL and gemini_service.configured and lang in gemini_languages():
        try:
            pcm, rate = await gemini_service.speak(text, lang, LOCALES[lang])
            result = (pcm_to_wav(pcm, rate), "audio/wav", "gemini")
        except ServiceUnavailableException as e:
            logger.warning("Gemini TTS failed for %s, using gTTS: %s", lang, e.message)
    if result is None:
        try:
            result = (await _gtts(text, lang), "audio/mpeg", "gtts")
        except Exception as e:
            logger.error("gTTS failed for %s: %s", lang, e)
            raise ApiError(503, "SERVICE_UNAVAILABLE", "Text-to-speech is temporarily unavailable.")

    _cache[key] = result
    if len(_cache) > _CACHE_ENTRIES:
        _cache.popitem(last=False)
    return result

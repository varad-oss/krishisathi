"""Read-aloud voices and answer language: native voice per language, no English voice for Indic text."""
import io
import wave
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

import helpers  # noqa: F401
from config import settings
from main import app
from models.exceptions import ServiceUnavailableException
from services import tts_service
from services.gemini_service import gemini_service
from services.languages import is_in_language, script_ratio

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolate(monkeypatch):
    tts_service._cache.clear()
    from core import rate_limit
    rate_limit._local_windows.clear()
    monkeypatch.setattr(gemini_service, "client", object())  # "configured"
    yield
    tts_service._cache.clear()


# --- locale mapping and text cleanup ----------------------------------------------

def test_every_language_has_an_indian_locale():
    assert tts_service.LOCALES == {
        "en": "en-IN", "hi": "hi-IN", "mr": "mr-IN", "ta": "ta-IN", "te": "te-IN",
        "bn": "bn-IN", "kn": "kn-IN", "gu": "gu-IN", "pa": "pa-IN", "ml": "ml-IN",
    }


def test_markdown_symbols_are_not_read_out():
    assert tts_service.speech_text("## **पानी** दें\n- सुबह") == "पानी दें - सुबह"


def test_pcm_is_wrapped_as_playable_wav():
    wav = tts_service.pcm_to_wav(b"\x00\x00" * 2400, 24_000)
    with wave.open(io.BytesIO(wav)) as w:
        assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (1, 2, 24_000, 2400)


# --- provider chain ---------------------------------------------------------------

def test_gemini_voice_used_for_supported_language():
    with patch.object(gemini_service, "speak", AsyncMock(return_value=(b"\x00\x00" * 10, 24_000))) as speak, \
         patch.object(tts_service, "_gtts", AsyncMock()) as gtts:
        res = client.post("/api/advisory/tts", json={"text": "नमस्ते किसान", "language": "hi"})
    assert res.status_code == 200
    assert res.headers["content-type"] == "audio/wav"
    assert res.headers["x-tts-provider"] == "gemini" and res.headers["x-tts-locale"] == "hi-IN"
    assert speak.call_args.args[1:] == ("hi", "hi-IN")
    gtts.assert_not_called()


def test_gemini_failure_falls_back_to_native_gtts_voice():
    with patch.object(gemini_service, "speak", AsyncMock(side_effect=ServiceUnavailableException("quota"))), \
         patch.object(tts_service, "_gtts", AsyncMock(return_value=b"ID3mp3")) as gtts:
        res = client.post("/api/advisory/tts", json={"text": "नमस्कार शेतकरी", "language": "mr"})
    assert res.status_code == 200 and res.headers["x-tts-provider"] == "gtts"
    assert gtts.call_args.args == ("नमस्कार शेतकरी", "mr")  # same language, never an English voice


def test_language_outside_gemini_list_goes_to_gtts(monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_TTS_LANGUAGES", "en,hi")
    with patch.object(gemini_service, "speak", AsyncMock()) as speak, \
         patch.object(tts_service, "_gtts", AsyncMock(return_value=b"ID3")) as gtts:
        res = client.post("/api/advisory/tts", json={"text": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ", "language": "pa"})
    assert res.status_code == 200 and res.headers["x-tts-locale"] == "pa-IN"
    speak.assert_not_called()
    assert gtts.call_args.args[1] == "pa"


def test_english_uses_indian_accent():
    captured = {}

    class FakeGTTS:
        def __init__(self, text, lang, tld):
            captured.update(lang=lang, tld=tld)

        def write_to_fp(self, fp):
            fp.write(b"ID3")

    with patch.object(tts_service, "gTTS", FakeGTTS):
        import asyncio
        asyncio.run(tts_service._gtts("Irrigate tomorrow morning", "en"))
    assert captured == {"lang": "en", "tld": "co.in"}


def test_all_providers_failing_is_503_not_wrong_voice():
    with patch.object(gemini_service, "speak", AsyncMock(side_effect=ServiceUnavailableException("x"))), \
         patch.object(tts_service, "_gtts", AsyncMock(side_effect=RuntimeError("blocked"))):
        res = client.post("/api/advisory/tts", json={"text": "வணக்கம்", "language": "ta"})
    assert res.status_code == 503
    assert res.json()["error"]["code"] == "SERVICE_UNAVAILABLE"


def test_tts_input_validation():
    assert client.post("/api/advisory/tts", json={"text": "", "language": "hi"}).status_code == 422
    assert client.post("/api/advisory/tts", json={"text": "hi", "language": "fr"}).status_code == 422
    assert client.post("/api/advisory/tts", json={"text": "a" * 1501, "language": "hi"}).status_code == 422
    with patch.object(tts_service, "_gtts", AsyncMock()):
        assert client.post("/api/advisory/tts", json={"text": "** ##", "language": "hi"}).status_code == 422


def test_repeat_request_is_served_from_cache():
    with patch.object(gemini_service, "speak", AsyncMock(return_value=(b"\x00\x00", 24_000))) as speak:
        client.post("/api/advisory/tts", json={"text": "नमस्ते", "language": "hi"})
        client.post("/api/advisory/tts", json={"text": "नमस्ते", "language": "hi"})
    assert speak.call_count == 1


# --- answer language ---------------------------------------------------------------

def test_script_ratio():
    assert script_ratio("पानी दें", "hi") == 1.0
    assert script_ratio("Water the field", "hi") == 0.0
    assert script_ratio("anything", "en") == 1.0
    assert is_in_language("मिट्टी का pH 7 है", "hi")  # technical terms may stay in Latin
    assert not is_in_language("Irrigate tomorrow. पानी", "hi")
    assert is_in_language("ಮಣ್ಣು ಪರೀಕ್ಷೆ", "kn") and not is_in_language("ಮಣ್ಣು ಪರೀಕ್ಷೆ", "ta")


def test_advisory_answer_in_wrong_language_is_regenerated():
    replies = [SimpleNamespace(text="Irrigate lightly tomorrow morning."), SimpleNamespace(text="उद्या सकाळी हलके पाणी द्या.")]
    with patch.object(gemini_service, "_call", AsyncMock(side_effect=replies)) as call:
        import asyncio
        text = asyncio.run(gemini_service.generate_advisory("Should I irrigate?", "[DATA]", "mr", "Wheat"))
    assert text == "उद्या सकाळी हलके पाणी द्या."
    assert call.call_count == 2
    assert "Marathi" in call.call_args.kwargs["contents"][-1]


def test_advisory_answer_in_right_language_is_not_regenerated():
    with patch.object(gemini_service, "_call", AsyncMock(return_value=SimpleNamespace(text="பாசனம் செய்யுங்கள்"))) as call:
        import asyncio
        asyncio.run(gemini_service.generate_advisory("water?", "[DATA]", "ta", None))
    assert call.call_count == 1


def test_gemini_speak_requests_audio_in_locale_and_reads_rate(monkeypatch):
    part = SimpleNamespace(inline_data=SimpleNamespace(data=b"\x01\x00", mime_type="audio/L16;codec=pcm;rate=16000"))
    response = SimpleNamespace(candidates=[SimpleNamespace(content=SimpleNamespace(parts=[part]))])
    generate = AsyncMock(return_value=response)
    fake = SimpleNamespace(aio=SimpleNamespace(models=SimpleNamespace(generate_content=generate)))
    monkeypatch.setattr(gemini_service, "client", fake)
    import asyncio
    pcm, rate = asyncio.run(gemini_service.speak("నమస్కారం", "te", "te-IN"))
    assert (pcm, rate) == (b"\x01\x00", 16000)
    config = generate.call_args.kwargs["config"]
    assert config.response_modalities == ["AUDIO"]
    assert config.speech_config.language_code == "te-IN"
    assert generate.call_args.kwargs["model"] == settings.GEMINI_TTS_MODEL


def test_gemini_speak_without_audio_is_unavailable(monkeypatch):
    response = SimpleNamespace(candidates=[SimpleNamespace(content=SimpleNamespace(parts=[SimpleNamespace(inline_data=None)]))])
    fake = SimpleNamespace(aio=SimpleNamespace(models=SimpleNamespace(generate_content=AsyncMock(return_value=response))))
    monkeypatch.setattr(gemini_service, "client", fake)
    import asyncio
    with pytest.raises(ServiceUnavailableException):
        asyncio.run(gemini_service.speak("x", "hi", "hi-IN"))

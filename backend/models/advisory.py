import base64
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from models.diagnosis import MAX_IMAGE_BYTES, Language

MAX_AUDIO_BYTES = 10 * 1024 * 1024


def _decode_limited(v: str, limit: int, label: str) -> str:
    if v.startswith("data:"):
        v = v.split(",", 1)[1] if "," in v else ""
    try:
        decoded = base64.b64decode(v, validate=True)
    except ValueError:
        raise ValueError("Invalid base64 encoding")
    if len(decoded) > limit:
        raise ValueError(f"Decoded {label} size exceeds {limit // (1024 * 1024)}MB")
    return v


class AdvisoryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    crop_type: Optional[str] = Field(None, max_length=40)
    image_base64: Optional[str] = Field(None, max_length=10_000_000)
    language: Language = "en"

    @field_validator("image_base64")
    @classmethod
    def validate_image_base64(cls, v):
        return _decode_limited(v, MAX_IMAGE_BYTES, "image") if v else v


class FollowUpRequest(AdvisoryRequest):
    disease_name: Optional[str] = Field(None, max_length=160)
    severity: Optional[Literal["low", "moderate", "high"]] = None


class DataSourceUse(BaseModel):
    id: str
    status: Literal["used", "unavailable", "not_provided", "none_found"]


class AdvisoryResponse(BaseModel):
    advisory_text: str
    advisory_type: str
    data_sources: List[DataSourceUse] = Field(default_factory=list)
    language: str
    generated_at: str
    recorded: bool = True


class TranscribeRequest(BaseModel):
    audio_base64: str = Field(..., max_length=14_000_000)
    language: Language = "en"

    @field_validator("audio_base64")
    @classmethod
    def validate_audio(cls, v):
        return _decode_limited(v, MAX_AUDIO_BYTES, "audio")


class VoiceAdvisoryRequest(BaseModel):
    audio_base64: str = Field(..., max_length=14_000_000)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    crop_type: Optional[str] = Field(None, max_length=40)
    language: Language = "hi"

    @field_validator("audio_base64")
    @classmethod
    def validate_audio(cls, v):
        return _decode_limited(v, MAX_AUDIO_BYTES, "audio")


class VoiceAdvisoryResponse(BaseModel):
    transcribed_text: str
    advisory: AdvisoryResponse
    audio_response_base64: Optional[str] = None

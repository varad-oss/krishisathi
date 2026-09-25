from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
import base64

class AdvisoryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    crop_type: Optional[str] = None
    image_base64: Optional[str] = Field(None, max_length=10_000_000)
    language: str = 'en'

    @field_validator('image_base64')
    def validate_image_base64(cls, v):
        if not v:
            return v
        try:
            if v.startswith('data:'):
                v = v.split(',', 1)[1]
            decoded = base64.b64decode(v, validate=True)
            if len(decoded) > 5 * 1024 * 1024:
                raise ValueError('Decoded image size exceeds 5MB')
            return v
        except ValueError as e:
            if "exceeds" in str(e):
                raise
            raise ValueError('Invalid base64 encoding')


class AdvisoryResponse(BaseModel):
    advisory_text: str
    advisory_type: str
    data_sources: List[str] = Field(default_factory=list)
    language: str
    translated_text: Optional[str] = None

class VoiceAdvisoryRequest(BaseModel):
    audio_base64: str = Field(..., max_length=10_000_000)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    language: str = 'hi'

    @field_validator('audio_base64')
    def validate_audio_base64(cls, v):
        try:
            if v.startswith('data:'):
                v = v.split(',', 1)[1]
            decoded = base64.b64decode(v, validate=True)
            if len(decoded) > 10 * 1024 * 1024:
                raise ValueError('Decoded audio size exceeds 10MB')
            return v
        except ValueError as e:
            if "exceeds" in str(e):
                raise
            raise ValueError('Invalid base64 encoding')


class VoiceAdvisoryResponse(BaseModel):
    transcribed_text: str
    advisory: AdvisoryResponse
    audio_response_base64: Optional[str] = None

from typing import Optional, List
from pydantic import BaseModel, Field

class AdvisoryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    crop_type: Optional[str] = None
    image_base64: Optional[str] = None
    language: str = 'en'

class AdvisoryResponse(BaseModel):
    advisory_text: str
    advisory_type: str
    data_sources: List[str] = Field(default_factory=list)
    language: str
    translated_text: Optional[str] = None

class VoiceAdvisoryRequest(BaseModel):
    audio_base64: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    language: str = 'hi'

class VoiceAdvisoryResponse(BaseModel):
    transcribed_text: str
    advisory: AdvisoryResponse
    audio_response_base64: Optional[str] = None

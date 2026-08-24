from typing import Optional, List
from pydantic import BaseModel

class AdvisoryRequest(BaseModel):
    query: str
    latitude: float
    longitude: float
    crop_type: Optional[str] = None
    image_base64: Optional[str] = None
    language: str = 'en'

class AdvisoryResponse(BaseModel):
    advisory_text: str
    advisory_type: str
    data_sources: List[str] = []
    language: str
    translated_text: Optional[str] = None

class VoiceAdvisoryRequest(BaseModel):
    audio_base64: str
    latitude: float
    longitude: float
    language: str = 'hi'

class VoiceAdvisoryResponse(BaseModel):
    transcribed_text: str
    advisory: AdvisoryResponse
    audio_response_base64: Optional[str] = None

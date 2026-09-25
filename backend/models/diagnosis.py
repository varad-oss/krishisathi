from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
import base64
from enum import Enum

class SeverityEnum(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"

class SpreadRiskEnum(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"

class TreatmentPlan(BaseModel):
    immediate: List[str] = Field(default_factory=list)
    organic: List[str] = Field(default_factory=list)
    chemical: List[str] = Field(default_factory=list)
    prevention: List[str] = Field(default_factory=list)

class DiagnosisRequest(BaseModel):
    image: str = Field(..., max_length=10_000_000) # base64 str
    crop_type: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    language: str = 'en'

    @field_validator('image')
    def validate_base64_image(cls, v):
        try:
            # Strip standard data URI header if present
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


class DiagnosisResponse(BaseModel):
    disease_name: str = Field(..., min_length=1)
    scientific_name: str
    confidence: float = Field(..., ge=0, le=1)
    severity: SeverityEnum
    affected_part: str
    treatment: TreatmentPlan
    spread_risk: SpreadRiskEnum
    image_analysis_summary: str
    advisory_text: str
    language: str

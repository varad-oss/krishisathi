from typing import Optional, List
from pydantic import BaseModel, Field
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
    image: str # base64 str
    crop_type: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    language: str = 'en'

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

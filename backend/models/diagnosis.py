from typing import Optional, List
from pydantic import BaseModel

class TreatmentPlan(BaseModel):
    immediate: List[str] = []
    organic: List[str] = []
    chemical: List[str] = []
    prevention: List[str] = []

class DiagnosisRequest(BaseModel):
    image: str # base64 str
    crop_type: Optional[str] = None
    latitude: float
    longitude: float
    language: str = 'en'

class DiagnosisResponse(BaseModel):
    disease_name: str
    scientific_name: str
    confidence: float
    severity: str
    affected_part: str
    treatment: TreatmentPlan
    spread_risk: str
    image_analysis_summary: str
    advisory_text: str
    language: str

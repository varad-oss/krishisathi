import base64
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

Language = Literal["en", "hi", "mr", "ta", "te", "bn", "kn", "gu", "pa", "ml"]
DiagnosisStatus = Literal["disease_detected", "healthy", "uncertain", "not_a_plant"]
Level = Literal["low", "moderate", "high"]
Urgency = Literal["routine", "soon", "immediate"]

MAX_IMAGE_BYTES = 5 * 1024 * 1024


def _short(items: list, limit: int = 6, length: int = 300) -> list:
    return [str(i)[:length] for i in items if isinstance(i, str) and i.strip()][:limit]


class TreatmentPlan(BaseModel):
    immediate: List[str] = Field(default_factory=list)
    organic: List[str] = Field(default_factory=list)
    chemical: List[str] = Field(default_factory=list)
    prevention: List[str] = Field(default_factory=list)

    @field_validator("immediate", "organic", "chemical", "prevention", mode="before")
    @classmethod
    def _bound(cls, v):
        return _short(v) if isinstance(v, list) else []


class AIDiagnosis(BaseModel):
    """Shape the vision model must return. Anything else is rejected as an invalid AI response."""
    diagnosis_status: DiagnosisStatus
    image_quality: Literal["good", "poor"]
    certainty: Level
    certainty_reason: str = Field(..., max_length=600)
    disease_name: Optional[str] = Field(None, max_length=160)
    disease_name_en: Optional[str] = Field(None, max_length=160)
    scientific_name: Optional[str] = Field(None, max_length=160)
    reference_id: Optional[str] = Field(None, max_length=80)
    affected_part: Optional[str] = Field(None, max_length=120)
    observed_symptoms: List[str] = Field(default_factory=list)
    alternative_causes: List[str] = Field(default_factory=list)
    severity: Optional[Level] = None
    spread_risk: Optional[Level] = None
    urgency: Urgency = "routine"
    treatment: TreatmentPlan = Field(default_factory=TreatmentPlan)
    summary: str = Field("", max_length=1500)

    @field_validator("observed_symptoms", "alternative_causes", mode="before")
    @classmethod
    def _bound(cls, v):
        return _short(v) if isinstance(v, list) else []


class ReferenceSource(BaseModel):
    organization: str
    title: str
    url: Optional[str] = None


class DiseaseReference(BaseModel):
    """Curated, human-verified reference entry (English), shown separately from AI text."""
    id: str
    name: str
    scientific_name: Optional[str] = None
    symptoms: str
    treatment: str
    sources: List[ReferenceSource]


class DiagnosisResponse(BaseModel):
    status: DiagnosisStatus
    certainty: Level
    certainty_reason: str
    image_quality: Literal["good", "poor"]
    disease_name: Optional[str] = None
    scientific_name: Optional[str] = None
    affected_part: Optional[str] = None
    observed_symptoms: List[str]
    alternative_causes: List[str]
    severity: Optional[Level] = None
    spread_risk: Optional[Level] = None
    urgency: Urgency
    treatment: TreatmentPlan
    summary: str
    reference: Optional[DiseaseReference] = None
    context_used: dict
    recorded: bool
    language: Language
    generated_by: dict


class DiagnosisRequest(BaseModel):
    image: str = Field(..., max_length=10_000_000)  # base64 str
    crop_type: Optional[str] = Field(None, max_length=40)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    language: Language = "en"

    @field_validator("image")
    @classmethod
    def validate_base64_image(cls, v):
        if v.startswith("data:"):
            v = v.split(",", 1)[1] if "," in v else ""
        try:
            decoded = base64.b64decode(v, validate=True)
        except ValueError:
            raise ValueError("Invalid base64 encoding")
        if len(decoded) > MAX_IMAGE_BYTES:
            raise ValueError("Decoded image size exceeds 5MB")
        return v

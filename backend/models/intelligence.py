"""Farm intelligence contract: the fused view of one farm that GET /api/farm/intelligence returns.

The API emits stable ids (risk category, driver, action, evidence id) plus numbers; the frontend renders
them in the farmer's language, so no English prose is generated here and nothing is AI-written.
"""
from datetime import date
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

Severity = Literal["low", "moderate", "high", "unavailable"]
Confidence = Literal["low", "moderate", "high"]
# What kind of statement a piece of evidence is. Never collapse these: a forecast is not an observation.
Basis = Literal[
    "observed", "forecast", "model_estimate", "satellite_observation", "rule_based",
    "ai_generated", "ai_classified_reports", "farmer_reported", "static_reference",
]
RiskCategory = Literal[
    "waterlogging", "water_stress", "heat_stress", "cold_stress", "disease", "pest",
    "spray_window", "harvest_weather", "crop_health",
]
SourceStatus = Literal["available", "unavailable", "not_configured", "no_data", "insufficient_data", "not_provided", "pending"]
# How a piece of evidence bears on a risk's stated level (see services/risk_engine.py, "Evidence confidence"):
# required   - a condition the stated risk level depends on; confidence is the weakest required item
# supporting - an alternative or corroborating signal; confidence is the strongest one
# context    - shown for transparency, does not raise the risk (stale, distant, low-certainty or background data)
EvidenceRole = Literal["required", "supporting", "context"]


class Evidence(BaseModel):
    id: str                               # e.g. "rain_forecast", "soil_water_status", "ndvi_change"
    value: Optional[float | str] = None
    unit: Optional[str] = None
    date: Optional[str] = None            # the day a forecast/observation refers to
    basis: Basis
    source: str                           # source id: weather | soil | soil_water | satellite | crop_stage | outbreaks | farm_history
    params: dict[str, Any] = Field(default_factory=dict)
    role: EvidenceRole = "supporting"
    group: Optional[str] = None           # independence group: evidence in one group shares an upstream source
    reliability: Optional[Confidence] = None


class RuleRef(BaseModel):
    id: str
    source: str
    url: Optional[str] = None


class Risk(BaseModel):
    """`severity` is the risk level: how concerning the condition would be if the signals are right.
    `confidence` is evidence confidence: how strong and reliable those signals are. They are independent axes."""
    category: RiskCategory
    severity: Severity
    confidence: Optional[Confidence] = None
    confidence_basis: list[str] = Field(default_factory=list)  # ids explaining the confidence level
    independent_sources: int = 0                                # distinct independence groups among non-context evidence
    drivers: list[str] = Field(default_factory=list)   # why this severity, as ids the UI can explain
    evidence: list[Evidence] = Field(default_factory=list)
    action: Optional[str] = None                       # recommended action id, None when nothing to do
    reason: Optional[str] = None                       # why the risk is unavailable / not assessed
    date: Optional[str] = None                         # soonest day the risk applies to
    crop: Optional[str] = None
    crop_stage: Optional[str] = None
    rules: list[RuleRef] = Field(default_factory=list)


class TopAction(BaseModel):
    status: Literal["action", "routine", "unavailable"]
    action: Optional[str] = None
    category: Optional[RiskCategory] = None
    severity: Optional[Severity] = None
    confidence: Optional[Confidence] = None
    confidence_basis: list[str] = Field(default_factory=list)
    drivers: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    rules: list[RuleRef] = Field(default_factory=list)
    date: Optional[str] = None
    reason: Optional[str] = None
    # Why this comes first: highest_severity | soonest | stronger_evidence | less_reversible | only_action
    priority_reason: Optional[str] = None


class DataQuality(BaseModel):
    source: str
    status: SourceStatus
    kind: str
    as_of: Optional[str] = None           # when the data was valid / retrieved / sensed
    reason: Optional[str] = None
    provider: Optional[str] = None


class FarmInput(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    crop: Optional[str] = None
    sowing_date: Optional[date] = None


class FarmIntelligence(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    generated_at: str
    farm: dict[str, Any]                  # crop, rounded location, crop stage estimate
    top_action: TopAction
    risks: list[Risk]
    weather: Optional[dict[str, Any]] = None
    soil: Optional[dict[str, Any]] = None
    soil_water: Optional[dict[str, Any]] = None
    crop_health: Optional[dict[str, Any]] = None
    nearby_outbreaks: Optional[list[dict[str, Any]]] = None
    data_quality: list[DataQuality]
    engine: dict[str, Any]                # engine id/version, rule references

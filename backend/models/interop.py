"""
Interoperability data models for cross-state agricultural data sharing.

These schemas define the standard payload format that any Indian state's
agricultural system can use to POST signals to the shared endpoint or
GET aggregated views. This is the core "Digital Public Good" data contract.
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class SignalType(str, Enum):
    DISEASE_ALERT = "disease_alert"
    PEST_ADVISORY = "pest_advisory"
    WEATHER_ADVISORY = "weather_advisory"
    BEST_PRACTICE = "best_practice"
    YIELD_REPORT = "yield_report"
    SOIL_HEALTH = "soil_health"


class SeverityLevel(str, Enum):
    INFO = "info"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class RegionalAgriSignal(BaseModel):
    """
    Standard payload for cross-state agricultural data exchange.
    Any state system can POST this to the shared endpoint.

    Raw farmer-level data is NEVER included — only aggregated,
    anonymized signals flow through this schema.
    """
    signal_id: Optional[str] = Field(None, description="Auto-generated if not provided")
    from_state: str = Field(..., description="ISO-style state code (e.g., 'MH', 'PB')", pattern=r"^[A-Z]{2}$")
    to_state: Optional[str] = Field(None, description="Target state code, or null for broadcast", pattern=r"^[A-Z]{2}$")
    signal_type: SignalType
    severity: SeverityLevel
    message: str = Field(..., description="Human-readable signal description", max_length=1000)
    disease_name: Optional[str] = Field(None, max_length=200)
    affected_crop: Optional[str] = Field(None, max_length=200)
    affected_district: Optional[str] = Field(None, max_length=200)
    affected_area_km2: Optional[float] = Field(None, ge=0)
    report_count: Optional[int] = Field(None, ge=0, description="Number of aggregated farmer reports")
    ndvi_trend: Optional[float] = Field(None, ge=-1, le=1, description="NDVI change over last 2 weeks (-1.0 to 1.0)")
    soil_health_index: Optional[float] = Field(None, ge=0, le=100, description="Composite soil health score (0-100)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict] = Field(None, description="Additional key-value metadata")

    model_config = ConfigDict(json_schema_extra={
            "example": {
                "from_state": "MH",
                "to_state": "KA",
                "signal_type": "disease_alert",
                "severity": "high",
                "message": "Fall Armyworm migration detected in Vidarbha — early warning for northern Karnataka maize",
                "disease_name": "Fall Armyworm",
                "affected_crop": "Maize",
                "affected_district": "Nagpur",
                "affected_area_km2": 450.0,
                "report_count": 89,
                "ndvi_trend": -0.12
            }
    })


class StateConfig(BaseModel):
    """
    Per-state configuration that adapts KrishiSathi to local context.
    The same backend code serves multiple states by swapping this config.
    """
    code: str = Field(..., description="2-letter state code")
    name: str
    lat: float = Field(..., description="Reference point used for indicative state-level forecasts")
    lng: float
    default_language: str
    primary_crops: List[str]


class AggregatedStateReport(BaseModel):
    """National-level aggregation of state signals — for the policymaker dashboard."""
    total_signals: int
    states_reporting: int
    critical_alerts: int
    disease_signals: int
    pest_signals: int
    weather_signals: int
    signals: List[RegionalAgriSignal]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    note: str = "All data is aggregated and anonymized. Raw farmer records remain within each state's deployment."


def strip_pii(data: dict) -> dict:
    """
    Strip any personally identifiable information before data flows
    from a state-level deployment to the national aggregator.

    This is the privacy boundary: raw farmer names, phone numbers,
    exact GPS coordinates of individual farms, etc. are removed.
    Only aggregated, district-level data passes through.
    """
    pii_fields = [
        "farmer_name", "farmer_id", "phone_number", "phone",
        "email", "aadhaar", "address", "exact_location",
        "farm_gps_lat", "farm_gps_lng", "farmer_photo",
        "device_id", "ip_address", "notes", "village"
    ]
    cleaned = {}
    for key, value in data.items():
        if key.lower() in pii_fields:
            continue  # Strip PII field entirely
        if isinstance(value, dict):
            cleaned[key] = strip_pii(value)
        elif isinstance(value, list):
            cleaned[key] = [
                strip_pii(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            cleaned[key] = value
    return cleaned

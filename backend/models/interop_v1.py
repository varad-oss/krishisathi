"""Country-neutral interoperability schemas, version 1.0.

Any national system (India first; other BRICS members through their own adapter) exchanges agricultural
signals in these shapes. Rules:

* codes, not names, carry meaning: ISO 3166-1 alpha-2 countries, ISO 3166-2 regions, stable crop and disease codes;
* every value states what kind of statement it is (`provenance.kind`) and where it came from;
* public signals are aggregates: coarse grid cells or regions, report counts, never a farm, farmer or exact point.
Farm-level shapes (FarmV1, PlotV1, FarmerRefV1) exist for exchange inside one country's deployment only and are
never served by the public signal API.
"""
from datetime import date, datetime
from typing import Any, Generic, Literal, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "1.0"

CountryCode = str  # ISO 3166-1 alpha-2, validated with a pattern where used
ProvenanceKind = Literal[
    "observed", "forecast", "model_estimate", "satellite_observation", "rule_based", "ai_generated",
    "ai_classified_reports", "farmer_reported", "official_statistic", "curated_reference", "authenticated_submission",
]
Level = Literal["low", "moderate", "high"]


class _V1(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProvenanceV1(_V1):
    source: str = Field(..., max_length=200)
    kind: ProvenanceKind
    method: Optional[str] = Field(None, max_length=500)
    url: Optional[str] = Field(None, max_length=500)
    retrieved_at: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)


class GridCellV1(_V1):
    """South-west corner and size of a regular lat/lng cell; the finest geography a public signal carries."""
    cell_deg: float = Field(..., gt=0, le=10)
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class GeoRefV1(_V1):
    country_code: CountryCode = Field(..., pattern=r"^[A-Z]{2}$")
    region_code: Optional[str] = Field(None, pattern=r"^[A-Z]{2}-[A-Z0-9]{1,3}$", description="ISO 3166-2")
    grid: Optional[GridCellV1] = None
    basis: Literal["region", "grid_cell", "region_reference_point"] = "region"


class CropV1(_V1):
    schema_version: Literal["1.0"] = SCHEMA_VERSION
    crop_code: str = Field(..., pattern=r"^[a-z0-9_]{2,40}$")
    name_en: str
    group: Optional[str] = None
    aliases: list[str] = Field(default_factory=list)


class ReferenceSourceV1(_V1):
    organization: str
    title: str
    url: Optional[str] = None


class DiseaseV1(_V1):
    schema_version: Literal["1.0"] = SCHEMA_VERSION
    disease_code: str = Field(..., pattern=r"^[a-z0-9_-]{2,80}$")
    name_en: str
    scientific_name: Optional[str] = None
    crop_codes: list[str]
    references: list[ReferenceSourceV1]
    provenance: ProvenanceV1


class PeriodV1(_V1):
    start: date
    end: date


class ObservationV1(_V1):
    """One aggregated observation, e.g. the number of AI-classified disease detections in a grid cell and period."""
    schema_version: Literal["1.0"] = SCHEMA_VERSION
    # production_statistic: official crop area / production / yield totals (added for Brazil's IBGE PAM; additive, v1.0)
    observation_type: Literal["disease_observation", "weather_observation", "soil_observation", "crop_health_observation",
                              "production_statistic"]
    geo: GeoRefV1
    period: PeriodV1
    crop_code: Optional[str] = None
    crop_stage: Optional[str] = None
    subject: Optional[str] = Field(None, description="e.g. disease_code for disease observations")
    variable: str
    value: float | int | str
    unit: str
    sample_size: Optional[int] = Field(None, ge=0)
    confidence: Optional[Level] = None
    provenance: ProvenanceV1


class RiskSignalV1(_V1):
    """A risk or early-warning signal. `source_region` is where the evidence is; `affected_region` is only set when a
    publisher names one. A signal never asserts that a pest or pathogen moved between regions."""
    schema_version: Literal["1.0"] = SCHEMA_VERSION
    signal_id: str
    signal_type: Literal["weather_risk", "disease_cluster", "disease_alert", "pest_advisory", "weather_advisory", "best_practice",
                         "yield_report", "soil_health"]
    category: Optional[str] = None
    severity: Level
    geo: GeoRefV1
    source_region: Optional[str] = None
    affected_region: Optional[str] = None
    crop_codes: list[str] = Field(default_factory=list)
    disease: Optional[str] = None
    report_count: Optional[int] = Field(None, ge=0)
    period: PeriodV1
    issued_at: datetime
    confidence: Level
    provenance: ProvenanceV1


class AdvisoryV1(_V1):
    schema_version: Literal["1.0"] = SCHEMA_VERSION
    action_code: str
    category: Optional[str] = None
    severity: Optional[Level] = None
    crop_code: Optional[str] = None
    geo: GeoRefV1
    issued_at: datetime
    provenance: ProvenanceV1


class OutcomeSummaryV1(_V1):
    """Self-reported follow-through and outcomes, aggregated; small groups are suppressed by the publisher."""
    schema_version: Literal["1.0"] = SCHEMA_VERSION
    action_code: Optional[str] = None
    crop_code: Optional[str] = None
    geo: GeoRefV1
    period: PeriodV1
    recommendations: int = Field(..., ge=0)
    followed: dict[str, int]
    outcomes: dict[str, int]
    provenance: ProvenanceV1


class FarmerRefV1(_V1):
    """Pseudonymous reference only; names, phone numbers and identity documents never enter the schema."""
    farmer_ref: str = Field(..., max_length=64)
    country_code: CountryCode = Field(..., pattern=r"^[A-Z]{2}$")


class PlotV1(_V1):
    plot_ref: str = Field(..., max_length=64)
    area_ha: Optional[float] = Field(None, gt=0)
    crop_code: Optional[str] = None
    sowing_date: Optional[date] = None


class FarmV1(_V1):
    """In-country exchange only (e.g. between a national registry and an advisory service)."""
    schema_version: Literal["1.0"] = SCHEMA_VERSION
    farm_ref: str = Field(..., max_length=64)
    farmer: Optional[FarmerRefV1] = None
    geo: GeoRefV1
    plots: list[PlotV1] = Field(default_factory=list)


class PrivacyV1(_V1):
    aggregation: str
    minimum_group_size: int
    spatial_resolution: str
    personal_data: Literal["none"] = "none"


T = TypeVar("T")


class PageV1(BaseModel, Generic[T]):
    schema_version: Literal["1.0"] = SCHEMA_VERSION
    country_code: str
    # "unsupported": the country has no real source for this category, so `items` is empty by definition, not by result.
    status: Literal["available", "unsupported"] = "available"
    generated_at: datetime
    count: int
    next_cursor: Optional[str] = None
    items: list[T]
    privacy: Optional[PrivacyV1] = None
    notes: Optional[str] = None


SCHEMAS: dict[str, type[BaseModel]] = {
    "Crop": CropV1, "Disease": DiseaseV1, "Observation": ObservationV1, "RiskSignal": RiskSignalV1,
    "Advisory": AdvisoryV1, "OutcomeSummary": OutcomeSummaryV1, "Farm": FarmV1, "Plot": PlotV1, "FarmerRef": FarmerRefV1,
    "Provenance": ProvenanceV1, "GeoRef": GeoRefV1,
}


def json_schemas() -> dict[str, Any]:
    return {name: model.model_json_schema() for name, model in SCHEMAS.items()}

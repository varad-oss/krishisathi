from datetime import datetime
from typing import List

from pydantic import BaseModel


class DiseaseAlert(BaseModel):
    alert_id: str
    disease_name: str
    region: str
    severity: str
    alert_radius_km: float  # clustering radius, not a measured affected area
    timestamp: datetime
    farmer_reports_count: int


class OutbreakReport(BaseModel):
    location: str
    disease_reports: List[str]
    cluster_center: dict  # {"lat": float, "lng": float}, rounded to ~11 km
    radius_km: float

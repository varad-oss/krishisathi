from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class DiseaseAlert(BaseModel):
    alert_id: str
    disease_name: str
    region: str
    severity: str
    affected_area_km2: float
    timestamp: datetime
    farmer_reports_count: int
    recommendation: str

class OutbreakReport(BaseModel):
    location: str
    disease_reports: List[str]
    cluster_center: dict # {"lat": float, "lng": float}
    radius_km: float

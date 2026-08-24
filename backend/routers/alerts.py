from fastapi import APIRouter
from typing import List
from models.alert import DiseaseAlert, OutbreakReport
from datetime import datetime

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

MOCK_ALERTS = [
    DiseaseAlert(
        alert_id="ALT-001",
        disease_name="Fall Armyworm",
        region="Pune, Maharashtra",
        severity="High",
        affected_area_km2=250.5,
        timestamp=datetime.utcnow(),
        farmer_reports_count=120,
        recommendation="Apply recommended insecticides. Deploy pheromone traps."
    ),
    DiseaseAlert(
        alert_id="ALT-002",
        disease_name="Wheat Rust",
        region="Ludhiana, Punjab",
        severity="Medium",
        affected_area_km2=50.0,
        timestamp=datetime.utcnow(),
        farmer_reports_count=45,
        recommendation="Use rust-resistant varieties next season. Apply fungicides if severe."
    )
]

MOCK_OUTBREAKS = [
    OutbreakReport(
        location="Pune, Maharashtra",
        disease_reports=["Fall Armyworm", "Leaf Blight"],
        cluster_center={"lat": 18.5204, "lng": 73.8567},
        radius_km=15.0
    )
]

@router.get("", response_model=List[DiseaseAlert])
async def get_alerts(region: str = None):
    alerts_copy = [DiseaseAlert(**a.model_dump()) for a in MOCK_ALERTS]
    for a in alerts_copy:
        a.timestamp = datetime.utcnow()
    
    if region:
        return [a for a in alerts_copy if region.lower() in a.region.lower()]
    return alerts_copy

@router.get("/outbreaks")
async def get_outbreaks():
    return [OutbreakReport(**o.model_dump()) for o in MOCK_OUTBREAKS]

@router.post("/report")
async def report_disease(disease: str, lat: float, lng: float):
    # In a real app, this would save to Firestore/BigQuery
    return {"status": "success", "message": "Report logged successfully"}

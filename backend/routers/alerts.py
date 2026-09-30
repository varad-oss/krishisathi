from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query

from models.alert import DiseaseAlert, OutbreakReport
from services.persistence_service import nearby_outbreaks, persistence_service

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

OUTBREAK_SOURCE = {
    "source": "KrishiSathi community reports",
    "kind": "ai_classified_user_reports",
    "notes": "Clusters of at least 3 AI-classified photo diagnoses of the same disease within 50 km in 7 days. Not laboratory-confirmed.",
}


@router.get("", response_model=List[DiseaseAlert])
async def get_alerts(region: Optional[str] = Query(None, max_length=100)):
    alerts = [
        DiseaseAlert(
            alert_id=o["id"],
            disease_name=o["disease"],
            region=o["location"],
            severity=o["severity"],
            alert_radius_km=o["radius_km"],
            timestamp=datetime.fromisoformat(o["timestamp"]),
            farmer_reports_count=o["report_count"],
        )
        for o in await persistence_service.get_outbreaks()
    ]
    if region:
        return [a for a in alerts if region.lower() in a.region.lower()]
    return alerts


@router.get("/outbreaks")
async def get_outbreaks():
    return [
        OutbreakReport(
            location=o["location"],
            disease_reports=[o["disease"]],
            cluster_center={"lat": o["lat"], "lng": o["lng"]},
            radius_km=o["radius_km"],
        )
        for o in await persistence_service.get_outbreaks()
    ]


@router.get("/personalized")
async def get_personalized_alerts(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    crop_type: Optional[str] = Query(None, max_length=40),
):
    alerts = nearby_outbreaks(await persistence_service.get_outbreaks(), lat, lng, crop_type)
    return {"alerts": alerts, "provenance": OUTBREAK_SOURCE}

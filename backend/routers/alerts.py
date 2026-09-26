import math
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query

from models.alert import DiseaseAlert, OutbreakReport
from services.persistence_service import persistence_service

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

OUTBREAK_SOURCE = {
    "source": "KrishiSathi community reports",
    "kind": "ai_classified_user_reports",
    "notes": "Clusters of at least 3 AI-classified photo diagnoses of the same disease within 50 km in 7 days. Not laboratory-confirmed.",
}


def _haversine(lat1, lon1, lat2, lon2):
    r = 6371.0
    d_lat, d_lon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


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
    alerts = []
    for outbreak in await persistence_service.get_outbreaks():
        dist = _haversine(lat, lng, outbreak["lat"], outbreak["lng"])
        if dist > outbreak["radius_km"] * 1.5:  # 50% margin for "nearby"
            continue
        targets = outbreak["crop_targets"]
        if crop_type and targets and not any(t.lower() in crop_type.lower() or crop_type.lower() in t.lower() for t in targets):
            continue
        alerts.append({
            "id": outbreak["id"],
            "disease": outbreak["disease"],
            "distance_km": round(dist),
            "location": outbreak["location"],
            "severity": outbreak["severity"],
            "report_count": outbreak["report_count"],
            "crop_targets": targets,
            "last_report_at": outbreak["timestamp"],
        })
    return {"alerts": alerts, "provenance": OUTBREAK_SOURCE}

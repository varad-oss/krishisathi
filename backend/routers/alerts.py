from fastapi import APIRouter
from typing import List, Optional
from models.alert import DiseaseAlert, OutbreakReport
from services.persistence_service import persistence_service
from datetime import datetime
import math

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

def _haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon / 2) * math.sin(dLon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@router.get("", response_model=List[DiseaseAlert])
async def get_alerts(region: str = None):
    # Retrieve outbreaks from database and map to alerts
    outbreaks = [o for o in await persistence_service.get_outbreaks() if o['status'] == 'active']
    alerts = []
    for o in outbreaks:
        # Convert OutbreakRecord dict to DiseaseAlert mock format
        alerts.append(DiseaseAlert(
            alert_id=o['id'],
            disease_name=o['disease'],
            region=o['location'],
            severity=o['severity'].capitalize(),
            affected_area_km2=o['radius_km'] * o['radius_km'] * 3.14159,
            timestamp=datetime.fromisoformat(o['timestamp']),
            farmer_reports_count=o['report_count'],
            recommendation="Please refer to advisory for specific treatments."
        ))
        
    if region:
        return [a for a in alerts if region.lower() in a.region.lower()]
    return alerts

@router.get("/outbreaks")
async def get_outbreaks():
    outbreaks = [o for o in await persistence_service.get_outbreaks() if o['status'] == 'active']
    return [
        OutbreakReport(
            location=o["location"],
            disease_reports=[o["disease"]],
            cluster_center={"lat": o["lat"], "lng": o["lng"]},
            radius_km=o["radius_km"]
        ) for o in outbreaks
    ]

@router.get("/personalized")
async def get_personalized_alerts(lat: float, lng: float, crop_type: Optional[str] = None):
    outbreaks = [o for o in await persistence_service.get_outbreaks() if o['status'] == 'active']
    personalized_alerts = []
    
    for outbreak in outbreaks:
        dist = _haversine(lat, lng, outbreak["lat"], outbreak["lng"])
        if dist <= outbreak["radius_km"] * 1.5:  # Add 50% margin for "nearby" alerts
            is_relevant_crop = False
            if crop_type and outbreak["crop_targets"]:
                for target in outbreak["crop_targets"]:
                    if target.lower() in crop_type.lower() or crop_type.lower() in target.lower():
                        is_relevant_crop = True
                        break
            else:
                is_relevant_crop = True
                
            if is_relevant_crop:
                personalized_alerts.append({
                    "disease": outbreak["disease"],
                    "distance_km": round(dist, 1),
                    "location": outbreak["location"],
                    "severity": outbreak["severity"],
                    "message": f"{outbreak['severity']} risk of {outbreak['disease']} detected {round(dist, 1)}km away in {outbreak['location']}."
                })
                
    return {"alerts": personalized_alerts}

@router.post("/report")
async def report_disease(disease: str, lat: float, lng: float):
    from fastapi import HTTPException
    raise HTTPException(status_code=501, detail="Feature not implemented yet.")

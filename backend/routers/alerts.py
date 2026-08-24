from fastapi import APIRouter
from typing import List, Optional
from models.alert import DiseaseAlert, OutbreakReport
from datetime import datetime
import math

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
    ),
    DiseaseAlert(
        alert_id="ALT-003",
        disease_name="Late Blight",
        region="Nashik, Maharashtra",
        severity="High",
        affected_area_km2=120.0,
        timestamp=datetime.utcnow(),
        farmer_reports_count=85,
        recommendation="Spray protectant fungicides immediately."
    )
]

# Adding explicit lat/lng to outbreaks for distance calculation
MOCK_OUTBREAKS = [
    {
        "location": "Pune, Maharashtra",
        "disease": "Fall Armyworm",
        "crop_targets": ["Maize", "Corn", "Sorghum"],
        "lat": 18.5204,
        "lng": 73.8567,
        "radius_km": 50.0,
        "severity": "high"
    },
    {
        "location": "Ludhiana, Punjab",
        "disease": "Wheat Rust",
        "crop_targets": ["Wheat"],
        "lat": 30.9010,
        "lng": 75.8573,
        "radius_km": 100.0,
        "severity": "high"
    },
    {
        "location": "Nashik, Maharashtra",
        "disease": "Late Blight",
        "crop_targets": ["Tomato", "Potato"],
        "lat": 20.0110,
        "lng": 73.7909,
        "radius_km": 40.0,
        "severity": "critical"
    }
]

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
    alerts_copy = [DiseaseAlert(**a.model_dump()) for a in MOCK_ALERTS]
    for a in alerts_copy:
        a.timestamp = datetime.utcnow()
    
    if region:
        return [a for a in alerts_copy if region.lower() in a.region.lower()]
    return alerts_copy

@router.get("/outbreaks")
async def get_outbreaks():
    # Keep legacy format for other consumers
    return [
        OutbreakReport(
            location=o["location"],
            disease_reports=[o["disease"]],
            cluster_center={"lat": o["lat"], "lng": o["lng"]},
            radius_km=o["radius_km"]
        ) for o in MOCK_OUTBREAKS
    ]

@router.get("/personalized")
async def get_personalized_alerts(lat: float, lng: float, crop_type: Optional[str] = None):
    """
    Returns hyper-local alerts relevant to the farmer's location and specific crop.
    """
    personalized_alerts = []
    
    for outbreak in MOCK_OUTBREAKS:
        # Check distance
        dist = _haversine(lat, lng, outbreak["lat"], outbreak["lng"])
        
        # We alert if they are within 150km (regional threat)
        if dist <= 150.0:
            # Check crop relevance if crop_type is provided
            is_relevant_crop = False
            if crop_type:
                for target in outbreak["crop_targets"]:
                    if target.lower() in crop_type.lower() or crop_type.lower() in target.lower():
                        is_relevant_crop = True
                        break
            else:
                # If no crop specified, show regional threats anyway
                is_relevant_crop = True
                
            if is_relevant_crop:
                personalized_alerts.append({
                    "disease": outbreak["disease"],
                    "distance_km": round(dist, 1),
                    "location": outbreak["location"],
                    "severity": outbreak["severity"],
                    "message": f"High risk of {outbreak['disease']} detected {round(dist, 1)}km away in {outbreak['location']}."
                })
                
    return {"alerts": personalized_alerts}

@router.post("/report")
async def report_disease(disease: str, lat: float, lng: float):
    return {"status": "success", "message": "Report logged successfully"}

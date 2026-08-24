from fastapi import APIRouter
from services.gemini_service import gemini_service
from datetime import datetime, timedelta
import random

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

# Rich realistic mock data for policymaker dashboard
MOCK_STATS = {
    "total_diagnoses": 15420,
    "diagnoses_trend": 12.5,  # % increase this week
    "active_outbreaks": 7,
    "outbreaks_trend": -2,  # decreased by 2
    "farmers_reached": 48350,
    "farmers_trend": 18.3,
    "languages_served": 10,
    "states_active": 8,
    "top_diseases": [
        {"name": "Fall Armyworm", "count": 3240, "severity": "high"},
        {"name": "Leaf Rust", "count": 2180, "severity": "high"},
        {"name": "Early Blight", "count": 1950, "severity": "moderate"},
        {"name": "Bacterial Leaf Blight", "count": 1420, "severity": "moderate"},
        {"name": "Powdery Mildew", "count": 890, "severity": "low"},
    ],
    "diagnoses_by_crop": [
        {"crop": "Wheat", "count": 4520},
        {"crop": "Rice", "count": 3890},
        {"crop": "Tomato", "count": 2340},
        {"crop": "Cotton", "count": 1980},
        {"crop": "Corn", "count": 1450},
        {"crop": "Potato", "count": 1240},
    ],
    "diagnoses_by_state": [
        {"state": "Uttar Pradesh", "code": "UP", "count": 8940},
        {"state": "Maharashtra", "code": "MH", "count": 7850},
        {"state": "Punjab", "code": "PB", "count": 5140},
        {"state": "Karnataka", "code": "KA", "count": 4980},
        {"state": "Madhya Pradesh", "code": "MP", "count": 3890},
        {"state": "Tamil Nadu", "code": "TN", "count": 3560},
        {"state": "Gujarat", "code": "GJ", "count": 2450},
        {"state": "West Bengal", "code": "WB", "count": 2210},
    ],
}


@router.get("/stats")
async def get_stats():
    return MOCK_STATS


@router.get("/report")
async def get_dashboard_report(language: str = 'en'):
    report_data = {
        "stats": MOCK_STATS,
        "period": "August 14-21, 2026",
        "focus_areas": [
            "Fall Armyworm surge in Maharashtra and Karnataka",
            "Wheat Rust early detection across Punjab",
            "Cross-state advisory sharing with Gujarat on soybean diseases",
        ],
    }
    report_text = gemini_service.generate_dashboard_report(report_data, language)
    return {
        "report_text": report_text,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "period": "August 14-21, 2026",
    }


@router.get("/outbreaks")
async def get_dashboard_outbreaks():
    return [
        {
            "id": "OB-2026-001",
            "disease": "Late Blight",
            "region": "Pune, MH",
            "country": "IN",
            "severity": "critical",
            "reports_count": 342,
            "affected_area_km2": 1200,
            "lat": 18.52,
            "lng": 73.86,
            "first_reported": "2026-08-15T08:30:00Z",
        },
        {
            "id": "OB-2026-002",
            "disease": "Wheat Rust",
            "region": "Ludhiana, PB",
            "country": "IN",
            "severity": "severe",
            "reports_count": 189,
            "affected_area_km2": 800,
            "lat": 30.90,
            "lng": 75.86,
            "first_reported": "2026-08-16T08:30:00Z",
        },
        {
            "id": "OB-2026-003",
            "disease": "Fall Armyworm",
            "region": "Belgaum, KA",
            "country": "IN",
            "severity": "moderate",
            "reports_count": 156,
            "affected_area_km2": 650,
            "lat": 15.85,
            "lng": 74.50,
            "first_reported": "2026-08-17T08:30:00Z",
        },
        {
            "id": "OB-2026-004",
            "disease": "Rice Blast",
            "region": "Thanjavur, TN",
            "country": "IN",
            "severity": "moderate",
            "reports_count": 98,
            "affected_area_km2": 420,
            "lat": 10.79,
            "lng": 79.14,
            "first_reported": "2026-08-18T08:30:00Z",
        },
        {
            "id": "OB-2026-005",
            "disease": "Yellow Mosaic",
            "region": "Indore, MP",
            "country": "IN",
            "severity": "severe",
            "reports_count": 134,
            "affected_area_km2": 550,
            "lat": 22.72,
            "lng": 75.86,
            "first_reported": "2026-08-19T08:30:00Z",
        },
        {
            "id": "OB-2026-006",
            "disease": "Powdery Mildew",
            "region": "Junagadh, GJ",
            "country": "IN",
            "severity": "low",
            "reports_count": 67,
            "affected_area_km2": 280,
            "lat": 21.52,
            "lng": 70.46,
            "first_reported": "2026-08-20T08:30:00Z",
        },
        {
            "id": "OB-2026-007",
            "disease": "Bacterial Leaf Blight",
            "region": "Burdwan, WB",
            "country": "IN",
            "severity": "moderate",
            "reports_count": 112,
            "affected_area_km2": 380,
            "lat": 23.23,
            "lng": 87.86,
            "first_reported": "2026-08-21T08:30:00Z",
        },
    ]


@router.get("/crop-health")
async def get_crop_health():
    return {
        "overall_index": 74.2,
        "measurement_date": "2026-08-20",
        "regions": [
            {"name": "Punjab", "ndvi": 0.72},
            {"name": "Maharashtra", "ndvi": 0.58},
            {"name": "Karnataka", "ndvi": 0.65},
            {"name": "Tamil Nadu", "ndvi": 0.71},
            {"name": "Uttar Pradesh", "ndvi": 0.45},
            {"name": "Madhya Pradesh", "ndvi": 0.62},
            {"name": "Gujarat", "ndvi": 0.68},
            {"name": "West Bengal", "ndvi": 0.55},
        ],
    }


@router.get("/activity")
async def get_recent_activity():
    """Recent farmer activity feed for the dashboard."""
    activities = [
        {"time": "2 min ago", "type": "diagnosis", "text": "Farmer in Pune, Maharashtra diagnosed Late Blight on Tomato (94% confidence)", "severity": "high"},
        {"time": "8 min ago", "type": "alert", "text": "⚠️ Outbreak alert triggered for Wheat Rust in Ludhiana, Punjab — 23 reports in 48 hours", "severity": "critical"},
        {"time": "15 min ago", "type": "diagnosis", "text": "Farmer in Nashik, Maharashtra diagnosed Early Blight on Tomato (87% confidence)", "severity": "moderate"},
        {"time": "22 min ago", "type": "advisory", "text": "Voice advisory served in Tamil to farmer in Coimbatore — wheat sowing schedule query", "severity": "info"},
        {"time": "35 min ago", "type": "diagnosis", "text": "Farmer in Indore, Madhya Pradesh diagnosed Yellow Mosaic (91% confidence)", "severity": "high"},
        {"time": "1 hour ago", "type": "alert", "text": "Disease cluster detected in Vidarbha region — Cotton Bollworm reports increasing", "severity": "high"},
        {"time": "1.5 hours ago", "type": "exchange", "text": "🤝 Cross-state data exchange: Maharashtra shared Fall Armyworm patterns with Karnataka", "severity": "info"},
        {"time": "2 hours ago", "type": "advisory", "text": "Advisory served in Hindi to 45 farmers in UP — monsoon crop management", "severity": "info"},
        {"time": "3 hours ago", "type": "diagnosis", "text": "Farmer in Burdwan, West Bengal diagnosed Bacterial Leaf Blight (78% confidence)", "severity": "moderate"},
        {"time": "4 hours ago", "type": "advisory", "text": "Voice advisory served in Marathi — organic pest control for cotton", "severity": "info"},
    ]
    return activities

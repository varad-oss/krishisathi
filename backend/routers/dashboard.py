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
    "countries_active": 5,
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
    "diagnoses_by_country": [
        {"country": "India", "code": "IN", "count": 8940, "flag": "🇮🇳"},
        {"country": "Brazil", "code": "BR", "count": 2850, "flag": "🇧🇷"},
        {"country": "China", "code": "CN", "count": 2140, "flag": "🇨🇳"},
        {"country": "Russia", "code": "RU", "count": 980, "flag": "🇷🇺"},
        {"country": "South Africa", "code": "ZA", "count": 510, "flag": "🇿🇦"},
    ],
}


@router.get("/stats")
async def get_stats():
    return MOCK_STATS


@router.get("/report")
async def get_dashboard_report():
    report_data = {
        "stats": MOCK_STATS,
        "period": "August 14-21, 2026",
        "focus_areas": [
            "Fall Armyworm surge in Maharashtra and Karnataka",
            "Wheat Rust early detection across Punjab",
            "Cross-border advisory sharing with Brazil on soybean diseases",
        ],
    }
    report_text = gemini_service.generate_dashboard_report(report_data)
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
            "disease": "Fall Armyworm",
            "scientific_name": "Spodoptera frugiperda",
            "region": "Maharashtra, India",
            "lat": 18.5204,
            "lng": 73.8567,
            "severity": "critical",
            "reports_count": 342,
            "affected_area_km2": 1250,
            "first_reported": "2026-08-15T08:30:00Z",
            "status": "active",
            "crops_affected": ["Corn", "Sorghum"],
        },
        {
            "id": "OB-2026-002",
            "disease": "Leaf Rust",
            "scientific_name": "Puccinia triticina",
            "region": "Punjab, India",
            "lat": 30.9010,
            "lng": 75.8573,
            "severity": "high",
            "reports_count": 218,
            "affected_area_km2": 890,
            "first_reported": "2026-08-17T06:15:00Z",
            "status": "active",
            "crops_affected": ["Wheat"],
        },
        {
            "id": "OB-2026-003",
            "disease": "Early Blight",
            "scientific_name": "Alternaria solani",
            "region": "Karnataka, India",
            "lat": 12.9716,
            "lng": 77.5946,
            "severity": "moderate",
            "reports_count": 156,
            "affected_area_km2": 430,
            "first_reported": "2026-08-18T10:00:00Z",
            "status": "active",
            "crops_affected": ["Tomato", "Potato"],
        },
        {
            "id": "OB-2026-004",
            "disease": "Soybean Rust",
            "scientific_name": "Phakopsora pachyrhizi",
            "region": "Mato Grosso, Brazil",
            "lat": -12.6819,
            "lng": -56.9211,
            "severity": "high",
            "reports_count": 189,
            "affected_area_km2": 2100,
            "first_reported": "2026-08-14T14:45:00Z",
            "status": "active",
            "crops_affected": ["Soybean"],
        },
        {
            "id": "OB-2026-005",
            "disease": "Rice Blast",
            "scientific_name": "Magnaporthe oryzae",
            "region": "Hunan, China",
            "lat": 27.6253,
            "lng": 111.8569,
            "severity": "moderate",
            "reports_count": 97,
            "affected_area_km2": 560,
            "first_reported": "2026-08-19T09:30:00Z",
            "status": "monitoring",
            "crops_affected": ["Rice"],
        },
        {
            "id": "OB-2026-006",
            "disease": "Wheat Stripe Rust",
            "scientific_name": "Puccinia striiformis",
            "region": "Krasnodar, Russia",
            "lat": 45.0355,
            "lng": 38.9753,
            "severity": "low",
            "reports_count": 45,
            "affected_area_km2": 320,
            "first_reported": "2026-08-20T07:00:00Z",
            "status": "monitoring",
            "crops_affected": ["Wheat"],
        },
        {
            "id": "OB-2026-007",
            "disease": "Maize Streak Virus",
            "scientific_name": "Maize streak virus",
            "region": "KwaZulu-Natal, South Africa",
            "lat": -29.8587,
            "lng": 31.0218,
            "severity": "moderate",
            "reports_count": 73,
            "affected_area_km2": 180,
            "first_reported": "2026-08-16T11:20:00Z",
            "status": "active",
            "crops_affected": ["Maize"],
        },
    ]


@router.get("/crop-health")
async def get_crop_health():
    return {
        "overall_index": 74.2,
        "measurement_date": "2026-08-20",
        "regions": [
            {"name": "Punjab", "country": "IN", "ndvi": 0.72, "health_index": 85, "drought_risk": "low", "primary_crop": "Wheat", "status": "healthy"},
            {"name": "Maharashtra", "country": "IN", "ndvi": 0.48, "health_index": 58, "drought_risk": "high", "primary_crop": "Cotton", "status": "stressed"},
            {"name": "Karnataka", "country": "IN", "ndvi": 0.61, "health_index": 71, "drought_risk": "moderate", "primary_crop": "Rice", "status": "fair"},
            {"name": "Madhya Pradesh", "country": "IN", "ndvi": 0.67, "health_index": 78, "drought_risk": "low", "primary_crop": "Soybean", "status": "healthy"},
            {"name": "Tamil Nadu", "country": "IN", "ndvi": 0.55, "health_index": 65, "drought_risk": "moderate", "primary_crop": "Rice", "status": "fair"},
            {"name": "Uttar Pradesh", "country": "IN", "ndvi": 0.70, "health_index": 82, "drought_risk": "low", "primary_crop": "Wheat", "status": "healthy"},
            {"name": "Mato Grosso", "country": "BR", "ndvi": 0.74, "health_index": 88, "drought_risk": "low", "primary_crop": "Soybean", "status": "healthy"},
            {"name": "São Paulo", "country": "BR", "ndvi": 0.65, "health_index": 76, "drought_risk": "moderate", "primary_crop": "Sugarcane", "status": "fair"},
            {"name": "Krasnodar", "country": "RU", "ndvi": 0.69, "health_index": 80, "drought_risk": "low", "primary_crop": "Wheat", "status": "healthy"},
            {"name": "Hunan", "country": "CN", "ndvi": 0.62, "health_index": 73, "drought_risk": "moderate", "primary_crop": "Rice", "status": "fair"},
            {"name": "KwaZulu-Natal", "country": "ZA", "ndvi": 0.58, "health_index": 68, "drought_risk": "moderate", "primary_crop": "Maize", "status": "fair"},
        ],
    }


@router.get("/activity")
async def get_recent_activity():
    """Recent farmer activity feed for the dashboard."""
    activities = [
        {"time": "2 min ago", "type": "diagnosis", "text": "Farmer in Pune, Maharashtra diagnosed Fall Armyworm on Corn (94% confidence)", "severity": "high"},
        {"time": "8 min ago", "type": "alert", "text": "⚠️ Outbreak alert triggered for Leaf Rust in Ludhiana, Punjab — 23 reports in 48 hours", "severity": "critical"},
        {"time": "15 min ago", "type": "diagnosis", "text": "Farmer in Nashik, Maharashtra diagnosed Early Blight on Tomato (87% confidence)", "severity": "moderate"},
        {"time": "22 min ago", "type": "advisory", "text": "Voice advisory served in Tamil to farmer in Coimbatore — wheat sowing schedule query", "severity": "info"},
        {"time": "35 min ago", "type": "diagnosis", "text": "Farmer in São Paulo, Brazil diagnosed Soybean Rust (91% confidence)", "severity": "high"},
        {"time": "1 hour ago", "type": "alert", "text": "Disease cluster detected in Vidarbha region — Cotton Bollworm reports increasing", "severity": "high"},
        {"time": "1.5 hours ago", "type": "brics", "text": "🤝 Cross-border data exchange: India shared Fall Armyworm patterns with South Africa", "severity": "info"},
        {"time": "2 hours ago", "type": "advisory", "text": "Advisory served in Hindi to 45 farmers in MP — monsoon crop management", "severity": "info"},
        {"time": "3 hours ago", "type": "diagnosis", "text": "Farmer in Krasnodar, Russia diagnosed Wheat Stripe Rust (78% confidence)", "severity": "moderate"},
        {"time": "4 hours ago", "type": "advisory", "text": "Voice advisory served in Marathi — organic pest control for cotton", "severity": "info"},
    ]
    return activities

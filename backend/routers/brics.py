from fastapi import APIRouter

router = APIRouter(prefix="/api/brics", tags=["BRICS Federation"])

@router.get("/countries")
async def get_brics_countries():
    return [
        {"country": "Brazil", "code": "BR", "active_nodes": 45, "primary_crops": ["Soybeans", "Coffee", "Sugarcane"]},
        {"country": "Russia", "code": "RU", "active_nodes": 30, "primary_crops": ["Wheat", "Barley", "Sunflower"]},
        {"country": "India", "code": "IN", "active_nodes": 120, "primary_crops": ["Rice", "Wheat", "Cotton"]},
        {"country": "China", "code": "CN", "active_nodes": 200, "primary_crops": ["Rice", "Wheat", "Corn"]},
        {"country": "South Africa", "code": "ZA", "active_nodes": 25, "primary_crops": ["Corn", "Wheat", "Sugarcane"]}
    ]

@router.get("/exchange")
async def get_data_exchange():
    return {
        "status": "active",
        "last_sync": "2026-08-21T02:00:00Z",
        "shared_insights": [
            {
                "from": "Brazil",
                "to": "India",
                "insight": "Drought-resistant soybean variant success rates in similar climate zones."
            },
            {
                "from": "China",
                "to": "Russia",
                "insight": "Early warning indicators for migratory pest swarms observed in border regions."
            }
        ]
    }

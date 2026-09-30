"""Public description of every data source the platform uses and whether it is configured."""
from fastapi import APIRouter

from config import settings
from services.earth_engine_service import PROVENANCE as SATELLITE_PROVENANCE, earth_engine_service
from services.gemini_service import gemini_service

router = APIRouter(prefix="/api", tags=["Meta"])


@router.get("/sources")
async def list_sources():
    def configured(flag: bool) -> str:
        return "configured" if flag else "not_configured"

    return {
        "sources": [
            {"id": "weather", "name": "Open-Meteo forecast API", "url": "https://open-meteo.com/", "kind": "model", "status": "configured", "used_for": ["weather", "alerts", "advisory"]},
            {"id": "soil", "name": "ISRIC SoilGrids 2.0", "url": "https://soilgrids.org/", "kind": "model", "status": "configured", "used_for": ["soil", "regenerative", "advisory"]},
            # "configured" only after Earth Engine accepted the key and answered for the dataset; a key that is
            # set but failing is "unavailable", with the failure code in `detail`.
            {"id": "satellite", "name": "Sentinel-2 via Google Earth Engine", "url": SATELLITE_PROVENANCE["source_url"], "kind": "satellite_observation",
             "status": {"available": "configured", "not_configured": "not_configured"}.get(earth_engine_service.status, "unavailable"),
             "detail": earth_engine_service.error, "used_for": ["crop_health"],
             **{k: SATELLITE_PROVENANCE[k] for k in ("dataset", "provider", "processing")}},
            {"id": "ai", "name": f"Google Gemini ({settings.GEMINI_DIAGNOSIS_MODEL})", "url": "https://ai.google.dev/", "kind": "ai_model", "status": configured(gemini_service.configured), "used_for": ["diagnosis", "advisory", "report"]},
            {"id": "disease_reference", "name": "Curated disease reference (ICAR institutes)", "url": None, "kind": "curated_reference", "status": "configured", "used_for": ["diagnosis", "advisory"]},
            {"id": "community_reports", "name": "KrishiSathi diagnosis records", "url": None, "kind": "ai_classified_user_reports", "status": "configured", "used_for": ["outbreaks", "policy_dashboard"]},
            {"id": "federation", "name": "Cross-state federation signals", "url": None, "kind": "authenticated_submissions", "status": configured(bool(settings.JWT_SECRET)), "used_for": ["policy_dashboard"]},
        ]
    }

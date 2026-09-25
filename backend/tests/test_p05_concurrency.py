import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from core.database import AsyncSessionLocal
from models.schema import OutbreakRecord, DiagnosisRecord
from sqlalchemy import select, delete
from services.persistence_service import persistence_service

@pytest.mark.asyncio
async def test_macro_grid_collision():
    # Clear db
    async with AsyncSessionLocal() as session:
        await session.execute(delete(OutbreakRecord))
        await session.execute(delete(DiagnosisRecord))
        await session.commit()
    
    # Grid ID is round(lat), round(lng).
    # 10.49 rounds to 10. 9.51 rounds to 10. Grid is 10.0_10.0
    # Create cluster 1 at 10.49, 10.49
    await persistence_service.save_diagnosis({"disease_name": "Rust", "model_confidence_score": 0.9, "model_inferred_severity": "Medium"}, "Wheat", 10.49, 10.49, "en")
    await persistence_service.save_diagnosis({"disease_name": "Rust", "model_confidence_score": 0.9, "model_inferred_severity": "Medium"}, "Wheat", 10.49, 10.49, "en")
    await persistence_service.save_diagnosis({"disease_name": "Rust", "model_confidence_score": 0.9, "model_inferred_severity": "Medium"}, "Wheat", 10.49, 10.49, "en")

    # Create cluster 2 at 9.51, 9.51 (Same grid, but distance is ~150km)
    await persistence_service.save_diagnosis({"disease_name": "Rust", "model_confidence_score": 0.9, "model_inferred_severity": "Medium"}, "Wheat", 9.51, 9.51, "en")
    await persistence_service.save_diagnosis({"disease_name": "Rust", "model_confidence_score": 0.9, "model_inferred_severity": "Medium"}, "Wheat", 9.51, 9.51, "en")
    await persistence_service.save_diagnosis({"disease_name": "Rust", "model_confidence_score": 0.9, "model_inferred_severity": "Medium"}, "Wheat", 9.51, 9.51, "en")

    outbreaks = await persistence_service.get_outbreaks()
    assert len(outbreaks) == 2, f"Expected 2 outbreaks due to spatial separation, got {len(outbreaks)}"

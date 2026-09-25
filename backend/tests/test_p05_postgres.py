import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from main import app
from core.database import AsyncSessionLocal
from models.schema import OutbreakRecord, DiagnosisRecord
from sqlalchemy import select, delete
from services.persistence_service import persistence_service

@pytest.mark.asyncio
async def test_concurrent_outbreak_creation_count():
    async with AsyncSessionLocal() as session:
        await session.execute(delete(OutbreakRecord))
        await session.execute(delete(DiagnosisRecord))
        await session.commit()
    
    # Pre-insert 2 diagnoses
    await persistence_service.save_diagnosis({"disease_name": "Rust", "model_confidence_score": 0.9, "model_inferred_severity": "Medium"}, "Wheat", 10.0, 10.0, "en")
    await persistence_service.save_diagnosis({"disease_name": "Rust", "model_confidence_score": 0.9, "model_inferred_severity": "Medium"}, "Wheat", 10.0, 10.0, "en")
    
    # Fire 3 concurrent diagnosis saves
    tasks = [
        persistence_service.save_diagnosis({"disease_name": "Rust", "model_confidence_score": 0.9, "model_inferred_severity": "Medium"}, "Wheat", 10.0, 10.0, "en"),
        persistence_service.save_diagnosis({"disease_name": "Rust", "model_confidence_score": 0.9, "model_inferred_severity": "Medium"}, "Wheat", 10.0, 10.0, "en"),
        persistence_service.save_diagnosis({"disease_name": "Rust", "model_confidence_score": 0.9, "model_inferred_severity": "Medium"}, "Wheat", 10.0, 10.0, "en")
    ]
    await asyncio.gather(*tasks, return_exceptions=True)
    
    outbreaks = await persistence_service.get_outbreaks()
    assert len(outbreaks) == 1
    assert outbreaks[0]["report_count"] == 5, f"Expected 5 reports, got {outbreaks[0]['report_count']}"


import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from main import app
from services.persistence_service import persistence_service
from core.database import AsyncSessionLocal
from models.schema import OutbreakRecord, DiagnosisRecord
from datetime import datetime, timedelta
from sqlalchemy import delete

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest_asyncio
@pytest_asyncio.fixture(autouse=True)
async def clear_db():
    # Clean DB before each test
    async with AsyncSessionLocal() as session:
        await session.execute(delete(DiagnosisRecord))
        await session.execute(delete(OutbreakRecord))
        await session.commit()
    yield

@pytest.mark.asyncio
async def test_insufficient_observations_no_outbreak():
    # 2 observations (threshold is 3)
    await persistence_service.save_diagnosis({"disease_name": "Rust", "confidence": 0.9, "severity": "Medium"}, "Wheat", 10.0, 10.0, "en")
    await persistence_service.save_diagnosis({"disease_name": "Rust", "confidence": 0.9, "severity": "Medium"}, "Wheat", 10.0, 10.0, "en")
    
    outbreaks = await persistence_service.get_outbreaks()
    assert len(outbreaks) == 0

@pytest.mark.asyncio
async def test_threshold_reached_creates_outbreak():
    # 3 observations
    await persistence_service.save_diagnosis({"disease_name": "Rust", "confidence": 0.9, "severity": "Medium"}, "Wheat", 10.0, 10.0, "en")
    await persistence_service.save_diagnosis({"disease_name": "Rust", "confidence": 0.9, "severity": "Medium"}, "Wheat", 10.0, 10.0, "en")
    await persistence_service.save_diagnosis({"disease_name": "Rust", "confidence": 0.9, "severity": "Medium"}, "Wheat", 10.0, 10.0, "en")
    
    outbreaks = await persistence_service.get_outbreaks()
    assert len(outbreaks) == 1
    assert outbreaks[0]["disease"] == "Rust"
    assert outbreaks[0]["report_count"] == 3

@pytest.mark.asyncio
async def test_repeated_detection_no_duplicate():
    # 4 observations
    await persistence_service.save_diagnosis({"disease_name": "Rust", "confidence": 0.9, "severity": "Medium"}, "Wheat", 10.0, 10.0, "en")
    await persistence_service.save_diagnosis({"disease_name": "Rust", "confidence": 0.9, "severity": "Medium"}, "Wheat", 10.0, 10.0, "en")
    await persistence_service.save_diagnosis({"disease_name": "Rust", "confidence": 0.9, "severity": "Medium"}, "Wheat", 10.0, 10.0, "en")
    await persistence_service.save_diagnosis({"disease_name": "Rust", "confidence": 0.9, "severity": "Medium"}, "Wheat", 10.0, 10.0, "en")
    
    outbreaks = await persistence_service.get_outbreaks()
    assert len(outbreaks) == 1
    assert outbreaks[0]["report_count"] == 4

@pytest.mark.asyncio
async def test_outside_radius_separate_cluster():
    # 3 in cluster A (10.0, 10.0)
    await persistence_service.save_diagnosis({"disease_name": "Rust", "confidence": 0.9, "severity": "Medium"}, "Wheat", 10.0, 10.0, "en")
    await persistence_service.save_diagnosis({"disease_name": "Rust", "confidence": 0.9, "severity": "Medium"}, "Wheat", 10.0, 10.0, "en")
    await persistence_service.save_diagnosis({"disease_name": "Rust", "confidence": 0.9, "severity": "Medium"}, "Wheat", 10.0, 10.0, "en")
    
    # 3 in cluster B (20.0, 20.0) - very far
    await persistence_service.save_diagnosis({"disease_name": "Rust", "confidence": 0.9, "severity": "Medium"}, "Wheat", 20.0, 20.0, "en")
    await persistence_service.save_diagnosis({"disease_name": "Rust", "confidence": 0.9, "severity": "Medium"}, "Wheat", 20.0, 20.0, "en")
    await persistence_service.save_diagnosis({"disease_name": "Rust", "confidence": 0.9, "severity": "Medium"}, "Wheat", 20.0, 20.0, "en")
    
    outbreaks = await persistence_service.get_outbreaks()
    assert len(outbreaks) == 2

@pytest.mark.asyncio
async def test_outside_time_window_not_grouped():
    # Create old diagnoses
    async with AsyncSessionLocal() as session:
        for _ in range(2):
            d = DiagnosisRecord(
                crop="Wheat", disease="Rust", confidence=0.9, severity="Medium",
                spread_risk="Medium", lat=10.0, lng=10.0, language="en",
                timestamp=datetime.utcnow() - timedelta(days=10) # 10 days old
            )
            session.add(d)
        await session.commit()
        
    # Add 1 new diagnosis
    await persistence_service.save_diagnosis({"disease_name": "Rust", "confidence": 0.9, "severity": "Medium"}, "Wheat", 10.0, 10.0, "en")
    
    # Total is 3, but only 1 is within 7 days, so NO outbreak should exist
    outbreaks = await persistence_service.get_outbreaks()
    assert len(outbreaks) == 0

@pytest.mark.asyncio
async def test_resolved_outbreak_excluded():
    await persistence_service.save_diagnosis({"disease_name": "Rust", "confidence": 0.9, "severity": "Medium"}, "Wheat", 10.0, 10.0, "en")
    await persistence_service.save_diagnosis({"disease_name": "Rust", "confidence": 0.9, "severity": "Medium"}, "Wheat", 10.0, 10.0, "en")
    await persistence_service.save_diagnosis({"disease_name": "Rust", "confidence": 0.9, "severity": "Medium"}, "Wheat", 10.0, 10.0, "en")
    
    # Mark as resolved
    async with AsyncSessionLocal() as session:
        from sqlalchemy import update
        await session.execute(update(OutbreakRecord).values(status="resolved"))
        await session.commit()
        
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/alerts")
        assert len(res.json()) == 0
        
        res_p = await ac.get("/api/alerts/personalized?lat=10.0&lng=10.0")
        assert len(res_p.json()["alerts"]) == 0


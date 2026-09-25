import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_crop_health_unavailable():
    """Prove that hard-coded crop-health values are not returned."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/dashboard/crop-health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unavailable"
        assert len(data["regions"]) == 0
        assert data["overall_index"] is None

"""Farm digital twin: creation, token access, snapshots, recommendation feedback and app-derived metrics."""
from datetime import date, timedelta
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, update

from core import rate_limit
from core.database import AsyncSessionLocal
from helpers import open_meteo_payload
from main import app
from models.schema import AdvisoryActionRecord, DiagnosisRecord, FarmRecord, FarmSnapshotRecord
from services import measurement
from services import weather_service as ws

HEAVY_RAIN = {"precipitation_sum": [0, 80.0, 0, 0, 0, 0, 0]}


@pytest_asyncio.fixture(autouse=True)
async def clean():
    rate_limit._local_windows.clear()
    async with AsyncSessionLocal() as session:
        await session.execute(delete(AdvisoryActionRecord))
        await session.execute(delete(FarmSnapshotRecord))
        await session.execute(update(DiagnosisRecord).values(farm_id=None))
        await session.execute(delete(FarmRecord))
        await session.commit()
    yield


def api():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


def sources(**daily):
    conditions = ws.parse_conditions(open_meteo_payload(**daily), 18.5, 73.8)
    return (
        patch("services.farm_context.weather_service.get_conditions", AsyncMock(return_value=conditions)),
        patch("services.farm_context.soil_service.get_soil", AsyncMock(return_value={"status": "unavailable", "reason": "timeout"})),
        patch("services.farm_context.persistence_service.get_outbreaks", AsyncMock(return_value=[])),
    )


async def create(c, **body):
    res = await c.post("/api/farms", json={"lat": 18.520439, "lng": 73.856744, "crop": "wheat", **body})
    assert res.status_code == 201, res.text
    data = res.json()
    return data["farm_id"], {"X-Farm-Token": data["farm_token"]}, data


@pytest.mark.asyncio
async def test_create_farm_stores_no_personal_data_and_coarse_location():
    async with api() as c:
        farm_id, headers, data = await create(c)
        assert data["location"] == {"lat": 18.52, "lng": 73.857}
        assert data["crop"] == "Wheat" and data["country_code"] == "IN"
        body = (await c.get(f"/api/farms/{farm_id}", headers=headers)).json()
    assert "farm_token" not in body["farm"] and "token_hash" not in body["farm"]
    async with AsyncSessionLocal() as session:
        stored = await session.get(FarmRecord, farm_id)
    assert stored.token_hash != headers["X-Farm-Token"] and len(stored.token_hash) == 64


@pytest.mark.asyncio
async def test_farm_requires_its_own_token():
    async with api() as c:
        farm_id, _, _ = await create(c)
        other_id, other_headers, _ = await create(c)
        assert (await c.get(f"/api/farms/{farm_id}")).status_code == 404
        assert (await c.get(f"/api/farms/{farm_id}", headers={"X-Farm-Token": "guess"})).status_code == 404
        assert (await c.get(f"/api/farms/{farm_id}", headers=other_headers)).status_code == 404  # same answer as unknown


@pytest.mark.asyncio
async def test_profile_validation():
    async with api() as c:
        future = (date.today() + timedelta(days=3)).isoformat()
        assert (await c.post("/api/farms", json={"lat": 18.5, "lng": 73.8, "sowing_date": future})).status_code == 422
        assert (await c.post("/api/farms", json={"lat": 95, "lng": 73.8})).status_code == 422
        assert (await c.post("/api/farms", json={"lat": 18.5, "lng": 73.8, "area_ha": -1})).status_code == 422


@pytest.mark.asyncio
async def test_twin_intelligence_records_snapshot_and_one_action_per_day():
    async with api() as c:
        farm_id, headers, _ = await create(c, sowing_date=(date.today() - timedelta(days=90)).isoformat())
        w, s, o = sources(**HEAVY_RAIN)
        with w, s, o:
            first = (await c.get(f"/api/farms/{farm_id}/intelligence", headers=headers)).json()
            second = (await c.get(f"/api/farms/{farm_id}/intelligence", headers=headers)).json()
        assert first["top_action"]["action"] == "clear_drainage"
        assert first["farm"]["crop_stage"]["status"] == "estimated"
        action = first["twin"]["action"]
        assert action["action"] == "clear_drainage" and action["severity"] == "high" and action["followed"] is None
        assert second["twin"]["action"]["action_id"] == action["action_id"]
        assert second["twin"]["snapshot_id"] == first["twin"]["snapshot_id"]  # within the minimum interval

        history = (await c.get(f"/api/farms/{farm_id}", headers=headers)).json()
    assert len(history["snapshots"]) == 1 and len(history["actions"]) == 1
    snap = history["snapshots"][0]
    assert snap["risks"]["waterlogging"] == "high" and snap["data_quality"]["soil"] == "unavailable"
    assert snap["observations"]["rain_next_3_days_mm"] == [0, 80.0, 0]
    assert "not evidence" in history["provenance"]["notes"]


@pytest.mark.asyncio
async def test_feedback_loop():
    async with api() as c:
        farm_id, headers, _ = await create(c)
        w, s, o = sources(**HEAVY_RAIN)
        with w, s, o:
            action_id = (await c.get(f"/api/farms/{farm_id}/intelligence", headers=headers)).json()["twin"]["action"]["action_id"]
        url = f"/api/farms/{farm_id}/actions/{action_id}/feedback"
        res = await c.post(url, json={"followed": "yes"}, headers=headers)
        assert res.status_code == 200 and res.json()["followed"] == "yes" and res.json()["outcome"] is None
        res = await c.post(url, json={"outcome": "improved"}, headers=headers)
        assert res.json()["followed"] == "yes" and res.json()["outcome"] == "improved"

        assert (await c.post(url, json={}, headers=headers)).status_code == 422
        assert (await c.post(url, json={"followed": "maybe"}, headers=headers)).status_code == 422
        # "Diagnosis was wrong" only makes sense for a photo diagnosis.
        assert (await c.post(url, json={"outcome": "diagnosis_wrong"}, headers=headers)).status_code == 422

        other_id, other_headers, _ = await create(c)
        stolen = f"/api/farms/{other_id}/actions/{action_id}/feedback"
        assert (await c.post(stolen, json={"followed": "no"}, headers=other_headers)).status_code == 404


@pytest.mark.asyncio
async def test_metrics_are_aggregated_and_small_groups_suppressed():
    async with api() as c:
        w, s, o = sources(**HEAVY_RAIN)
        for i in range(6):
            rate_limit._local_windows.clear()
            farm_id, headers, _ = await create(c, crop="rice" if i < 5 else "maize")
            with w, s, o:
                action_id = (await c.get(f"/api/farms/{farm_id}/intelligence", headers=headers)).json()["twin"]["action"]["action_id"]
            await c.post(f"/api/farms/{farm_id}/actions/{action_id}/feedback",
                         json={"followed": "yes" if i < 3 else "no", "outcome": "improved" if i == 0 else None} if i < 3 else {"followed": "no"},
                         headers=headers)
    m = await measurement.feedback_metrics()
    assert m["overall"]["recommendations"] == 6
    assert m["overall"]["followed_rate"] == 0.5
    assert m["overall"]["outcomes"] == {"improved": 1}
    assert set(m["by_crop"]["groups"]) == {"Rice"} and m["by_crop"]["suppressed_groups"] == 1  # 1 maize farm is hidden
    assert m["repeat_diagnosis"]["status"] == "insufficient_data"
    assert m["provenance"]["kind"] == "app_derived_feedback"


@pytest.mark.asyncio
async def test_diagnosis_linked_to_farm_supports_diagnosis_feedback_and_feeds_the_engine():
    import base64
    import json
    from types import SimpleNamespace
    from helpers import ai_diagnosis, jpeg_bytes
    from services.gemini_service import gemini_service
    from models.exceptions import ServiceUnavailableException
    from services.weather_service import weather_service

    async with api() as c:
        farm_id, headers, _ = await create(c, crop="wheat")
        body = {"image": base64.b64encode(jpeg_bytes()).decode(), "language": "en", "farm_id": farm_id}
        ai = SimpleNamespace(text=json.dumps(ai_diagnosis(certainty="low")))
        with patch.object(gemini_service, "_call", AsyncMock(return_value=ai)), \
                patch.object(weather_service, "get_current_weather", AsyncMock(side_effect=ServiceUnavailableException("down"))):
            res = await c.post("/api/diagnose/base64", json=body, headers=headers)
            stale = await c.post("/api/diagnose/base64", json=body, headers={"X-Farm-Token": "wrong"})
        data = res.json()
        assert res.status_code == 200, res.text
        # The farm record supplied crop and location the request left out.
        assert data["context_used"]["farm"] == "linked" and data["context_used"]["crop"] == "provided"
        assert data["context_used"]["location"] == "provided"
        action = data["twin"]["action"]
        assert action["source_type"] == "diagnosis" and action["action"] == "consult_expert" and action["confidence"] == "low"
        ok = await c.post(f"/api/farms/{farm_id}/actions/{action['action_id']}/feedback", json={"outcome": "diagnosis_wrong"}, headers=headers)
        assert ok.status_code == 200 and ok.json()["outcome"] == "diagnosis_wrong"

        assert stale.status_code == 200 and stale.json()["context_used"]["farm"] == "not_linked" and stale.json()["twin"] is None

        history = (await c.get(f"/api/farms/{farm_id}", headers=headers)).json()
    assert len(history["diagnoses"]) == 1 and history["diagnoses"][0]["status"] == "disease_detected"

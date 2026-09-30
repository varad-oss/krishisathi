"""Evaluation layer: diagnosis feedback by model confidence, advisory follow-through, privacy-safe aggregation
and the admin-only evaluation data contract. All of it is self-reported feedback, never proof of effect."""
import json
from datetime import datetime, timedelta
from unittest.mock import patch

import jwt
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import delete, update

from config import settings
from core.database import AsyncSessionLocal
from main import app
from models.schema import AdvisoryActionRecord, DiagnosisRecord, FarmPlotRecord, FarmRecord, FarmSnapshotRecord
from services import measurement

SECRET = "evaluation-test-secret-with-enough-length"
client = TestClient(app)


@pytest_asyncio.fixture(autouse=True)
async def clean():
    async def wipe():
        async with AsyncSessionLocal() as session:
            await session.execute(delete(AdvisoryActionRecord))
            await session.execute(delete(FarmSnapshotRecord))
            await session.execute(delete(FarmPlotRecord))
            await session.execute(update(DiagnosisRecord).values(farm_id=None))
            await session.execute(delete(DiagnosisRecord))
            await session.execute(delete(FarmRecord))
            await session.commit()
    await wipe()
    yield
    await wipe()


async def seed_diagnoses(n: int, certainty: str, wrong: int, crop: str = "Wheat", quality: str = "good", lat: float = 18.52):
    """n farms, each with one diagnosis and its recommendation; `wrong` of them report diagnosis_wrong, the rest 'improved'."""
    now = datetime.utcnow()
    async with AsyncSessionLocal() as session:
        for i in range(n):
            farm = FarmRecord(token_hash="x", lat=lat, lng=73.857, crop=crop, created_at=now, updated_at=now)
            session.add(farm)
            await session.flush()
            d = DiagnosisRecord(crop=crop, disease="Rust", diagnosis_status="disease_detected", certainty=certainty, image_quality=quality,
                                guidance_level="escalate" if certainty == "low" else "supported", model_version="test-model",
                                differential=[{"name": "Leaf rust", "likelihood": "moderate"}], lat=lat, lng=73.857, farm_id=farm.id,
                                timestamp=now)
            session.add(d)
            await session.flush()
            session.add(AdvisoryActionRecord(farm_id=farm.id, created_at=now - timedelta(days=5), source_type="diagnosis", source_ref=d.id,
                                             action="treat_as_advised", category="disease", confidence=certainty, crop=crop,
                                             followed="yes", outcome="diagnosis_wrong" if i < wrong else "improved", outcome_at=now))
            session.add(FarmSnapshotRecord(farm_id=farm.id, created_at=now, risks={"disease": "moderate"}, data_quality={},
                                           observations={"ndvi": 0.6}))
        await session.commit()


async def seed_advisories(followed: list[str], crop: str = "Rice", category: str = "waterlogging"):
    now = datetime.utcnow()
    async with AsyncSessionLocal() as session:
        for f in followed:
            farm = FarmRecord(token_hash="x", lat=18.52, lng=73.857, crop=crop, created_at=now, updated_at=now)
            session.add(farm)
            await session.flush()
            session.add(AdvisoryActionRecord(farm_id=farm.id, created_at=now, source_type="intelligence", action="clear_drainage",
                                             category=category, severity="high", confidence="moderate", crop=crop, followed=f,
                                             outcome="same" if f == "yes" else None))
        await session.commit()


@pytest.mark.asyncio
async def test_diagnosis_wrong_rate_by_model_confidence_with_small_tiers_suppressed():
    await seed_diagnoses(6, "high", wrong=1)
    await seed_diagnoses(5, "moderate", wrong=2)
    await seed_diagnoses(2, "low", wrong=2)       # too few to show
    m = await measurement.evaluation_metrics()
    d = m["diagnosis"]
    assert d["diagnosis_feedback_count"] == 13 and d["diagnosis_wrong"] == 5
    tiers = d["observed_feedback_by_model_confidence"]["tiers"]
    assert (tiers["high"]["diagnosis_wrong"], tiers["high"]["feedback_count"]) == (1, 6)
    assert (tiers["moderate"]["diagnosis_wrong"], tiers["moderate"]["feedback_count"]) == (2, 5)
    assert tiers["low"] == {"status": "suppressed", "minimum": 5}
    assert "not a calibration curve" in d["observed_feedback_by_model_confidence"]["label"]
    assert d["by_crop"]["groups"]["Wheat"]["feedback_count"] == 13
    assert d["by_image_quality"]["groups"]["good"]["diagnosis_wrong"] == 5
    assert d["by_guidance_level"]["suppressed_groups"] == 1  # the two 'escalate' records
    assert all(c["count"] >= 5 for c in d["uncertainty_distribution"]) and d["uncertainty_cells_suppressed"] == 1


@pytest.mark.asyncio
async def test_too_little_diagnosis_feedback_is_insufficient_not_a_rate():
    await seed_diagnoses(3, "high", wrong=1)
    d = (await measurement.evaluation_metrics())["diagnosis"]
    assert d["status"] == "insufficient_data" and "diagnosis_wrong_rate" not in d
    assert d["observed_feedback_by_model_confidence"]["tiers"]["high"]["status"] == "suppressed"


@pytest.mark.asyncio
async def test_advisory_follow_through_partial_and_outcomes():
    await seed_advisories(["yes", "yes", "partial", "no", "not_applicable", "yes"])
    await seed_advisories(["yes", "no"], crop="Maize", category="heat_stress")  # small groups
    a = (await measurement.evaluation_metrics())["advisory"]
    o = a["overall"]
    assert o["recommendations"] == 8 and o["follow_through_answers"] == 7 and o["not_applicable"] == 1
    assert (o["followed_rate"], o["partial_rate"], o["not_followed_rate"]) == (0.57, 0.14, 0.29)
    assert o["outcome_distribution"] == {"same": 4}
    assert set(a["by_crop"]["groups"]) == {"Rice"} and a["by_crop"]["suppressed_groups"] == 1
    assert set(a["by_category"]["groups"]) == {"waterlogging"}
    assert list(a["by_region"]["groups"]) == ["18,73"]


@pytest.mark.asyncio
async def test_metrics_are_labelled_self_reported_and_never_claim_success_or_yield():
    await seed_advisories(["yes"] * 5)
    m = await measurement.evaluation_metrics()
    assert m["label"] == "KrishiSathi self-reported feedback" and m["provenance"]["kind"] == "farmer_reported"
    text = json.dumps(m).lower()
    assert "success_rate" not in text and "yield_improvement" not in text
    assert "yield change" in m["provenance"]["does_not_show"]


@pytest.mark.asyncio
async def test_public_evaluation_endpoint_has_no_farm_identifiers():
    await seed_diagnoses(5, "high", wrong=1)
    body = client.get("/api/dashboard/evaluation").json()
    text = json.dumps(body)
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        ids = [r for (r,) in (await session.execute(select(FarmRecord.id))).all()]
    assert not any(i in text for i in ids) and "73.857" not in text and "token" not in text


def _admin(role="admin"):
    return {"Authorization": "Bearer " + jwt.encode({"sub": "ops", "role": role}, SECRET, algorithm="HS256")}


@pytest.mark.asyncio
async def test_evaluation_records_are_admin_only_and_pseudonymous():
    await seed_diagnoses(2, "moderate", wrong=1)
    await seed_advisories(["yes"])
    with patch.object(settings, "JWT_SECRET", SECRET):
        assert client.get("/api/dashboard/evaluation/records").status_code == 401
        assert client.get("/api/dashboard/evaluation/records", headers=_admin("partner")).status_code == 403
        res = client.get("/api/dashboard/evaluation/records", headers=_admin())
    assert res.status_code == 200
    body = res.json()
    assert body["contract_version"] == "1.0" and "never used to retrain" in body["use_policy"].lower()
    assert body["count"] == 3
    diag = next(r for r in body["records"] if r["record_type"] == "diagnosis")
    assert diag["prediction"]["certainty"] == "moderate" and diag["prediction"]["differential"][0]["name"] == "Leaf rust"
    assert diag["prediction"]["image_quality"] == "good" and diag["farmer_feedback"]["kind"] == "farmer_reported"
    assert diag["later_observation"]["kind"] == "later_app_assessment" and diag["later_observation"]["risk_level"] == "moderate"
    adv = next(r for r in body["records"] if r["record_type"] == "advisory")
    assert adv["later_observation"] is None  # no later snapshot: nothing is invented
    text = json.dumps(body)
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        ids = [r for (r,) in (await session.execute(select(FarmRecord.id))).all()]
        action_ids = [r for (r,) in (await session.execute(select(AdvisoryActionRecord.id))).all()]
    assert not any(i in text for i in ids + action_ids) and "73.857" not in text
    assert {r["region"] for r in body["records"]} == {"18,73"}

"""BRICS interoperability: schema v1.0, country adapters, privacy-aware signal API and federation contract."""
from datetime import date, datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import jwt
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import delete

from config import settings
from core import rate_limit
from core.database import AsyncSessionLocal
from helpers import RUST
from main import app
from models.interop import RegionalAgriSignal
from models.interop_v1 import PrivacyV1
from test_interop_schemas import _obs
from models.schema import DiagnosisRecord, FederationSignalRecord, OutbreakRecord
from services.federation import FedAvg, ModelUpdate, registry
from services.interop import adapter as adapters
from services.persistence_service import persistence_service

client = TestClient(app)
SECRET = "interop-test-secret-with-32-bytes!!"


def auth(role="partner"):
    return {"Authorization": "Bearer " + jwt.encode({"sub": "partner-br", "role": role}, SECRET, algorithm="HS256")}


@pytest.fixture(autouse=True)
def secret():
    rate_limit._local_windows.clear()
    with patch.object(settings, "JWT_SECRET", SECRET):
        yield


@pytest_asyncio.fixture
async def clean_db():
    async with AsyncSessionLocal() as session:
        for table in (DiagnosisRecord, OutbreakRecord, FederationSignalRecord):
            await session.execute(delete(table))
        await session.commit()
    yield


# --- schemas ---------------------------------------------------------------------------------------

def test_schema_catalogue_is_versioned():
    body = client.get("/api/interoperability/schemas").json()
    assert body["schema_version"] == "1.0"
    assert {"Crop", "Disease", "Observation", "RiskSignal", "Advisory", "OutcomeSummary", "Farm"} <= set(body["schemas"])


# --- public catalogues ------------------------------------------------------------------------------

def test_crops_are_paginated_with_an_opaque_cursor():
    first = client.get("/api/interoperability/crops", params={"limit": 5}).json()
    assert first["count"] == 5 and first["country_code"] == "IN" and first["next_cursor"]
    assert first["items"][0] == {"schema_version": "1.0", "crop_code": "wheat", "name_en": "Wheat", "group": "cereal", "aliases": []}
    rest = client.get("/api/interoperability/crops", params={"limit": 50, "cursor": first["next_cursor"]}).json()
    assert rest["next_cursor"] is None and first["count"] + rest["count"] == 16
    assert any(c["crop_code"] == "pearl_millet" and "bajra" in c["aliases"] for c in first["items"] + rest["items"])
    assert client.get("/api/interoperability/crops", params={"cursor": "%%%"}).status_code == 422


def test_diseases_carry_crop_codes_and_sources():
    items = client.get("/api/interoperability/diseases", params={"limit": 200}).json()["items"]
    rust = next(d for d in items if d["disease_code"] == "wheat-rust")
    assert rust["crop_codes"] == ["wheat"] and rust["references"][0]["organization"].startswith("ICAR")
    assert rust["provenance"]["kind"] == "curated_reference"


def test_unknown_country_has_no_adapter():
    res = client.get("/api/interoperability/crops", params={"country": "ZZ"})
    assert res.status_code == 404 and "ZZ" in res.json()["error"]["message"]


# --- authenticated signals --------------------------------------------------------------------------

@pytest.mark.parametrize("path", ["weather-signals", "agricultural-observations", "risk-signals"])
def test_signals_require_a_partner_token(path):
    assert client.get(f"/api/interoperability/{path}").status_code == 401
    assert client.get(f"/api/interoperability/{path}", headers=auth("user")).status_code == 403
    with patch.object(settings, "JWT_SECRET", None):
        assert client.get(f"/api/interoperability/{path}", headers=auth()).json()["error"]["code"] == "AUTH_NOT_CONFIGURED"


@pytest.mark.asyncio
async def test_observations_are_aggregated_to_grid_cells_with_small_groups_suppressed(clean_db):
    for lat, lng in [(18.52, 73.85), (18.61, 73.91), (18.70, 73.80)]:  # three detections in one 0.5° cell
        await persistence_service.save_diagnosis(RUST, "Wheat", lat, lng, "en")
    for lat, lng in [(30.9, 75.8), (30.95, 75.85)]:  # two in another cell: below the minimum group size
        await persistence_service.save_diagnosis(RUST, "Wheat", lat, lng, "en")
    await persistence_service.save_diagnosis({**RUST, "certainty": "low"}, "Wheat", 18.52, 73.85, "en")  # low certainty never counts

    body = client.get("/api/interoperability/agricultural-observations", headers=auth()).json()
    assert body["privacy"] == {"aggregation": "0.5° grid cells or state reference points", "minimum_group_size": 3,
                               "spatial_resolution": "0.5° (~55 km)", "personal_data": "none"}
    assert len(body["items"]) == 1
    obs = body["items"][0]
    assert obs["geo"] == {"country_code": "IN", "region_code": None, "grid": {"cell_deg": 0.5, "lat": 18.5, "lng": 73.5}, "basis": "grid_cell"}
    assert (obs["value"], obs["unit"], obs["crop_code"], obs["confidence"]) == (3, "count", "wheat", "low")
    assert obs["provenance"]["kind"] == "ai_classified_reports"
    text = str(body)
    assert "18.52" not in text and "73.85" not in text and "farm" not in text.lower().replace("farmer_reported", "")


@pytest.mark.asyncio
async def test_risk_signals_from_clusters_and_regional_federation(clean_db):
    for _ in range(3):
        await persistence_service.save_diagnosis(RUST, "Wheat", 30.9, 75.85, "en")
    await persistence_service.save_federation_signal(RegionalAgriSignal(
        signal_id="11111111-1111-4111-8111-111111111111", from_state="PB", to_state="HR", signal_type="disease_alert", severity="critical",
        message="Yellow rust reports rising", disease_name="Yellow rust", affected_crop="wheat", report_count=40,
        metadata={"farmer_name": "never exported"}))
    body = client.get("/api/interoperability/risk-signals", headers=auth("system")).json()
    by_type = {s["signal_type"]: s for s in body["items"]}
    cluster, fed = by_type["disease_cluster"], by_type["disease_alert"]
    assert cluster["geo"]["grid"] == {"cell_deg": 0.5, "lat": 30.5, "lng": 75.5} and cluster["report_count"] == 3
    assert cluster["confidence"] == "low" and "not a confirmed outbreak" in cluster["provenance"]["notes"]
    assert (fed["source_region"], fed["affected_region"], fed["severity"]) == ("IN-PB", "IN-HR", "high")
    assert fed["crop_codes"] == ["wheat"] and fed["provenance"]["kind"] == "authenticated_submission"
    assert "never exported" not in str(body) and "Yellow rust reports rising" not in str(body)
    assert "never assert" in body["notes"]


def test_weather_signals_publish_nothing_for_an_unavailable_forecast():
    risk = {"regions": [
        {"state": "MH", "status": "available", "insights": [{"id": "heavy_rain", "severity": "warning", "date": "2026-09-27",
                                                             "basis": {"source": {"name": "India Meteorological Department (IMD)"}}}]},
        {"state": "PB", "status": "unavailable", "insights": []}],
        "provenance": {"retrieved_at": "2026-09-26T04:00:00+00:00"}}
    with patch("services.interop.india.state_weather_risk", AsyncMock(return_value=risk)):
        items = client.get("/api/interoperability/weather-signals", headers=auth()).json()["items"]
    assert len(items) == 1
    s = items[0]
    assert (s["category"], s["severity"], s["geo"]["region_code"], s["geo"]["basis"]) == ("waterlogging", "high", "IN-MH", "region_reference_point")
    assert s["provenance"]["kind"] == "forecast" and "IMD" in s["provenance"]["method"]


# --- adapters and federation ------------------------------------------------------------------------

class PartnerAdapter:
    """Test-only stand-in for another country's adapter: proves the API needs no change to serve it."""
    country_code, name = "ZA", "Test partner"
    privacy = PrivacyV1(aggregation="region", minimum_group_size=10, spatial_resolution="state")

    def describe(self):
        return {"country_code": "ZA", "name": self.name}

    async def crops(self):
        return []

    async def diseases(self):
        return []

    async def weather_signals(self):
        return []

    async def observations(self, since):
        return [_obs()]

    async def risk_signals(self, since):
        return []


def test_another_country_plugs_in_through_an_adapter():
    adapters.register(PartnerAdapter())
    try:
        body = client.get("/api/interoperability/agricultural-observations", params={"country": "za"}, headers=auth()).json()
        assert body["country_code"] == "ZA" and body["count"] == 1
        assert {a["country_code"] for a in client.get("/api/interoperability/adapters").json()["adapters"]} == {"IN", "BR", "ZA"}
    finally:
        adapters._REGISTRY.pop("ZA")
    with pytest.raises(TypeError):
        adapters.register(object())


def test_fedavg_weights_by_examples_and_validates_updates():
    a = ModelUpdate("m", "1.0", "IN", 300, (1.0, 0.0))
    b = ModelUpdate("m", "1.0", "BR", 100, (0.0, 4.0))
    result = FedAvg().aggregate([a, b])
    assert result.parameters == (0.75, 1.0) and result.contributors == ("BR", "IN") and result.total_examples == 400
    for bad in ([a], [a, ModelUpdate("m", "2.0", "BR", 10, (0.0, 0.0))], [a, ModelUpdate("m", "1.0", "BR", 10, (0.0,))],
                [a, ModelUpdate("m", "1.0", "BR", 0, (0.0, 0.0))]):
        with pytest.raises(ValueError):
            FedAvg().aggregate(bad)


def test_model_registry_is_honest_about_federation():
    body = client.get("/api/interoperability/models").json()
    assert body["federation"]["status"] == "not_running" and body["federation"]["update_contract"]["raw_data_shared"] is False
    assert all(m["federated"] is False for m in body["models"])
    assert {m["kind"] for m in body["models"]} == {"external_foundation_model", "rule_engine"}
    assert registry(datetime(2026, 1, 1, tzinfo=timezone.utc))["generated_at"].startswith("2026-01-01")
    # Running models and federation-ready contracts are listed separately; no contract claims to train anything.
    assert set(body["currently_running"]) == {m["model_id"] for m in body["models"]}
    ready = {c["id"]: c["status"] for c in body["federated_ready"]}
    assert ready["fedavg_aggregator"] == ready["model_update_contract"] == "contract_only"
    assert all("simulation" not in m["kind"] for m in body["models"])

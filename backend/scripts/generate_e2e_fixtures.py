"""Regenerates the Milestone 11 E2E fixtures (field crop health, field intelligence, plot, evaluation, interoperability
comparison) from the real routes and shaping code. Upstreams (Open-Meteo, SoilGrids, Earth Engine, IBGE SIDRA) are stubbed
with TEST VALUES, so the fixtures follow the live contract but contain no real observations. The committed `intelligence`
and `farm_intelligence` fixtures are kept as they are, because existing journeys assert their content.

Run from backend/: python3 scripts/generate_e2e_fixtures.py ../frontend/e2e/fixtures/api.json"""
import asyncio, json, os, sys, tempfile
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch
tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{tmp}/fx.db"
sys.path.insert(0, "tests"); sys.path.insert(0, ".")
from alembic import command
from alembic.config import Config
command.upgrade(Config("alembic.ini"), "head")
import httpx
from fastapi.testclient import TestClient
from main import app
from helpers import open_meteo_payload
from services import weather_service as ws, earth_engine_service as ees
from services.earth_engine_service import EarthEngineService, polygon_field, point_field
from services.plots import validate_polygon
from test_brazil_adapter import PAYLOAD
from test_plots import square

out_path = sys.argv[1]
fx = json.load(open(out_path))
client = TestClient(app)
LAT, LNG = 18.52, 73.856
cond = ws.parse_conditions(open_meteo_payload(relative_humidity_2m_mean=[60, 90, 92, 91, 60, 60, 60]), LAT, LNG)
outbreak = [{"id": "o1", "disease": "Late Blight", "lat": 18.6, "lng": 73.9, "radius_km": 50, "severity": "high", "report_count": 4,
             "crop_targets": ["Tomato"], "timestamp": "2026-09-29T10:00:00+00:00", "location": "18.6, 73.9"}]

def win(ndvi, px, count=4):
    return {"ndvi": ndvi, "clear_px": px, "count": count, "latest_ms": 1790985600000, "valid_px": px + 5,
            "latest_id": ["20260920T053901_20260920T054440_T43QCU"], "latest_cloud_pct": [18.2]}

def ee_result(field, info):
    svc = EarthEngineService.__new__(EarthEngineService); svc.sar_available = True
    m = MagicMock(); m.Dictionary.return_value.getInfo.return_value = info
    with patch.object(ees, "ee", m, create=True), patch.object(EarthEngineService, "_window_stats", staticmethod(lambda *a: None)), \
         patch.object(EarthEngineService, "_field_extras", staticmethod(lambda *a: {})), patch.object(EarthEngineService, "_sar_stats", staticmethod(lambda *a: None)):
        r = svc._field_ndvi(field, date(2026, 9, 30))
    r["provenance"] = ees.PROVENANCE
    return r

sar = {"ASCENDING": {"vv_db": -9.1, "vh_db": -15.8, "count": 2, "latest_ms": 1790899200000}, "DESCENDING": {"vv_db": None, "vh_db": None, "count": 0, "latest_ms": None}}
sar_prev = {"ASCENDING": {"vv_db": -9.4, "vh_db": -15.2, "count": 2, "latest_ms": 1789862400000}, "DESCENDING": sar["DESCENDING"]}
plot = {"geometry": validate_polygon(square(160, LAT, LNG))["geometry"], "area_ha": validate_polygon(square(160, LAT, LNG))["area_ha"]}
poly = ee_result(polygon_field(plot), {"current": win(0.52, 240), "previous": win(0.66, 250), "roi_px": 256, "landcover": {"40": 230.0, "10": 16.0, "50": 10.0},
                                        "baseline_1": win(0.63, 250), "baseline_2": win(0.6, 245), "baseline_3": win(None, 0, 2),
                                        "sar_current": sar, "sar_previous": sar_prev})
point = ee_result(point_field(LAT, LNG), {"current": win(0.55, 1800), "previous": win(0.61, 1700), "landcover": {"40": 1300.0, "10": 400.0, "50": 263.0},
                                           "baseline_1": win(0.6, 1900), "baseline_2": win(0.62, 1850), "sar_current": sar, "sar_previous": sar_prev})

def intel(health, with_plot=False):
    with patch("services.farm_context.weather_service.get_conditions", AsyncMock(return_value=cond)), \
         patch("services.farm_context.soil_service.get_soil", AsyncMock(return_value={"status": "unavailable", "reason": "timeout"})), \
         patch("services.farm_context.persistence_service.get_outbreaks", AsyncMock(return_value=outbreak)), \
         patch.object(EarthEngineService, "get_crop_health", AsyncMock(return_value=health)):
        created = client.post("/api/farms", json={"lat": LAT, "lng": LNG, "crop": "tomato"}).json()
        h = {"X-Farm-Token": created["farm_token"]}
        if with_plot:
            assert client.put(f"/api/farms/{created['farm_id']}/plot", headers=h, json={"geometry": plot["geometry"]}).status_code == 200
        return client.get(f"/api/farms/{created['farm_id']}/intelligence", headers=h).json()

fx["farm_intelligence_field"] = intel(poly, with_plot=True)
fx["field_crop_health_point"] = point
fx["field_crop_health_polygon"] = poly
fx["field_crop_health_insufficient"] = ee_result(polygon_field(plot), {"current": win(0.7, 30), "previous": win(0.6, 200), "roi_px": 256, "landcover": {"40": 256.0}})
fx["field_crop_health_insufficient"]["provenance"] = ees.PROVENANCE
fx["plot_geometry"] = plot["geometry"]
fx["plot"] = {"plot_id": "7d0b0f6e-2a8e-4d0a-9d8c-1f7a3f0b5e21", "area_ha": plot["area_ha"], "crop": "Tomato", "sowing_date": None,
              "created_at": "2026-09-30T05:00:00+00:00", "updated_at": "2026-09-30T05:00:00+00:00", "geometry": plot["geometry"]}

async def sidra_get(self, url, params=None):
    return httpx.Response(200, json=PAYLOAD, request=httpx.Request("GET", url))
with patch.object(httpx.AsyncClient, "get", sidra_get):
    fx["interop_compare"] = client.get("/api/interoperability/compare", params={"crop": "soybean"}).json()
fx["interop_compare"]["_fixture_note"] = "Brazil sample values are TEST VALUES (SIDRA HTTP call stubbed), not IBGE data."
# Evaluation: seed through the same helpers as the backend tests.
from test_evaluation import seed_advisories, seed_diagnoses
from services import measurement
async def seed():
    await seed_diagnoses(8, "high", wrong=1); await seed_diagnoses(6, "moderate", wrong=2); await seed_diagnoses(2, "low", wrong=1)
    await seed_advisories(["yes", "yes", "partial", "no", "yes", "not_applicable", "yes"])
    return await measurement.evaluation_metrics()
fx["evaluation"] = json.loads(json.dumps(asyncio.run(seed()), default=str))
fx["intelligence"], fx["farm_intelligence"] = json.load(open(out_path))["intelligence"], json.load(open(out_path))["farm_intelligence"]
json.dump(fx, open(out_path, "w"), indent=1, ensure_ascii=False)
import shutil
shutil.rmtree(tmp, ignore_errors=True)
print("ok", fx["farm_intelligence_field"]["top_action"]["priority_reason"], fx["field_crop_health_polygon"]["status"], fx["field_crop_health_insufficient"]["status"])

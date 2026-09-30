"""Field plots: geometry validation, persistence, authorization and polygon-aware satellite statistics."""
import math
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from core import rate_limit
from core.database import AsyncSessionLocal
from main import app
from models.schema import FarmPlotRecord, FarmRecord
from services import earth_engine_service as ees
from services.earth_engine_service import EarthEngineService, point_field, polygon_field
from services.plots import PlotError, area_ha, geometry_key, validate_polygon

LAT, LNG = 18.520, 73.857


def square(side_m: float, lat: float = LAT, lng: float = LNG, closed: bool = True) -> dict:
    """An axis-aligned square of the given side centred on (lat, lng), as a GeoJSON Polygon."""
    dlat = side_m / 2 / 111_195
    dlng = dlat / math.cos(math.radians(lat))
    ring = [[lng - dlng, lat - dlat], [lng + dlng, lat - dlat], [lng + dlng, lat + dlat], [lng - dlng, lat + dlat]]
    return {"type": "Polygon", "coordinates": [ring + ([ring[0]] if closed else [])]}


# --- validation ----------------------------------------------------------------------------------

def test_area_of_a_100_m_square_is_one_hectare():
    assert validate_polygon(square(100))["area_ha"] == pytest.approx(1.0, rel=0.01)
    assert area_ha(square(200)["coordinates"][0]) == pytest.approx(4.0, rel=0.01)


def test_ring_is_closed_and_stored_counter_clockwise():
    ring = square(100, closed=False)["coordinates"][0][::-1]  # clockwise, unclosed
    out = validate_polygon({"type": "Polygon", "coordinates": [ring]})["geometry"]["coordinates"][0]
    assert out[0] == out[-1] and len(out) == 5
    twice = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(out, out[1:]))
    assert twice > 0


@pytest.mark.parametrize("geometry,code", [
    (None, "invalid_geometry"),
    ({"type": "Point", "coordinates": [LNG, LAT]}, "invalid_geometry"),
    ({"type": "Polygon"}, "empty_polygon"),
    ({"type": "Polygon", "coordinates": []}, "empty_polygon"),
    ({"type": "Polygon", "coordinates": [[[LNG, LAT], [LNG, LAT], [LNG, LAT]]]}, "empty_polygon"),
    ({"type": "Polygon", "coordinates": [[[LNG, LAT], [LNG + 0.001, LAT]]]}, "empty_polygon"),
    ({"type": "Polygon", "coordinates": [[["73.8", "18.5"], [LNG, LAT], [LNG, LAT + 0.01]]]}, "invalid_geometry"),
    ({"type": "Polygon", "coordinates": [[[LNG, LAT, 5], [LNG, LAT], [LNG, LAT]]]}, "invalid_geometry"),
    ({"type": "Polygon", "coordinates": [[[float("nan"), LAT], [LNG, LAT], [LNG, LAT + 0.01]]]}, "invalid_geometry"),
    ({"type": "Polygon", "coordinates": [[[190, LAT], [LNG, LAT], [LNG, LAT + 0.01]]]}, "out_of_bounds"),
    ({"type": "Polygon", "coordinates": square(100)["coordinates"] * 2}, "holes_not_supported"),
    ({"type": "Polygon", "coordinates": square(100)["coordinates"], "properties": {"owner": "x"}}, "invalid_geometry"),
])
def test_malformed_geojson_is_rejected(geometry, code):
    with pytest.raises(PlotError) as e:
        validate_polygon(geometry)
    assert e.value.code == code


def test_self_intersecting_bow_tie_is_rejected():
    d = 0.001
    bow = [[LNG, LAT], [LNG + d, LAT + d], [LNG + d, LAT], [LNG, LAT + d], [LNG, LAT]]
    with pytest.raises(PlotError) as e:
        validate_polygon({"type": "Polygon", "coordinates": [bow]})
    assert e.value.code == "self_intersecting"


def test_area_limits_and_distance_from_farm():
    with pytest.raises(PlotError) as e:
        validate_polygon(square(5))  # 0.0025 ha
    assert e.value.code == "area_too_small"
    with pytest.raises(PlotError) as e:
        validate_polygon(square(1500))  # 225 ha
    assert e.value.code == "area_too_large"
    with pytest.raises(PlotError) as e:
        validate_polygon(square(100, lat=LAT + 0.1), LAT, LNG)  # ~11 km away
    assert e.value.code == "too_far_from_farm"


def test_geometry_key_is_stable_and_does_not_contain_coordinates():
    g = validate_polygon(square(100))["geometry"]
    key = geometry_key(g)
    assert key == geometry_key(validate_polygon(square(100))["geometry"]) and len(key) == 24
    assert "73.8" not in key and "18.5" not in key


# --- persistence and authorization ---------------------------------------------------------------

@pytest_asyncio.fixture(autouse=True)
async def clean():
    rate_limit._local_windows.clear()
    async with AsyncSessionLocal() as session:
        await session.execute(delete(FarmPlotRecord))
        await session.commit()
    yield
    async with AsyncSessionLocal() as session:
        await session.execute(delete(FarmPlotRecord))
        await session.commit()


def api():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


async def create(c):
    res = await c.post("/api/farms", json={"lat": LAT, "lng": LNG, "crop": "wheat"})
    assert res.status_code == 201
    data = res.json()
    return data["farm_id"], {"X-Farm-Token": data["farm_token"]}


@pytest.mark.asyncio
async def test_plot_create_read_edit_remove():
    async with api() as c:
        farm_id, h = await create(c)
        assert (await c.get(f"/api/farms/{farm_id}/plot", headers=h)).json() == {"plot": None}
        saved = (await c.put(f"/api/farms/{farm_id}/plot", headers=h, json={"geometry": square(100)})).json()["plot"]
        assert saved["area_ha"] == pytest.approx(1.0, rel=0.01) and saved["crop"] == "Wheat"
        assert saved["geometry"]["type"] == "Polygon"
        edited = (await c.put(f"/api/farms/{farm_id}/plot", headers=h, json={"geometry": square(200), "crop": "rice"})).json()["plot"]
        assert edited["plot_id"] == saved["plot_id"] and edited["area_ha"] == pytest.approx(4.0, rel=0.01) and edited["crop"] == "Rice"
        history = (await c.get(f"/api/farms/{farm_id}", headers=h)).json()
        assert history["plot"]["area_ha"] == edited["area_ha"] and "geometry" not in history["plot"]
        assert (await c.delete(f"/api/farms/{farm_id}/plot", headers=h)).json() == {"plot": None, "removed": True}
        assert (await c.get(f"/api/farms/{farm_id}/plot", headers=h)).json() == {"plot": None}


@pytest.mark.asyncio
async def test_invalid_plot_is_a_422_with_a_clear_code():
    async with api() as c:
        farm_id, h = await create(c)
        res = await c.put(f"/api/farms/{farm_id}/plot", headers=h, json={"geometry": square(100, lat=LAT + 0.2)})
        assert res.status_code == 422 and res.json()["error"]["code"] == "INVALID_GEOMETRY"
        res = await c.put(f"/api/farms/{farm_id}/plot", headers=h, json={"geometry": "not geojson"})
        assert res.status_code == 422


@pytest.mark.asyncio
async def test_plot_needs_the_farm_token():
    async with api() as c:
        farm_id, h = await create(c)
        other_id, other_h = await create(c)
        await c.put(f"/api/farms/{farm_id}/plot", headers=h, json={"geometry": square(100)})
        for headers in ({}, {"X-Farm-Token": "wrong"}, other_h):
            assert (await c.get(f"/api/farms/{farm_id}/plot", headers=headers)).status_code == 404
            assert (await c.put(f"/api/farms/{farm_id}/plot", headers=headers, json={"geometry": square(50)})).status_code == 404
            assert (await c.delete(f"/api/farms/{farm_id}/plot", headers=headers)).status_code == 404
            assert (await c.get(f"/api/farms/{farm_id}/crop-health", headers=headers)).status_code == 404
        assert (await c.get(f"/api/farms/{other_id}/plot", headers=other_h)).json() == {"plot": None}


@pytest.mark.asyncio
async def test_field_crop_health_prefers_the_polygon_and_falls_back_to_the_point():
    plot_health = AsyncMock(return_value={"status": "available", "roi": {"mode": "polygon"}})
    point_health = AsyncMock(return_value={"status": "available", "roi": {"mode": "point"}})
    with patch.object(EarthEngineService, "get_plot_crop_health", plot_health), patch.object(EarthEngineService, "get_point_crop_health", point_health):
        async with api() as c:
            farm_id, h = await create(c)
            assert (await c.get(f"/api/farms/{farm_id}/crop-health", headers=h)).json()["roi"]["mode"] == "point"
            await c.put(f"/api/farms/{farm_id}/plot", headers=h, json={"geometry": square(100)})
            assert (await c.get(f"/api/farms/{farm_id}/crop-health", headers=h)).json()["roi"]["mode"] == "polygon"
            plot_arg = plot_health.call_args.args[0]
            assert plot_arg["area_ha"] == pytest.approx(1.0, rel=0.01) and plot_arg["geometry"]["type"] == "Polygon"
            # The farm moved far away from the plot: the stale outline is not used.
            await c.post(f"/api/farms/{farm_id}", headers=h, json={"lat": LAT + 1, "lng": LNG, "crop": "wheat"})
            assert (await c.get(f"/api/farms/{farm_id}/crop-health", headers=h)).json()["roi"]["mode"] == "point"


@pytest.mark.asyncio
async def test_deleting_a_farm_row_leaves_no_readable_plot():
    async with api() as c:
        farm_id, h = await create(c)
        await c.put(f"/api/farms/{farm_id}/plot", headers=h, json={"geometry": square(100)})
    async with AsyncSessionLocal() as session:
        await session.execute(delete(FarmPlotRecord).where(FarmPlotRecord.farm_id == farm_id))
        await session.execute(delete(FarmRecord).where(FarmRecord.id == farm_id))
        await session.commit()
    async with api() as c:
        assert (await c.get(f"/api/farms/{farm_id}/plot", headers=h)).status_code == 404


# --- polygon satellite statistics (Earth Engine responses mocked) --------------------------------

PLOT = {"geometry": validate_polygon(square(100))["geometry"], "area_ha": 1.0}
SCENE = {"latest_id": ["20260227T053901_20260227T054440_T43REQ"], "latest_cloud_pct": [12.3]}
CROPLAND = {"40": 90.0, "10": 5.0, "50": 5.0}


def _win(ndvi, px, count=3, valid=100):
    return {"ndvi": ndvi, "clear_px": px, "count": count, "latest_ms": 1772150400000, "valid_px": valid, **SCENE}


def _polygon_result(info, sar_available=False):
    svc = EarthEngineService.__new__(EarthEngineService)
    svc.sar_available = sar_available
    ee_mock = MagicMock()
    ee_mock.Dictionary.return_value.getInfo.return_value = info
    with patch.object(ees, "ee", ee_mock, create=True), patch.object(EarthEngineService, "_window_stats", staticmethod(lambda *a: None)), \
            patch.object(EarthEngineService, "_field_extras", staticmethod(lambda *a: {})), \
            patch.object(EarthEngineService, "_sar_stats", staticmethod(lambda *a: None)):
        return svc._field_ndvi(polygon_field(PLOT), date(2026, 3, 1)), ee_mock


def test_polygon_ndvi_uses_the_fields_own_pixel_count_and_reports_quality():
    res, ee_mock = _polygon_result({"current": _win(0.62, 90), "previous": _win(0.5, 80), "roi_px": 100, "landcover": CROPLAND,
                                    "baseline_1": _win(0.6, 90), "baseline_2": _win(0.65, 95)})
    assert res["status"] == "available" and res["ndvi"] == 0.62 and res["change"] == 0.12
    assert res["roi"] == {"mode": "polygon", "area_ha": 1.0, "pixel_count": 100}  # no coordinates echoed
    q = res["quality"]
    assert (q["mode"], q["level"], q["pixel_count"], q["clear_pixel_count"], q["clear_pixel_fraction"]) == ("polygon", "good", 100, 90, 0.9)
    assert q["valid_pixel_fraction"] == 1.0 and q["land_cover"]["cropland_fraction"] == 0.9 and q["flags"] == []
    assert res["baseline"]["status"] == "available"
    assert ee_mock.Dictionary.return_value.getInfo.call_count == 1  # one round trip


def test_polygon_with_few_clear_pixels_is_insufficient_data_not_a_number():
    res, _ = _polygon_result({"current": _win(0.8, 20), "previous": _win(0.5, 90), "roi_px": 100, "landcover": CROPLAND})
    assert res["status"] == "insufficient_data" and res["reason"] == "too_few_clear_pixels" and "ndvi" not in res
    assert res["quality"]["level"] == "insufficient" and "too_few_clear_pixels" in res["quality"]["flags"]


def test_fully_cloudy_polygon_is_no_data():
    res, _ = _polygon_result({"current": _win(None, 0), "previous": _win(0.5, 90), "roi_px": 100, "landcover": CROPLAND})
    assert res["status"] == "no_data" and res["reason"] == "no_suitable_observation" and "ndvi" not in res


def test_polygon_below_ten_pixels_is_too_small_for_sentinel2():
    res, _ = _polygon_result({"current": _win(0.7, 6), "previous": _win(0.6, 6), "roi_px": 6, "landcover": CROPLAND}, sar_available=True)
    assert res["status"] == "insufficient_data" and res["reason"] == "field_too_small" and "ndvi" not in res
    assert res["sar"]["status"] == "insufficient_data" and res["baseline"]["status"] == "insufficient_data"


def test_mixed_land_cover_is_flagged_and_limits_quality():
    res, _ = _polygon_result({"current": _win(0.4, 90), "previous": _win(0.4, 90), "roi_px": 100,
                              "landcover": {"40": 30.0, "80": 40.0, "10": 30.0}})
    q = res["quality"]
    assert res["status"] == "available" and q["level"] == "limited"
    assert {"mixed_land_cover", "contains_water", "contains_trees"} <= set(q["flags"])


def test_missing_land_cover_is_explicitly_unavailable():
    res, _ = _polygon_result({"current": _win(0.6, 90), "previous": _win(0.6, 90), "roi_px": 100})
    assert res["quality"]["land_cover"]["status"] == "unavailable"


def test_point_mode_is_flagged_as_not_a_field_boundary():
    svc = EarthEngineService.__new__(EarthEngineService)
    svc.sar_available = False
    ee_mock = MagicMock()
    ee_mock.Dictionary.return_value.getInfo.return_value = {"current": _win(0.6, 1963), "previous": _win(0.6, 1963)}
    with patch.object(ees, "ee", ee_mock, create=True), patch.object(EarthEngineService, "_window_stats", staticmethod(lambda *a: None)), \
            patch.object(EarthEngineService, "_field_extras", staticmethod(lambda *a: {})):
        res = svc._point_ndvi(LAT, LNG, date(2026, 3, 1))
    assert res["quality"]["mode"] == "point" and "point_circle_not_field_boundary" in res["quality"]["flags"]
    assert res["quality"]["level"] == "limited"


def test_cache_keys_hash_polygons_and_too_large_fields_are_refused():
    key = polygon_field(PLOT)["key"]
    assert key[0] == "plot" and all("73.8" not in str(k) for k in key)
    assert point_field(LAT, LNG)["key"] == ("point", LAT, LNG)
    with pytest.raises(ValueError):
        polygon_field({"geometry": PLOT["geometry"], "area_ha": 500})


@pytest.mark.asyncio
async def test_polygon_query_failure_is_unavailable_never_fabricated():
    svc = EarthEngineService.__new__(EarthEngineService)
    svc.initialized, svc.status, svc.error = True, "available", None
    svc.ensure_initialized = lambda: True
    ees._point_cache.clear()
    with patch.object(EarthEngineService, "_field_ndvi", side_effect=Exception("Image.reduceRegion: Too many pixels")):
        res = await svc.get_plot_crop_health(PLOT)
    assert res["status"] == "unavailable" and res["reason"] == "dataset_query_failed" and "ndvi" not in res
    assert res["roi"] == {"mode": "polygon"}


@pytest.mark.asyncio
async def test_browser_preflight_allows_plot_edit_and_remove():
    from config import settings
    origin = settings.CORS_ALLOWED_ORIGINS.split(",")[0].strip()
    async with api() as c:
        for method in ("PUT", "DELETE"):
            res = await c.options("/api/farms/x/plot", headers={"Origin": origin, "Access-Control-Request-Method": method,
                                                                 "Access-Control-Request-Headers": "x-farm-token,content-type"})
            assert res.status_code == 200 and method in res.headers["access-control-allow-methods"]


@pytest.mark.asyncio
async def test_polygon_failures_never_log_the_geometry(caplog):
    import logging
    caplog.set_level(logging.ERROR, logger="services.earth_engine_service")
    logging.getLogger("services.earth_engine_service").disabled = False  # alembic's fileConfig disables loggers in tests
    svc = EarthEngineService.__new__(EarthEngineService)
    svc.initialized, svc.status, svc.error = True, "available", None
    svc.ensure_initialized = lambda: True
    ees._point_cache.clear()
    ring = PLOT["geometry"]["coordinates"][0]
    with patch.object(EarthEngineService, "_field_ndvi", side_effect=Exception(f"Geometry {ring} is invalid")):
        await svc.get_plot_crop_health(PLOT)
    assert str(ring[0][0]) not in caplog.text and "Exception" in caplog.text


@pytest.mark.asyncio
async def test_saved_plot_never_reaches_public_interoperability_or_dashboards():
    import jwt as pyjwt
    from config import settings
    secret = "plot-privacy-secret-with-32-bytes!!"
    geometry = square(100)
    async with api() as c:
        farm_id, h = await create(c)
        assert (await c.put(f"/api/farms/{farm_id}/plot", headers=h, json={"geometry": geometry})).status_code == 200
        token = {"Authorization": "Bearer " + pyjwt.encode({"sub": "p", "role": "partner"}, secret, algorithm="HS256")}
        with patch.object(settings, "JWT_SECRET", secret), \
                patch("services.interop.brazil.pam_observations", AsyncMock(return_value=[])):
            bodies = [(await c.get(path, headers=token)).text for path in (
                "/api/interoperability/agricultural-observations?country=IN", "/api/interoperability/risk-signals?country=IN",
                "/api/interoperability/compare", "/api/dashboard/evaluation", "/api/dashboard/feedback-metrics",
                "/api/dashboard/early-warning", "/api/dashboard/stats")]
    corner = f"{validate_polygon(geometry)['geometry']['coordinates'][0][0][0]}"
    for body in bodies:
        assert corner not in body and farm_id not in body and '"geometry"' not in body

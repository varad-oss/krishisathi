"""Weather parsing, agro rules, soil parsing and regenerative recommendations."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from helpers import open_meteo_payload
from main import app
from models.exceptions import ServiceUnavailableException
from services import agro_rules, soil_service as soil_module, weather_service as ws
from services.regenerative_service import recommend
from services.soil_service import parse_soilgrids, rate_organic_carbon, rate_ph

client = TestClient(app)


def conditions(**daily):
    return ws.parse_conditions(open_meteo_payload(**daily), 18.5, 73.8)


# --- Weather contract -----------------------------------------------------------

def test_weather_request_uses_valid_forecast_variables():
    """Regression: soil_moisture_0_to_7cm is not a forecast-API variable and broke live weather."""
    assert "soil_moisture_0_to_7cm" not in ws.CURRENT_VARS
    assert {"soil_moisture_0_to_1cm", "soil_moisture_3_to_9cm"} <= set(ws.CURRENT_VARS)


def test_current_values_come_from_current_block_not_midnight_hourly():
    c = conditions()
    assert c["current"]["temperature_c"] == 29.4
    assert c["current"]["humidity_pct"] == 64
    assert c["current"]["valid_at"] == "2026-09-26T10:15"
    assert c["provenance"]["kind"] == "model"
    assert "not ground-station observations" in c["provenance"]["notes"]


def test_missing_current_temperature_is_an_error():
    payload = open_meteo_payload()
    del payload["current"]["temperature_2m"]
    with pytest.raises(ServiceUnavailableException):
        ws.parse_conditions(payload, 1, 1)


def test_missing_optional_fields_become_null_not_invented():
    payload = open_meteo_payload()
    del payload["daily"]["et0_fao_evapotranspiration"]
    c = ws.parse_conditions(payload, 1, 1)
    assert all(d["et0_mm"] is None for d in c["daily"])


@pytest.mark.asyncio
async def test_conditions_are_cached():
    ws._cache.clear()
    resp = MagicMock()
    resp.json.return_value = open_meteo_payload()
    resp.raise_for_status.return_value = None
    with patch("services.weather_service.httpx.AsyncClient.get", AsyncMock(return_value=resp)) as get:
        await ws.weather_service.get_conditions(18.5, 73.8)
        await ws.weather_service.get_conditions(18.501, 73.801)
    assert get.call_count == 1
    ws._cache.clear()


# --- Agro rules -----------------------------------------------------------------

def ids(c):
    return {i["id"]: i for i in agro_rules.evaluate(c)}


def test_rain_expected_advises_delaying_irrigation():
    found = ids(conditions())
    assert found["rain_expected"]["params"]["precipitation_mm"] == 12.0
    assert found["rain_expected"]["basis"]["kind"] == "forecast"


def test_heavy_rain_uses_imd_threshold():
    found = ids(conditions(precipitation_sum=[0, 70.0, 0, 0, 0, 0, 0]))
    assert found["heavy_rain"]["severity"] == "warning"
    assert "IMD" in found["heavy_rain"]["basis"]["source"]["name"]
    assert "rain_expected" not in found


def test_heat_levels():
    assert ids(conditions(temperature_2m_max=[41, 30, 30, 30, 30, 30, 30]))["heat_stress"]["severity"] == "watch"
    assert ids(conditions(temperature_2m_max=[46, 30, 30, 30, 30, 30, 30]))["heat_stress"]["severity"] == "warning"
    assert "heat_stress" not in ids(conditions())


def test_fungal_risk_requires_humidity_and_moderate_temperature():
    assert "fungal_risk" in ids(conditions())  # day 2: 88 % RH, mean 25.5 °C
    assert "fungal_risk" not in ids(conditions(relative_humidity_2m_mean=[60] * 7))


def test_dry_spell():
    found = ids(conditions(precipitation_sum=[0] * 7, et0_fao_evapotranspiration=[5] * 7))
    assert found["dry_spell"]["params"]["et0_total_mm"] == 35
    assert "dry_spell" not in ids(conditions(precipitation_sum=[0] * 7, et0_fao_evapotranspiration=[None] * 7))


def test_no_alerts_from_missing_data():
    payload = open_meteo_payload()
    payload["daily"] = {"time": payload["daily"]["time"]}
    payload["current"]["wind_speed_10m"] = None
    assert agro_rules.evaluate(ws.parse_conditions(payload, 1, 1)) == []


def test_insights_sorted_by_severity():
    found = agro_rules.evaluate(conditions(temperature_2m_max=[46, 30, 30, 30, 30, 30, 30]))
    assert found[0]["severity"] == "warning"


def test_farm_conditions_endpoint_includes_insights():
    with patch.object(ws.weather_service, "get_conditions", AsyncMock(return_value=conditions())):
        res = client.get("/api/farm/conditions?lat=18.5&lng=73.8")
    assert res.status_code == 200
    body = res.json()
    assert body["insights"] and body["provenance"]["source"] == "Open-Meteo"


# --- Soil -----------------------------------------------------------------------

SOILGRIDS = {"properties": {"layers": [
    {"name": "phh2o", "unit_measure": {"d_factor": 10}, "depths": [{"label": "0-5cm", "values": {"mean": 78}}, {"label": "5-15cm", "values": {"mean": 81}}]},
    {"name": "soc", "unit_measure": {"d_factor": 10}, "depths": [{"label": "0-5cm", "values": {"mean": 60}}, {"label": "5-15cm", "values": {"mean": 39}}]},
    {"name": "nitrogen", "unit_measure": {"d_factor": 100}, "depths": [{"label": "0-5cm", "values": {"mean": 90}}, {"label": "5-15cm", "values": {"mean": 60}}]},
    {"name": "clay", "unit_measure": {"d_factor": 10}, "depths": [{"label": "0-5cm", "values": {"mean": 420}}, {"label": "5-15cm", "values": {"mean": 450}}]},
    {"name": "sand", "unit_measure": {"d_factor": 10}, "depths": [{"label": "0-5cm", "values": {"mean": 250}}, {"label": "5-15cm", "values": {"mean": 240}}]},
]}}


def test_soilgrids_parsing_applies_d_factor_and_depth_weighting():
    soil = parse_soilgrids(SOILGRIDS)
    p = soil["properties"]
    assert p["ph"] == 8.0            # (7.8*5 + 8.1*10) / 15
    assert p["organic_carbon_pct"] == 0.46  # SOC 4.6 g/kg -> 0.46 %
    assert p["clay_pct"] == 44.0
    assert soil["ratings"] == {"ph": "alkaline", "organic_carbon": "low", "source": soil["ratings"]["source"]}


def test_soilgrids_no_data_pixels():
    empty = {"properties": {"layers": [{"name": "phh2o", "unit_measure": {"d_factor": 10}, "depths": [{"label": "0-5cm", "values": {"mean": None}}]}]}}
    assert parse_soilgrids(empty) == {"status": "no_data"}


def test_soil_health_card_ratings():
    assert rate_organic_carbon(0.4) == "low" and rate_organic_carbon(0.6) == "medium" and rate_organic_carbon(0.9) == "high"
    assert rate_ph(5.0) == "strongly_acidic" and rate_ph(7.0) == "neutral" and rate_ph(9.0) == "strongly_alkaline"


# --- Regenerative ----------------------------------------------------------------

def test_regenerative_triggers_are_explained():
    soil = {"status": "available", **parse_soilgrids(SOILGRIDS)}
    recs = recommend("Wheat", soil, [{"id": "dry_spell"}])
    by_id = {r["id"]: r for r in recs}
    assert by_id["organic_matter"]["priority"] == "high"
    assert by_id["organic_matter"]["triggers"][0] == {"signal": "soil_organic_carbon", "value": 0.46, "rating": "low"}
    assert by_id["water_conservation"]["priority"] == "high"
    assert "residue_retention" in by_id and "legume_rotation" in by_id
    assert recs[0]["priority"] == "high"


def test_regenerative_without_soil_data_recommends_testing_first():
    recs = recommend(None, {"status": "unavailable"}, [])
    assert recs[0]["id"] == "soil_test" and recs[0]["priority"] == "high"
    organic = next(r for r in recs if r["id"] == "organic_matter")
    assert organic["triggers"] == [{"signal": "soil_data", "value": None, "rating": "unavailable"}]
    assert not any(r["id"] == "ph_management" for r in recs)  # never inferred without soil data


def test_regenerative_endpoint_reports_inputs():
    soil_module._cache.clear()
    with patch.object(soil_module.soil_service, "get_soil", AsyncMock(return_value={"status": "unavailable"})), \
         patch.object(ws.weather_service, "get_conditions", AsyncMock(side_effect=ServiceUnavailableException("x"))):
        res = client.get("/api/farm/regenerative?lat=18.5&lng=73.8&crop=paddy")
    body = res.json()
    assert body["crop"] == "Rice"
    assert body["inputs"] == {"soil": "unavailable", "weather": "unavailable", "crop": "provided"}

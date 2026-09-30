"""Sentinel-2 / Earth Engine: credential handling, honest status reporting and NDVI result shaping.

Earth Engine is mocked everywhere except the last test, which queries real Sentinel-2 data and runs
only when EE_SERVICE_ACCOUNT_KEY_JSON is set.
"""
import asyncio
import base64
import json
import os
import sys
import threading
from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import services.earth_engine_service as ees  # noqa: E402
from main import app  # noqa: E402
from google.auth.exceptions import RefreshError  # noqa: E402
from services.earth_engine_service import CredentialError, EarthEngineService, classify_error, parse_service_account_key  # noqa: E402

KEY = {
    "type": "service_account",
    "project_id": "krishisathi-ee",
    "private_key": "-----BEGIN PRIVATE KEY-----\nabc\n-----END PRIVATE KEY-----\n",
    "client_email": "ndvi@krishisathi-ee.iam.gserviceaccount.com",
}
client = TestClient(app)


# --- credentials ---------------------------------------------------------------------------

def test_key_accepted_raw_or_base64():
    raw = json.dumps(KEY)
    assert parse_service_account_key(raw)["client_email"] == KEY["client_email"]
    assert parse_service_account_key(base64.b64encode(raw.encode()).decode())["project_id"] == "krishisathi-ee"


def test_escaped_newlines_in_private_key_are_repaired():
    pasted = json.dumps({**KEY, "private_key": KEY["private_key"].replace("\n", "\\n")})
    assert parse_service_account_key(pasted)["private_key"] == KEY["private_key"]


@pytest.mark.parametrize("raw, code", [
    ("not base64 or json!", "invalid_key_encoding"),
    ("{not json", "invalid_key_json"),
    (json.dumps({**KEY, "type": "authorized_user"}), "not_a_service_account_key"),
    (json.dumps({k: v for k, v in KEY.items() if k != "private_key"}), "key_missing_fields"),
    (json.dumps({**KEY, "project_id": ""}), "key_missing_fields"),
])
def test_unusable_keys_are_rejected_with_a_code(raw, code):
    with pytest.raises(CredentialError) as err:
        parse_service_account_key(raw)
    assert err.value.code == code


def _service(key_json, ee_mock=None, project=None):
    ee_mock = ee_mock or MagicMock()
    with patch.object(ees, "EE_AVAILABLE", True), patch.object(ees, "ee", ee_mock, create=True), \
            patch.object(ees.settings, "EE_SERVICE_ACCOUNT_KEY_JSON", key_json), patch.object(ees.settings, "EE_PROJECT", project):
        return EarthEngineService(), ee_mock


def _state(svc):
    return svc.configured, svc.authenticated, svc.initialized, svc.status, svc.error


def test_missing_key_is_not_configured():
    svc, ee_mock = _service(None)
    assert _state(svc) == (False, False, False, "not_configured", None)
    ee_mock.Initialize.assert_not_called()


def test_project_without_key_uses_application_default_credentials():
    svc, ee_mock = _service(None, project="registered-ee-project")
    assert _state(svc) == (True, True, True, "available", None)
    ee_mock.ServiceAccountCredentials.assert_not_called()
    ee_mock.Initialize.assert_called_once_with(project="registered-ee-project")
    ee_mock.Number.return_value.getInfo.assert_called_once()  # ADC is verified like a key, never assumed


def test_rejected_application_default_credentials_are_unavailable():
    ee_mock = MagicMock()
    ee_mock.Number.return_value.getInfo.side_effect = RefreshError("Reauthentication is needed")
    svc, _ = _service(None, ee_mock, project="registered-ee-project")
    assert _state(svc) == (True, False, False, "unavailable", "auth_failed")


def test_bad_key_is_unavailable_not_a_silent_not_set_up():
    svc, ee_mock = _service("{broken")
    assert _state(svc) == (True, False, False, "unavailable", "invalid_key_json")
    ee_mock.Initialize.assert_not_called()


def test_valid_key_initializes_and_verifies_account_and_dataset_with_real_requests():
    svc, ee_mock = _service(json.dumps(KEY))
    assert _state(svc) == (True, True, True, "available", None)
    assert svc.project == "krishisathi-ee" and svc.checked_at
    ee_mock.ServiceAccountCredentials.assert_called_once()
    assert ee_mock.Initialize.call_args.kwargs["project"] == "krishisathi-ee"
    ee_mock.Number.return_value.getInfo.assert_called_once()  # proves account + project, not just parsing
    # proves the datasets are readable: Sentinel-2 (required) and Sentinel-1 (optional radar)
    assert [c.args[0] for c in ee_mock.data.getAsset.call_args_list] == ["COPERNICUS/S2_SR_HARMONIZED", "COPERNICUS/S1_GRD"]
    assert svc.sar_available is True
    ee_mock.data.setDeadline.assert_called_once_with(ees.TIMEOUT_S * 1000)


def test_dataset_not_readable_is_authenticated_but_unavailable():
    ee_mock = MagicMock()
    ee_mock.data.getAsset.side_effect = Exception("Asset 'COPERNICUS/S2_SR_HARMONIZED' not found.")
    svc, _ = _service(json.dumps(KEY), ee_mock)
    assert _state(svc) == (True, True, False, "unavailable", "dataset_query_failed")
    assert svc.describe()["project"] == "krishisathi-ee"


@pytest.mark.parametrize("exc, code", [
    (RefreshError("invalid_grant: Invalid grant: account not found"), "auth_failed"),
    (Exception("Not signed up for Earth Engine or project is not registered."), "project_configuration_error"),
    (Exception("Earth Engine API has not been used in project 123 before or it is disabled."), "project_configuration_error"),
    (Exception("Caller does not have required permission to use project x."), "project_configuration_error"),
    (TimeoutError("The read operation timed out"), "timeout"),
    (Exception("Computation timed out."), "timeout"),
    (ConnectionError("Connection reset by peer"), "earth_engine_unavailable"),
    (Exception("The service is currently unavailable."), "earth_engine_unavailable"),
])
def test_initialization_failures_are_classified(exc, code):
    ee_mock = MagicMock()
    ee_mock.Number.return_value.getInfo.side_effect = exc
    svc, _ = _service(json.dumps(KEY), ee_mock)
    assert _state(svc) == (True, False, False, "unavailable", code)


def test_unknown_query_failure_is_a_dataset_query_failure():
    assert classify_error(Exception("Image.select: band B8 not found"), "dataset_query_failed") == "dataset_query_failed"


def test_ee_project_overrides_the_keys_project():
    svc, ee_mock = _service(json.dumps(KEY), project="registered-ee-project")
    assert ee_mock.Initialize.call_args.kwargs["project"] == "registered-ee-project"


def test_rejected_credentials_are_reported_and_retried_later():
    ee_mock = MagicMock()
    ee_mock.Number.return_value.getInfo.side_effect = RefreshError("invalid_grant (secret-detail)")
    svc, _ = _service(json.dumps(KEY), ee_mock)
    assert _state(svc) == (True, False, False, "unavailable", "auth_failed")
    assert "secret" not in json.dumps(svc.describe())

    ee_mock.Number.return_value.getInfo.side_effect = None
    with patch.object(ees, "EE_AVAILABLE", True), patch.object(ees, "ee", ee_mock, create=True), \
            patch.object(ees.settings, "EE_SERVICE_ACCOUNT_KEY_JSON", json.dumps(KEY)), patch.object(ees.settings, "EE_PROJECT", None):
        assert svc.ensure_initialized() is False  # no retry before the cool-down
        ee_mock.Initialize.reset_mock()
        assert svc.ensure_initialized() is False
        ee_mock.Initialize.assert_not_called()
        svc._next_attempt = 0
        assert svc.ensure_initialized() is True
    assert svc.status == "available"


def test_unfixable_key_errors_are_not_retried():
    svc, ee_mock = _service("{broken")
    svc._next_attempt = 0
    with patch.object(ees, "ee", ee_mock, create=True):
        assert svc.ensure_initialized() is False
    ee_mock.Initialize.assert_not_called()


def test_crop_health_reason_distinguishes_missing_from_broken_configuration():
    svc, _ = _service("{broken")
    body = asyncio.run(svc.get_point_crop_health(18.5, 73.8))
    assert body["status"] == "unavailable" and body["reason"] == "invalid_key_json" and "ndvi" not in body
    svc, _ = _service(None)
    assert asyncio.run(svc.get_point_crop_health(18.5, 73.8))["reason"] == "not_configured"


def _sources_and_ready(status, error, initialized=False):
    svc = ees.earth_engine_service
    with patch.object(svc, "initialized", initialized), patch.object(svc, "status", status), patch.object(svc, "error", error):
        return {s["id"]: s for s in client.get("/api/sources").json()["sources"]}["satellite"], client.get("/health/ready").json()


def test_sources_and_readiness_expose_the_precise_state():
    sat, ready = _sources_and_ready("unavailable", "auth_failed")
    assert (sat["status"], sat["detail"]) == ("unavailable", "auth_failed")
    assert ready["dependencies"]["earth_engine"] == "unavailable:auth_failed"
    assert ready["ready"] or ready["dependencies"]["database"] != "ok"  # optional: never blocks readiness

    sat, ready = _sources_and_ready("not_configured", None)
    assert (sat["status"], sat["detail"]) == ("not_configured", None)
    assert ready["dependencies"]["earth_engine"] == "not_configured"

    sat, ready = _sources_and_ready("available", None, initialized=True)
    assert (sat["status"], sat["detail"]) == ("configured", None)  # shown as "Enabled"
    assert ready["dependencies"]["earth_engine"] == "available"
    assert (sat["dataset"], sat["provider"]) == ("COPERNICUS/S2_SR_HARMONIZED", "Copernicus / ESA")
    assert "Level-2A" in sat["processing"]


def test_invalid_coordinates_are_rejected():
    for query in ("lat=91&lng=75", "lat=30&lng=181", "lat=abc&lng=75"):
        res = client.get(f"/api/farm/crop-health?{query}")
        assert res.status_code == 422 and res.json()["error"]["code"] == "INVALID_INPUT"
    with pytest.raises(ValueError):
        asyncio.run(EarthEngineService.__new__(EarthEngineService).get_point_crop_health(95, 75))


# --- NDVI result shaping (Earth Engine responses mocked) ----------------------------------

def _point_result(info):
    svc = EarthEngineService.__new__(EarthEngineService)
    ee_mock = MagicMock()
    ee_mock.Dictionary.return_value.getInfo.return_value = info
    with patch.object(ees, "ee", ee_mock, create=True), patch.object(EarthEngineService, "_window_stats", staticmethod(lambda *a: None)):
        return svc._point_ndvi(30.9, 75.85, date(2026, 3, 1)), ee_mock


FULL = 1963  # clear 10 m pixels in a fully clear 250 m circle
SCENE = {"latest_id": ["20260227T053901_20260227T054440_T43REQ"], "latest_cloud_pct": [12.345]}


def test_ndvi_available_with_change_acquisition_date_and_observation_metadata():
    res, ee_mock = _point_result({"current": {"ndvi": 0.71234, "clear_px": FULL, "count": 5, "latest_ms": 1772150400000, **SCENE},
                                  "previous": {"ndvi": 0.60111, "clear_px": 1500, "count": 4, "latest_ms": 1769558400000}})
    assert res["status"] == "available"
    assert (res["ndvi"], res["ndvi_previous"], res["change"]) == (0.712, 0.601, 0.111)
    assert res["image_count"] == 5 and res["latest_image_date"] == "2026-02-27"
    assert res["window"] == {"start": "2026-01-30", "end": "2026-03-01"}
    assert res["clear_pixel_fraction"] == 1.0
    assert res["observation"] == {"image_id": "COPERNICUS/S2_SR_HARMONIZED/20260227T053901_20260227T054440_T43REQ",
                                  "sensed_at": "2026-02-27T00:00:00+00:00", "scene_cloud_pct": 12.3}
    assert res["roi"] == {"lat": 30.9, "lng": 75.85, "radius_m": 250, "mode": "point"}
    assert ee_mock.Dictionary.return_value.getInfo.call_count == 1  # both windows in one round trip


def test_ndvi_without_previous_window_has_no_change():
    res, _ = _point_result({"current": {"ndvi": 0.5, "clear_px": FULL, "count": 2, "latest_ms": 1772150400000, **SCENE},
                            "previous": {"ndvi": None, "clear_px": 0, "count": 0, "latest_ms": None}})
    assert res["status"] == "available" and res["ndvi_previous"] is None and res["change"] is None


def test_cloudy_month_is_no_suitable_observation_not_a_number():
    res, _ = _point_result({"current": {"ndvi": None, "clear_px": 0, "count": 3, "latest_ms": 1772150400000, **SCENE},
                            "previous": {"ndvi": 0.4, "clear_px": FULL, "count": 2, "latest_ms": 1769558400000}})
    assert res["status"] == "no_data" and res["reason"] == "no_suitable_observation" and "ndvi" not in res
    assert res["observation"]["image_id"].endswith("T43REQ")  # the scene exists, but was cloudy over the field


def test_few_clear_pixels_are_not_reported_as_the_field():
    res, _ = _point_result({"current": {"ndvi": 0.8, "clear_px": 50, "count": 3, "latest_ms": 1772150400000, **SCENE},
                            "previous": {"ndvi": 0.4, "clear_px": 60, "count": 2, "latest_ms": 1769558400000}})
    assert res["status"] == "no_data" and res["clear_pixel_fraction"] == 0.03 and "ndvi" not in res


def test_no_imagery_at_all():
    res, _ = _point_result({"current": {"ndvi": None, "clear_px": 0, "count": 0, "latest_ms": None, "latest_id": [], "latest_cloud_pct": []},
                            "previous": {"ndvi": None, "clear_px": 0, "count": 0, "latest_ms": None}})
    assert res["status"] == "no_data" and res["image_count"] == 0 and res["observation"] is None


def _ready_service():
    svc = EarthEngineService.__new__(EarthEngineService)
    svc.initialized, svc.status, svc.error, svc._lock = True, "available", None, threading.Lock()
    return svc


@pytest.mark.parametrize("exc, reason, retryable", [
    (Exception("Image.reduceRegion: quota exceeded xyz"), "dataset_query_failed", False),
    (asyncio.TimeoutError(), "timeout", True),
    (Exception("The service is currently unavailable. xyz"), "earth_engine_unavailable", True),
])
def test_query_failure_is_unavailable_with_a_code_and_provenance(exc, reason, retryable):
    svc = _ready_service()
    with patch.object(EarthEngineService, "_point_ndvi", side_effect=exc):
        body = asyncio.run(svc.get_point_crop_health(30.9, 75.85))
    assert (body["status"], body["reason"], body["retryable"]) == ("unavailable", reason, retryable)
    assert "xyz" not in json.dumps(body) and body["provenance"]["dataset"] == "COPERNICUS/S2_SR_HARMONIZED"
    assert svc.status == "available"  # a transient or query failure does not flip the source status


def test_key_revoked_after_startup_flips_the_source_to_unavailable():
    svc = _ready_service()
    with patch.object(EarthEngineService, "_point_ndvi", side_effect=RefreshError("invalid_grant")):
        body = asyncio.run(svc.get_point_crop_health(30.9, 75.85))
    assert body["reason"] == "auth_failed" and (svc.initialized, svc.status, svc.error) == (False, "unavailable", "auth_failed")


def test_provenance_labels_ndvi_as_a_satellite_signal_not_ground_truth():
    assert ees.PROVENANCE["signal"].startswith("Satellite-derived vegetation signal")
    assert "not ground-truth" in ees.PROVENANCE["signal"]
    assert ees.PROVENANCE["provider"] == "Copernicus / ESA"


# --- live Sentinel-2 query --------------------------------------------------------------------

@pytest.mark.skipif(not os.getenv("EE_SERVICE_ACCOUNT_KEY_JSON"), reason="set EE_SERVICE_ACCOUNT_KEY_JSON to query real Sentinel-2 data")
def test_live_sentinel2_ndvi_for_a_ludhiana_wheat_field():
    svc = EarthEngineService()
    assert svc.status == "available", svc.describe()
    body = asyncio.run(svc.get_point_crop_health(30.90, 75.85))
    assert body["status"] in ("available", "no_data"), body
    if body["status"] == "available":
        assert -1.0 <= body["ndvi"] <= 1.0
        assert body["image_count"] >= 1 and body["latest_image_date"] <= date.today().isoformat()
        assert body["observation"]["image_id"].startswith("COPERNICUS/S2_SR_HARMONIZED/")


# --- Temporal baseline, history series and Sentinel-1 radar ------------------------------------

def _point_with(info, sar_available=True):
    svc = EarthEngineService.__new__(EarthEngineService)
    svc.sar_available = sar_available
    ee_mock = MagicMock()
    ee_mock.Dictionary.return_value.getInfo.return_value = info
    with patch.object(ees, "ee", ee_mock, create=True), patch.object(EarthEngineService, "_window_stats", staticmethod(lambda *a: None)), \
            patch.object(EarthEngineService, "_sar_stats", staticmethod(lambda *a: None)):
        return svc._point_ndvi(30.9, 75.85, date(2026, 3, 1))


def _win(ndvi, px=FULL):
    return {"ndvi": ndvi, "clear_px": px, "count": 3, "latest_ms": 1772150400000, **SCENE}


def _pass(vv, vh, count=2):
    return {"vv_db": vv, "vh_db": vh, "count": count, "latest_ms": 1772150400000}


def test_baseline_compares_with_the_same_weeks_of_previous_years():
    res = _point_with({"current": _win(0.41), "previous": _win(0.55),
                       "baseline_1": _win(0.62), "baseline_2": _win(0.58), "baseline_3": _win(None, 0)})
    b = res["baseline"]
    assert b["status"] == "available" and (b["min"], b["max"], b["mean"]) == (0.58, 0.62, 0.6)
    assert b["position"] == "below_range"
    assert [y["year"] for y in b["years"]] == [2025, 2024, 2023] and b["years"][2]["ndvi"] is None  # cloudy year stays null


def test_baseline_needs_two_usable_years():
    res = _point_with({"current": _win(0.41), "previous": _win(0.55), "baseline_1": _win(0.62), "baseline_2": _win(0.7, 10)})
    assert res["baseline"]["status"] == "insufficient_data" and "position" not in res["baseline"]


def test_radar_is_reported_even_when_clouds_hide_the_field():
    res = _point_with({"current": _win(None, 0), "previous": _win(0.5),
                       "sar_current": {"ASCENDING": _pass(-9.0, -19.5), "DESCENDING": _pass(None, None, 0)},
                       "sar_previous": {"ASCENDING": _pass(-8.0, -15.0), "DESCENDING": _pass(None, None, 0)}})
    assert res["status"] == "no_data" and "ndvi" not in res
    sar = res["sar"]
    assert sar["status"] == "available" and sar["orbit_pass"] == "ASCENDING"
    assert (sar["vh_db"], sar["vh_db_previous"], sar["vh_change_db"]) == (-19.5, -15.0, -4.5)
    assert sar["water_signal"] is True  # -19.5 / -15.0 = 1.3 > 1.25 (UN-SPIDER)
    assert sar["provenance"]["dataset"] == "COPERNICUS/S1_GRD" and "not a measurement" in sar["provenance"]["signal"]


def test_radar_compares_only_the_same_orbit_direction():
    res = _point_with({"current": _win(0.5), "previous": _win(0.5),
                       "sar_current": {"ASCENDING": _pass(-9, -16), "DESCENDING": _pass(-10, -18)},
                       "sar_previous": {"ASCENDING": _pass(None, None, 0), "DESCENDING": _pass(-10, -17)}})
    assert res["sar"]["orbit_pass"] == "DESCENDING" and res["sar"]["water_signal"] is False


def test_radar_without_a_previous_pass_has_no_change_and_no_water_claim():
    res = _point_with({"current": _win(0.5), "previous": _win(0.5),
                       "sar_current": {"ASCENDING": _pass(-9, -16), "DESCENDING": _pass(None, None, 0)},
                       "sar_previous": {"ASCENDING": _pass(None, None, 0), "DESCENDING": _pass(None, None, 0)}})
    assert res["sar"]["vh_change_db"] is None and res["sar"]["water_signal"] is None


def test_no_radar_scene_and_radar_dataset_unavailable():
    empty = {"ASCENDING": _pass(None, None, 0), "DESCENDING": _pass(None, None, 0)}
    assert _point_with({"current": _win(0.5), "previous": _win(0.5), "sar_current": empty, "sar_previous": empty})["sar"]["reason"] == "no_radar_scene"
    res = _point_with({"current": _win(0.5), "previous": _win(0.5)}, sar_available=False)
    assert res["status"] == "available" and res["sar"]["reason"] == "radar_dataset_unavailable"


def test_radar_dataset_failure_does_not_disable_sentinel2():
    ee_mock = MagicMock()

    def get_asset(asset):
        if asset == "COPERNICUS/S1_GRD":
            raise Exception("permission denied")
        return {}

    ee_mock.data.getAsset.side_effect = get_asset
    svc, _ = _service(json.dumps(KEY), ee_mock)
    assert svc.status == "available" and svc.initialized and svc.sar_available is False


def test_history_series_keeps_gaps_as_null():
    svc = EarthEngineService.__new__(EarthEngineService)
    ee_mock = MagicMock()
    ee_mock.Dictionary.return_value.getInfo.return_value = {"0": _win(0.6), "1": _win(None, 0), "2": _win(0.55), "3": _win(0.4, 20),
                                                            "4": _win(0.3), "5": {}}
    with patch.object(ees, "ee", ee_mock, create=True), patch.object(EarthEngineService, "_window_stats", staticmethod(lambda *a: None)):
        res = svc._point_series(30.9, 75.85, date(2026, 3, 1))
    assert [p["ndvi"] for p in res["series"]] == [None, 0.3, None, 0.55, None, 0.6]  # oldest first; cloudy windows stay null
    assert res["series"][-1]["end"] == "2026-03-01" and res["usable_windows"] == 3 and res["status"] == "available"
    assert ee_mock.Dictionary.return_value.getInfo.call_count == 1

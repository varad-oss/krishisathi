"""Sentinel-2 / Earth Engine: credential handling, honest status reporting and NDVI result shaping.

The last test queries real Sentinel-2 data and runs only when EE_SERVICE_ACCOUNT_KEY_JSON is set.
"""
import asyncio
import base64
import json
import os
import sys
from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import services.earth_engine_service as ees  # noqa: E402
from main import app  # noqa: E402
from services.earth_engine_service import CredentialError, EarthEngineService, parse_service_account_key  # noqa: E402

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


def test_missing_key_is_not_configured():
    svc, ee_mock = _service(None)
    assert (svc.initialized, svc.status, svc.error) == (False, "not_configured", None)
    ee_mock.Initialize.assert_not_called()


def test_bad_key_is_an_error_not_a_silent_not_set_up():
    svc, ee_mock = _service("{broken")
    assert (svc.initialized, svc.status, svc.error) == (False, "error", "invalid_key_json")
    ee_mock.Initialize.assert_not_called()


def test_valid_key_initializes_and_verifies_with_a_real_request():
    svc, ee_mock = _service(json.dumps(KEY))
    assert (svc.initialized, svc.status, svc.project) == (True, "configured", "krishisathi-ee")
    ee_mock.ServiceAccountCredentials.assert_called_once()
    assert ee_mock.Initialize.call_args.kwargs["project"] == "krishisathi-ee"
    ee_mock.Number.return_value.getInfo.assert_called_once()  # proves account + project, not just parsing


def test_ee_project_overrides_the_keys_project():
    svc, ee_mock = _service(json.dumps(KEY), project="registered-ee-project")
    assert ee_mock.Initialize.call_args.kwargs["project"] == "registered-ee-project"


def test_rejected_credentials_are_reported_and_retried_later():
    ee_mock = MagicMock()
    ee_mock.Number.return_value.getInfo.side_effect = Exception("Caller does not have permission (secret-detail)")
    svc, _ = _service(json.dumps(KEY), ee_mock)
    assert (svc.initialized, svc.status, svc.error) == (False, "error", "authentication_failed")
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
    assert svc.status == "configured"


def test_crop_health_reason_distinguishes_missing_from_broken_configuration():
    svc, _ = _service("{broken")
    body = asyncio.run(svc.get_point_crop_health(18.5, 73.8))
    assert body["status"] == "unavailable" and body["reason"] == "configuration_error" and "ndvi" not in body


def test_sources_and_readiness_expose_the_precise_state():
    with patch.object(ees.earth_engine_service, "initialized", False), \
            patch.object(ees.earth_engine_service, "status", "error"), \
            patch.object(ees.earth_engine_service, "error", "authentication_failed"):
        sources = {s["id"]: s for s in client.get("/api/sources").json()["sources"]}
        ready = client.get("/health/ready").json()
    assert sources["satellite"]["status"] == "not_configured"
    assert sources["satellite"]["detail"] == "authentication_failed"
    assert ready["dependencies"]["earth_engine"] == "error:authentication_failed"


# --- NDVI result shaping (Earth Engine responses mocked) ----------------------------------

def _point_result(info):
    svc = EarthEngineService.__new__(EarthEngineService)
    ee_mock = MagicMock()
    ee_mock.Dictionary.return_value.getInfo.return_value = info
    with patch.object(ees, "ee", ee_mock, create=True), patch.object(EarthEngineService, "_window_stats", staticmethod(lambda *a: None)):
        return svc._point_ndvi(30.9, 75.85, date(2026, 3, 1)), ee_mock


def test_ndvi_available_with_change_and_acquisition_date():
    res, ee_mock = _point_result({"current": {"ndvi": 0.71234, "count": 5, "latest_ms": 1772150400000},
                                  "previous": {"ndvi": 0.60111, "count": 4, "latest_ms": 1769558400000}})
    assert res["status"] == "available"
    assert (res["ndvi"], res["ndvi_previous"], res["change"]) == (0.712, 0.601, 0.111)
    assert res["image_count"] == 5 and res["latest_image_date"] == "2026-02-27"
    assert res["window"] == {"start": "2026-01-30", "end": "2026-03-01"}
    assert ee_mock.Dictionary.return_value.getInfo.call_count == 1  # both windows in one round trip


def test_ndvi_without_previous_window_has_no_change():
    res, _ = _point_result({"current": {"ndvi": 0.5, "count": 2, "latest_ms": 1772150400000},
                            "previous": {"ndvi": None, "count": 0, "latest_ms": None}})
    assert res["status"] == "available" and res["ndvi_previous"] is None and res["change"] is None


def test_cloudy_month_is_no_data_not_a_number():
    res, _ = _point_result({"current": {"ndvi": None, "count": 3, "latest_ms": 1772150400000},
                            "previous": {"ndvi": 0.4, "count": 2, "latest_ms": 1769558400000}})
    assert res["status"] == "no_data" and res["reason"] == "no_clear_imagery" and "ndvi" not in res


def test_upstream_failure_is_unavailable_with_provenance():
    svc = EarthEngineService.__new__(EarthEngineService)
    svc.initialized, svc.status, svc.error = True, "configured", None
    with patch.object(EarthEngineService, "_point_ndvi", side_effect=Exception("quota exceeded xyz")):
        body = asyncio.run(svc.get_point_crop_health(30.9, 75.85))
    assert body["status"] == "unavailable" and body["reason"] == "upstream_error"
    assert "xyz" not in json.dumps(body) and body["provenance"]["kind"] == "satellite_observation"


# --- live Sentinel-2 query --------------------------------------------------------------------

@pytest.mark.skipif(not os.getenv("EE_SERVICE_ACCOUNT_KEY_JSON"), reason="set EE_SERVICE_ACCOUNT_KEY_JSON to query real Sentinel-2 data")
def test_live_sentinel2_ndvi_for_a_ludhiana_wheat_field():
    svc = EarthEngineService()
    assert svc.status == "configured", svc.describe()
    body = asyncio.run(svc.get_point_crop_health(30.90, 75.85))
    assert body["status"] in ("available", "no_data"), body
    if body["status"] == "available":
        assert -1.0 <= body["ndvi"] <= 1.0
        assert body["image_count"] >= 1 and body["latest_image_date"] <= date.today().isoformat()

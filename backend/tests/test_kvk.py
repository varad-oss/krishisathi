"""KVK lookup: never report a distance to a district reference point as a distance to the KVK."""
import helpers  # noqa: F401  (puts the backend on sys.path)
from fastapi.testclient import TestClient

from main import app
from services.kvk_service import MATCH_RADIUS_KM, KvkService, haversine_km, kvk_service

client = TestClient(app)


def test_haversine_known_distance():
    # Delhi to Mumbai is about 1148 km.
    assert 1140 < haversine_km(28.6139, 77.2090, 19.0760, 72.8777) < 1160


def test_haversine_zero_and_symmetry():
    assert haversine_km(18.52, 73.856, 18.52, 73.856) == 0
    a = haversine_km(18.52, 73.856, 19.997, 73.789)
    b = haversine_km(19.997, 73.789, 18.52, 73.856)
    assert abs(a - b) < 1e-9
    assert 160 < a < 170  # Pune to Nashik, ~164 km


def test_swapped_coordinates_do_not_match():
    # (lng, lat) instead of (lat, lng) lands in the Arctic: must not resolve to a KVK.
    assert kvk_service.get_nearest_kvk(73.856, 18.52) is None


def test_district_reference_point_gives_no_distance():
    # The bundled list stores district HQ points. Querying the exact Pune HQ point used to report "0 km".
    k = kvk_service.get_nearest_kvk(18.520, 73.856)
    assert k["name"] == "KVK Pune"
    assert k["match"] == "district"
    assert k["distance_km"] is None
    assert k["lat"] is None and k["lng"] is None


def test_different_locations_match_different_districts():
    assert kvk_service.get_nearest_kvk(19.9, 73.8)["district"] == "Nashik"
    assert kvk_service.get_nearest_kvk(21.1, 79.0)["district"] == "Nagpur"


def test_location_outside_coverage_returns_none():
    # Patna, Bihar: no listed district within the match radius.
    assert kvk_service.get_nearest_kvk(25.594, 85.137) is None


def test_verified_site_reports_rounded_distance():
    svc = KvkService([{"name": "KVK Test", "district": "X", "state": "MH", "lat": 18.60, "lng": 73.90, "location_basis": "site"}])
    k = svc.get_nearest_kvk(18.52, 73.856)
    assert k["match"] == "site"
    assert k["distance_km"] == round(haversine_km(18.52, 73.856, 18.60, 73.90), 1)
    assert 9 < k["distance_km"] < 11


def test_radius_boundary():
    svc = KvkService([{"name": "KVK A", "district": "A", "state": "MH", "lat": 0.0, "lng": 0.0}])
    one_degree_km = haversine_km(0, 0, 1, 0)
    inside = (MATCH_RADIUS_KM - 1) / one_degree_km
    outside = (MATCH_RADIUS_KM + 1) / one_degree_km
    assert svc.get_nearest_kvk(inside, 0) is not None
    assert svc.get_nearest_kvk(outside, 0) is None


def test_empty_list_returns_none():
    assert KvkService([]).get_nearest_kvk(18.5, 73.8) is None


def test_endpoint_match_and_not_found():
    ok = client.get("/api/kvk/nearest?lat=18.52&lng=73.856")
    assert ok.status_code == 200
    body = ok.json()
    assert body["distance_km"] is None and body["match"] == "district"
    assert body["provenance"]["verify_url"].startswith("https://kvk.icar.gov.in")

    missing = client.get("/api/kvk/nearest?lat=25.594&lng=85.137")
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "NOT_FOUND"

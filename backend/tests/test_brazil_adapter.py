"""Brazil adapter (IBGE PAM via SIDRA) and India/Brazil cross-country schema validation.

The SIDRA payloads below follow the API's JSON layout (first row = header labels, then one row per cell). Their
numbers are TEST VALUES, not IBGE data; real data only ever comes from the live API.
"""
import asyncio
import json
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, patch

import httpx
import jwt
import pytest
from fastapi.testclient import TestClient

from config import settings
from core import rate_limit
from main import app
from models.interop_v1 import SCHEMAS, CropV1, ObservationV1, PageV1
from services.interop import brazil
from services.interop.adapter import CountryAdapter, SourceUnavailable, UnsupportedCategory
from services.interop.brazil import BrazilAdapter, parse_pam, product_crop
from services.interop.india import IndiaAdapter

client = TestClient(app)
SECRET = "brazil-test-secret-with-32-bytes!!!"

HEADER = {"NC": "Nível Territorial (Código)", "NN": "Nível Territorial", "MC": "Unidade de Medida (Código)", "MN": "Unidade de Medida",
          "V": "Valor", "D1C": "Unidade da Federação (Código)", "D1N": "Unidade da Federação", "D2C": "Variável (Código)", "D2N": "Variável",
          "D3C": "Ano (Código)", "D3N": "Ano", "D4C": "Produto das lavouras temporárias e permanentes (Código)",
          "D4N": "Produto das lavouras temporárias e permanentes"}


def row(uf, uf_name, var, var_name, unit, value, product, year="2024"):
    return {"NC": "3", "NN": "Unidade da Federação", "MC": "0", "MN": unit, "V": value, "D1C": uf, "D1N": uf_name, "D2C": var,
            "D2N": var_name, "D3C": year, "D3N": year, "D4C": "0", "D4N": product}


PAYLOAD = [
    HEADER,
    row("51", "Mato Grosso", "216", "Área colhida", "Hectares", "1000", "Soja (em grão)"),
    row("51", "Mato Grosso", "214", "Quantidade produzida", "Toneladas", "3500", "Soja (em grão)"),
    row("51", "Mato Grosso", "112", "Rendimento médio da produção", "Quilogramas por Hectare", "3500", "Soja (em grão)"),
    row("41", "Paraná", "214", "Quantidade produzida", "Toneladas", "...", "Soja (em grão)"),       # not available: omitted
    row("41", "Paraná", "214", "Quantidade produzida", "Toneladas", "X", "Milho (em grão)"),        # confidential: omitted
    row("41", "Paraná", "214", "Quantidade produzida", "Toneladas", "-", "Trigo (em grão)"),        # zero: omitted, not invented
    row("35", "São Paulo", "214", "Quantidade produzida", "Toneladas", "20", "Café (em grão) Arábica"),  # counted via the total only
    row("35", "São Paulo", "214", "Quantidade produzida", "Toneladas", "25", "Café (em grão) Total"),
    row("35", "São Paulo", "214", "Quantidade produzida", "Mil frutos", "9", "Coco-da-baía"),        # unmapped product and unit
    row("35", "São Paulo", "214", "Área colhida", "Toneladas", "7", "Milho (em grão)"),              # code/name mismatch: dropped
    row("99", "Nowhere", "214", "Quantidade produzida", "Toneladas", "5", "Milho (em grão)"),        # unknown state: dropped
]
NOW = datetime(2026, 9, 30, tzinfo=timezone.utc)


def auth(role="partner"):
    return {"Authorization": "Bearer " + jwt.encode({"sub": "partner-in", "role": role}, SECRET, algorithm="HS256")}


@pytest.fixture(autouse=True)
def reset():
    rate_limit._local_windows.clear()
    brazil._cache.clear()
    with patch.object(settings, "JWT_SECRET", SECRET):
        yield
    brazil._cache.clear()


def sidra(payload=PAYLOAD, status=200):
    """Patches the HTTP call to SIDRA only; everything after it is the real adapter code."""
    async def get(self, url, params=None):
        assert url == brazil.SIDRA_URL and params == {"formato": "json"}
        return httpx.Response(status, json=payload, request=httpx.Request("GET", url))
    return patch.object(httpx.AsyncClient, "get", get)


# --- parsing and normalization ----------------------------------------------------------------------

def test_pam_rows_become_v1_observations_with_full_provenance():
    obs = parse_pam(PAYLOAD, NOW)
    assert {(o.geo.region_code, o.crop_code, o.variable, o.value, o.unit) for o in obs} == {
        ("BR-MT", "soybean", "harvested_area", 1000.0, "ha"), ("BR-MT", "soybean", "production", 3500.0, "t"),
        ("BR-MT", "soybean", "yield", 3500.0, "kg/ha"), ("BR-SP", "coffee", "production", 25.0, "t")}
    o = next(o for o in obs if o.variable == "yield")
    assert o.observation_type == "production_statistic" and o.geo.basis == "region" and o.geo.grid is None
    assert (o.period.start, o.period.end) == (date(2024, 1, 1), date(2024, 12, 31))
    assert o.subject == "Soja (em grão)" and o.confidence is None and o.sample_size is None
    p = o.provenance
    assert p.kind == "official_statistic" and p.source.startswith("IBGE") and p.url == "https://sidra.ibge.gov.br/tabela/5457"
    assert p.retrieved_at == NOW and "112" in p.method and "Rendimento" in p.method and "not a farm" in p.notes


def test_special_symbols_are_never_turned_into_numbers():
    assert not any(o.geo.region_code == "BR-PR" for o in parse_pam(PAYLOAD, NOW))


def test_dimension_order_is_read_from_the_header_not_assumed():
    swapped = {**HEADER, "D2C": "Ano (Código)", "D2N": "Ano", "D3C": "Variável (Código)", "D3N": "Variável"}
    rows = [{**r, "D2C": r["D3C"], "D2N": r["D3N"], "D3C": r["D2C"], "D3N": r["D2N"]} for r in PAYLOAD[1:]]
    assert {o.model_dump_json() for o in parse_pam([swapped, *rows], NOW)} == {o.model_dump_json() for o in parse_pam(PAYLOAD, NOW)}


@pytest.mark.parametrize("payload", [{}, [], [{"foo": "bar"}], [{"D1C": "Something else (Código)"}]])
def test_unexpected_format_is_unavailable(payload):
    with pytest.raises(SourceUnavailable):
        parse_pam(payload, NOW)


def test_product_mapping():
    assert product_crop("Soja (em grão)")[0] == "soybean" and product_crop("Algodão herbáceo (em caroço)")[0] == "cotton"
    assert product_crop("Cana-de-açúcar")[0] == "sugarcane" and product_crop("Café (em grão) Canephora") is None
    assert product_crop("Coco-da-baía") is None


# --- adapter contract --------------------------------------------------------------------------------

def test_brazil_adapter_implements_the_same_contract_without_changing_it():
    br = BrazilAdapter()
    assert isinstance(br, CountryAdapter)
    info = br.describe()
    assert info["categories"] == {"crops": "available", "observations": "available", "diseases": "unsupported",
                                  "weather_signals": "unsupported", "risk_signals": "unsupported"}
    assert info["sources"][0]["kind"] == "official_statistic" and info["identified_not_integrated"] and info["limitations"]
    assert len(info["coverage"]["states"]) == 27 and "BR-DF" in info["coverage"]["states"]
    crops = asyncio.run(br.crops())
    assert all(isinstance(c, CropV1) for c in crops) and {"soybean", "maize", "rice"} <= {c.crop_code for c in crops}


@pytest.mark.parametrize("call", ["diseases", "weather_signals"])
def test_unsupported_categories_raise_instead_of_returning_placeholders(call):
    with pytest.raises(UnsupportedCategory):
        asyncio.run(getattr(BrazilAdapter(), call)())
    with pytest.raises(UnsupportedCategory):
        asyncio.run(BrazilAdapter().risk_signals(date(2026, 1, 1)))


@pytest.mark.asyncio
async def test_unreachable_sidra_is_unavailable_and_not_cached():
    with sidra(status=500):
        with pytest.raises(SourceUnavailable):
            await BrazilAdapter().observations(date(2026, 1, 1))
    assert "pam" not in brazil._cache
    with sidra():
        assert len(await BrazilAdapter().observations(date(2026, 1, 1))) == 4
    assert "pam" in brazil._cache


@pytest.mark.asyncio
async def test_concurrent_requests_share_one_sidra_call():
    calls = []

    async def get(self, url, params=None):
        calls.append(url)
        await asyncio.sleep(0.01)
        return httpx.Response(200, json=PAYLOAD, request=httpx.Request("GET", url))
    with patch.object(httpx.AsyncClient, "get", get):
        results = await asyncio.gather(*(BrazilAdapter().observations(date(2026, 1, 1)) for _ in range(5)))
    assert len(calls) == 1 and all(len(r) == 4 for r in results)


# --- API ------------------------------------------------------------------------------------------------

def test_brazil_observations_through_the_api_validate_against_v1():
    with sidra():
        body = client.get("/api/interoperability/agricultural-observations", params={"country": "BR", "limit": 2}, headers=auth()).json()
        rest = client.get("/api/interoperability/agricultural-observations",
                          params={"country": "BR", "limit": 2, "cursor": body["next_cursor"]}, headers=auth()).json()
    assert body["country_code"] == "BR" and body["status"] == "available" and body["count"] == 2 and body["next_cursor"]
    assert rest["count"] == 2 and rest["next_cursor"] is None
    for item in body["items"] + rest["items"]:
        ObservationV1.model_validate(item)
        assert item["geo"]["country_code"] == "BR" and item["provenance"]["retrieved_at"]


def test_brazil_source_outage_is_a_503_not_an_empty_page():
    with sidra(status=503):
        res = client.get("/api/interoperability/agricultural-observations", params={"country": "BR"}, headers=auth())
    assert res.status_code == 503 and res.json()["error"]["code"] == "SOURCE_UNAVAILABLE"


@pytest.mark.parametrize("path", ["diseases", "weather-signals", "risk-signals"])
def test_brazil_unsupported_categories_are_explicit(path):
    res = client.get(f"/api/interoperability/{path}", params={"country": "BR"}, headers=auth())
    body = res.json()
    assert res.status_code == 200 and body["status"] == "unsupported" and body["count"] == 0 and body["items"] == []
    assert body["notes"]


def test_india_pages_say_available():
    body = client.get("/api/interoperability/crops", params={"country": "IN"}).json()
    assert body["status"] == "available"


# --- cross-country schema validation --------------------------------------------------------------------

PRIVATE_KEYS = {"farm_id", "farm_token", "token", "token_hash", "phone", "email", "farmer_name", "farmer", "geometry", "coordinates", "lat_exact"}


def _keys(value):
    if isinstance(value, dict):
        for k, v in value.items():
            yield k
            yield from _keys(v)
    elif isinstance(value, list):
        for v in value:
            yield from _keys(v)


def test_compare_shows_india_and_brazil_through_the_same_contract():
    with sidra():
        res = client.get("/api/interoperability/compare", params={"crop": "soybean"})
    assert res.status_code == 200
    body = res.json()
    by = {c["country_code"]: c for c in body["countries"]}
    assert set(by) >= {"IN", "BR"} and "not directly comparable" in body["notes"]
    assert by["IN"]["categories"]["observations"] == "available" and by["IN"]["samples"]["observations"] == {"status": "partner_only"}
    assert by["BR"]["categories"]["risk_signals"] == "unsupported" and by["BR"]["samples"].get("risk_signals") is None
    br_obs = by["BR"]["samples"]["observations"]
    assert br_obs["status"] == "available" and br_obs["matching_crop"] == 3
    for item in br_obs["items"]:
        ObservationV1.model_validate(item)
    for country in ("IN", "BR"):
        for crop in by[country]["samples"]["crops"]["items"]:
            CropV1.model_validate(crop)
        assert by[country]["samples"]["crops"]["items"][0]["crop_code"] == "soybean"  # same code in both catalogues
    assert not PRIVATE_KEYS & set(_keys(body))


def test_compare_reports_an_unavailable_brazil_source_without_inventing_samples():
    with sidra(status=500):
        body = client.get("/api/interoperability/compare").json()
    br = next(c for c in body["countries"] if c["country_code"] == "BR")
    assert br["samples"]["observations"] == {"status": "unavailable", "reason": "ibge_sidra_unavailable"}


@pytest.mark.parametrize("adapter", [IndiaAdapter(), BrazilAdapter()])
def test_both_adapters_emit_valid_country_codes_and_provenance(adapter):
    with sidra(), patch("services.interop.india.persistence_service.detection_rows", AsyncMock(return_value=[])):
        obs = asyncio.run(adapter.observations(date(2026, 7, 1)))
        crops = asyncio.run(adapter.crops())
    for o in obs:
        assert o.geo.country_code == adapter.country_code and o.provenance.kind and o.provenance.source
        assert o.geo.region_code is None or o.geo.region_code.startswith(adapter.country_code + "-")
        assert o.geo.grid is None or o.geo.grid.cell_deg >= 0.5  # never a farm-level point
    assert crops and all(c.crop_code for c in crops)
    PageV1[ObservationV1](country_code=adapter.country_code, generated_at=NOW, count=len(obs), items=obs)


def test_unknown_fields_are_rejected_for_every_shape():
    for name, model in SCHEMAS.items():
        assert model.model_json_schema().get("additionalProperties") is False, name


def test_production_statistic_is_part_of_the_published_schema():
    schema = client.get("/api/interoperability/schemas").json()["schemas"]["Observation"]
    assert "production_statistic" in json.dumps(schema)

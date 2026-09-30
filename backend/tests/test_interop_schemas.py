"""Interoperability schema v1.0 and the India country adapter (no HTTP)."""
import asyncio
from datetime import date

import pytest
from pydantic import ValidationError

from models.interop_v1 import GeoRefV1, ObservationV1, PeriodV1, ProvenanceV1, json_schemas
from services.interop.adapter import CountryAdapter
from services.interop.india import IndiaAdapter, cell, crop_code


def _obs(**over):
    base = dict(observation_type="disease_observation", geo=GeoRefV1(country_code="BR", region_code="BR-MT", basis="region"),
                period=PeriodV1(start=date(2026, 9, 1), end=date(2026, 9, 30)), variable="detections", value=4, unit="count",
                provenance=ProvenanceV1(source="x", kind="ai_classified_reports"))
    base.update(over)
    return ObservationV1(**base)


def test_schemas_are_country_neutral_and_reject_personal_fields():
    assert _obs().geo.country_code == "BR"  # not tied to India
    with pytest.raises(ValidationError):
        _obs(farmer_name="Ramesh")  # unknown fields are refused, so PII cannot ride along
    with pytest.raises(ValidationError):
        GeoRefV1(country_code="India")
    with pytest.raises(ValidationError):
        ProvenanceV1(source="x", kind="guess")  # every value must say what kind of statement it is


def test_json_schemas_are_generated_for_every_shape():
    schemas = json_schemas()
    assert schemas["RiskSignal"]["properties"]["schema_version"]["const"] == "1.0"
    assert schemas["Observation"]["additionalProperties"] is False


def test_india_adapter_implements_the_contract():
    india = IndiaAdapter()
    assert isinstance(india, CountryAdapter)
    info = india.describe()
    assert info["country_code"] == "IN" and "IN-MH" in info["coverage"]["states"] and info["limitations"]
    crops = asyncio.run(india.crops())
    assert len(crops) == 16 and all(c.crop_code == c.crop_code.lower() for c in crops)


def test_codes_and_grid_cells():
    assert crop_code("Pigeon pea") == "pigeon_pea" and crop_code("paddy") == "rice" and crop_code("unknown crop") is None
    c = cell(-0.2, -73.6)  # works south of the equator and west of Greenwich
    assert (c.lat, c.lng) == (-0.5, -74.0)

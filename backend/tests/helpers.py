"""Shared test fixtures/data (imported by test modules; pytest puts this directory on sys.path)."""
import io
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PIL import Image

# A confident, located disease detection: eligible for outbreak clustering.
RUST = {"disease_name": "Rust", "diagnosis_status": "disease_detected", "certainty": "high", "severity": "moderate"}


def jpeg_bytes(size=(128, 128), color=(40, 140, 60)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="JPEG")
    return buf.getvalue()


def ai_diagnosis(**overrides) -> dict:
    data = {
        "diagnosis_status": "disease_detected",
        "image_quality": "good",
        "certainty": "high",
        "certainty_reason": "Yellow-orange pustules in stripes are characteristic of stripe rust.",
        "disease_name": "Stripe rust",
        "disease_name_en": "Stripe rust",
        "scientific_name": "Puccinia striiformis",
        "reference_id": "wheat-rust",
        "affected_part": "Leaves",
        "observed_symptoms": ["Yellow stripes of pustules on leaves"],
        "alternative_causes": ["Leaf rust"],
        "severity": "moderate",
        "spread_risk": "high",
        "urgency": "soon",
        "treatment": {"immediate": ["Inspect nearby plants"], "organic": [], "chemical": ["Propiconazole 25 EC"], "prevention": ["Use resistant varieties"]},
        "summary": "Likely stripe rust.",
    }
    data.update(overrides)
    return data


def open_meteo_payload(**daily_overrides) -> dict:
    daily = {
        "time": ["2026-09-26", "2026-09-27", "2026-09-28", "2026-09-29", "2026-09-30", "2026-10-01", "2026-10-02"],
        "weather_code": [1, 61, 3, 0, 0, 1, 2],
        "temperature_2m_max": [32.0, 30.0, 31.0, 33.0, 33.5, 34.0, 33.0],
        "temperature_2m_min": [22.0, 21.0, 21.5, 22.0, 22.0, 23.0, 22.5],
        "precipitation_sum": [0.0, 12.0, 1.0, 0.0, 0.0, 0.0, 0.0],
        "precipitation_probability_max": [10, 80, 30, 5, 5, 5, 10],
        "et0_fao_evapotranspiration": [4.1, 3.0, 3.8, 4.5, 4.6, 4.7, 4.5],
        "relative_humidity_2m_mean": [60, 88, 70, 55, 50, 50, 52],
        "wind_speed_10m_max": [12, 18, 10, 9, 9, 10, 11],
    }
    daily.update(daily_overrides)
    return {
        "timezone": "Asia/Kolkata",
        "elevation": 560.0,
        "current": {
            "time": "2026-09-26T10:15",
            "temperature_2m": 29.4,
            "relative_humidity_2m": 64,
            "precipitation": 0.0,
            "weather_code": 1,
            "wind_speed_10m": 8.5,
            "soil_moisture_0_to_1cm": 0.21,
            "soil_moisture_3_to_9cm": 0.27,
        },
        "daily": daily,
    }

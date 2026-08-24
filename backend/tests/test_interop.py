import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from models.interop import strip_pii, RegionalAgriSignal, StateConfig
from datetime import datetime

def test_strip_pii():
    dirty_metadata = {
        "farmer_name": "Ramesh Kumar",
        "phone_number": "+91-9876543210",
        "crop_yield": 45,
        "village": "Palampur",
        "notes": "Farmer called to report pest"
    }
    
    clean_metadata = strip_pii(dirty_metadata)
    
    assert "farmer_name" not in clean_metadata
    assert "phone_number" not in clean_metadata
    assert "notes" not in clean_metadata
    assert "village" not in clean_metadata
    assert "crop_yield" in clean_metadata
    assert clean_metadata["crop_yield"] == 45

def test_regional_agri_signal_creation():
    signal = RegionalAgriSignal(
        from_state="MH",
        to_state="KA",
        signal_type="pest_advisory",
        severity="high",
        message="Test message",
        disease_name="Test Disease",
        affected_crop="Test Crop",
        affected_district="Test District",
        report_count=10,
        timestamp=datetime.utcnow()
    )
    assert signal.from_state == "MH"
    assert signal.severity == "high"

def test_state_config_creation():
    config = StateConfig(
        code="PB",
        name="Punjab",
        capital="Chandigarh",
        lat=31.1471,
        lng=75.3412,
        default_language="pa",
        primary_crops=["Wheat", "Rice"],
        districts=23,
        arable_land_mha=4.2,
        farmers_reached=2000000,
        active_alerts=2,
        top_crop="Wheat"
    )
    assert config.code == "PB"
    assert len(config.primary_crops) == 2

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services.disease_reference_service import disease_reference_service
from config import settings

def test_disease_reference_data_loads():
    # 1. disease_reference.json loads successfully
    assert len(disease_reference_service.data) > 0

def test_disease_reference_schema():
    # 2. dataset contains at least the expected required schema
    for item in disease_reference_service.data:
        assert 'id' in item
        assert 'name' in item
        assert 'crops' in item
        assert 'symptoms' in item
        assert 'treatment' in item
        assert 'sources' in item

def test_crop_lookup():
    # 3. crop lookup returns matching entries
    context = disease_reference_service.get_grounding_context(crop_type="Wheat", state_code="")
    assert "Wheat Rust" in context
    assert "General Disease Reference Data:" in context

def test_unknown_crop():
    # 4. unknown crop returns no matching reference
    context = disease_reference_service.get_grounding_context(crop_type="Dragonfruit", state_code="")
    assert "No specific regional disease reference data found" in context

def test_state_parameter_behavior():
    # 5. state parameter behavior is correct
    context_pb = disease_reference_service.get_grounding_context(crop_type="Wheat", state_code="PB")
    assert "Wheat Rust" in context_pb
    assert "Regional Disease Reference Data:" in context_pb
    assert "ICAR-Indian Institute of Wheat and Barley Research" in context_pb

def test_model_configuration():
    # 6. Gemini model configuration resolves to a valid configured value
    assert settings.GEMINI_DIAGNOSIS_MODEL is not None
    assert settings.GEMINI_ADVISORY_MODEL is not None
    
def test_model_configuration_override(monkeypatch):
    # 7. model configuration can be overridden through environment settings
    monkeypatch.setenv("GEMINI_DIAGNOSIS_MODEL", "gemini-3.8-flash-test")
    
    # Reload settings
    from config import Settings
    new_settings = Settings()
    assert new_settings.GEMINI_DIAGNOSIS_MODEL == "gemini-3.8-flash-test"

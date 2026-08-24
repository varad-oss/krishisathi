import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services.disease_reference_service import disease_reference_service

def test_get_grounding_context():
    context = disease_reference_service.get_grounding_context(crop_type="Wheat", state_code="PB")
    
    assert context is not None
    assert isinstance(context, str)

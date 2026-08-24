import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from services.kvk_service import kvk_service

def test_haversine_nearest():
    # Delhi approx coordinates
    delhi_lat = 28.6139
    delhi_lng = 77.2090
    
    nearest = kvk_service.get_nearest_kvk(delhi_lat, delhi_lng)
    
    # We should get a KVK returned if the static list is loaded
    assert nearest is not None
    assert "name" in nearest
    assert "distance_km" in nearest
    assert nearest["distance_km"] >= 0

def test_haversine_distance_calc():
    dist = kvk_service._haversine(28.6139, 77.2090, 19.0760, 72.8777) # Delhi to Mumbai
    assert 1100 < dist < 1200 # Approx 1148 km

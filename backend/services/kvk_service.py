import json
import math
import os
import logging

logger = logging.getLogger(__name__)

class KvkService:
    def __init__(self):
        self.locations = []
        try:
            data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'kvk_locations.json')
            with open(data_path, 'r', encoding='utf-8') as f:
                self.locations = json.load(f)
            logger.info(f"Loaded {len(self.locations)} KVK locations.")
        except Exception as e:
            logger.error(f"Failed to load kvk_locations.json: {e}")

    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 6371.0 # Earth radius in kilometers
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dLon / 2) * math.sin(dLon / 2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def get_nearest_kvk(self, lat: float, lng: float) -> dict:
        if not self.locations:
            return {}

        nearest = None
        min_dist = float('inf')
        
        for loc in self.locations:
            dist = self._haversine(lat, lng, loc['lat'], loc['lng'])
            if dist < min_dist:
                min_dist = dist
                nearest = loc
                
        if nearest:
            result = dict(nearest)
            result['distance_km'] = round(min_dist, 2)
            return result
        return {}

kvk_service = KvkService()

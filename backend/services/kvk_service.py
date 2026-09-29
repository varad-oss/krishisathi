"""Krishi Vigyan Kendra lookup from a small static reference list.

The bundled records carry *district reference points* (district headquarters), not
the coordinates of the KVK campus. A distance to such a point is not a distance to
the KVK, so a match is reported as "the KVK for this district" and `distance_km`
is only filled for records whose coordinates are the verified KVK site
(`"location_basis": "site"`). Locations far from every listed district return no
match instead of a far-away, misleading "nearest" KVK.
"""
import json
import logging
import math
import os

logger = logging.getLogger(__name__)

# A point farther than this from every listed district reference point is treated
# as outside the list's coverage (typical Indian district radius is 30–60 km).
MATCH_RADIUS_KM = 60.0

KVK_PROVENANCE = {
    "source": "KrishiSathi KVK list (subset)",
    "kind": "static_reference",
    "notes": "Covers a limited set of districts. Matched by the nearest district headquarters; the KVK address is not verified. Check the official KVK portal.",
    "verify_url": "https://kvk.icar.gov.in/",
}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometres (spherical Earth, R = 6371 km)."""
    r = 6371.0
    d_lat, d_lon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class KvkService:
    def __init__(self, locations: list[dict] | None = None):
        if locations is not None:
            self.locations = locations
            return
        self.locations = []
        try:
            data_path = os.path.join(os.path.dirname(__file__), "..", "data", "kvk_locations.json")
            with open(data_path, "r", encoding="utf-8") as f:
                self.locations = json.load(f)
            logger.info("Loaded %d KVK records.", len(self.locations))
        except Exception as e:
            logger.error("Failed to load kvk_locations.json: %s", e)

    def get_nearest_kvk(self, lat: float, lng: float) -> dict | None:
        """KVK for the district nearest to (lat, lng), or None when no listed district is within MATCH_RADIUS_KM."""
        best, best_dist = None, math.inf
        for loc in self.locations:
            dist = haversine_km(lat, lng, loc["lat"], loc["lng"])
            if dist < best_dist:
                best, best_dist = loc, dist
        if best is None or best_dist > MATCH_RADIUS_KM:
            return None

        verified_site = best.get("location_basis") == "site"
        return {
            "name": best["name"],
            "district": best.get("district"),
            "state": best.get("state"),
            "match": "site" if verified_site else "district",
            # Only a verified campus location gives a meaningful travel distance.
            "distance_km": round(best_dist, 1) if verified_site else None,
            "lat": best["lat"] if verified_site else None,
            "lng": best["lng"] if verified_site else None,
        }


kvk_service = KvkService()

"""Field plots: an optional polygon the farmer draws around their field.

A plot is a GeoJSON Polygon (RFC 7946: [lng, lat] positions, closed exterior ring). Holes and multi-polygons
are not accepted: a smallholder field is one simple shape, and a simple shape keeps the satellite statistics
easy to reason about. Validation is strict because the geometry drives Earth Engine queries.

The exact geometry is private to the farm: it is returned only to the farm-token holder and never enters
the public interoperability API, logs or cache keys (the cache key is a hash of the coordinates).
"""
import hashlib
import json
import math

EARTH_RADIUS_M = 6_371_008.8
COORD_DECIMALS = 6            # ~0.1 m; finer digits are GPS noise
MIN_VERTICES = 3              # distinct corners
MAX_VERTICES = 200
MIN_AREA_HA = 0.01            # one Sentinel-2 pixel is 0.01 ha; smaller shapes cannot be observed at all
MAX_AREA_HA = 200.0           # larger than any smallholding; also bounds Earth Engine work (20 000 pixels at 10 m)
MAX_DISTANCE_FROM_FARM_KM = 5.0


class PlotError(ValueError):
    """Invalid plot geometry. `code` is safe to show to the client."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def _number(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _project(ring: list[list[float]]) -> list[tuple[float, float]]:
    """Local equirectangular projection in metres around the ring's mean latitude (error well under 1% for fields)."""
    lat0 = math.radians(sum(p[1] for p in ring) / len(ring))
    return [(math.radians(p[0]) * EARTH_RADIUS_M * math.cos(lat0), math.radians(p[1]) * EARTH_RADIUS_M) for p in ring]


def area_ha(ring: list[list[float]]) -> float:
    """Shoelace area of a closed [lng, lat] ring, in hectares."""
    xy = _project(ring)
    twice = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(xy, xy[1:]))
    return abs(twice) / 2 / 10_000


def centroid(ring: list[list[float]]) -> tuple[float, float]:
    """(lat, lng) vertex mean; good enough to check the plot is near the farm."""
    pts = ring[:-1]
    return sum(p[1] for p in pts) / len(pts), sum(p[0] for p in pts) / len(pts)


def _cross(o, a, b) -> float:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _segments_cross(p1, p2, p3, p4) -> bool:
    d1, d2, d3, d4 = _cross(p3, p4, p1), _cross(p3, p4, p2), _cross(p1, p2, p3), _cross(p1, p2, p4)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)) and 0 not in (d1, d2, d3, d4):
        return True
    return False


def _self_intersects(ring: list[list[float]]) -> bool:
    xy = _project(ring)
    edges = list(zip(xy, xy[1:]))
    n = len(edges)
    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue  # first and last edge share the closing vertex
            if _segments_cross(*edges[i], *edges[j]):
                return True
    return False


def haversine_km(lat1, lng1, lat2, lng2) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lng2 - lng1) / 2) ** 2
    return 2 * EARTH_RADIUS_M / 1000 * math.asin(math.sqrt(a))


def validate_polygon(geometry, farm_lat: float | None = None, farm_lng: float | None = None) -> dict:
    """Returns a canonical GeoJSON Polygon with its area, or raises PlotError."""
    if not isinstance(geometry, dict) or geometry.get("type") != "Polygon":
        raise PlotError("invalid_geometry", "Geometry must be a GeoJSON Polygon.")
    extra = set(geometry) - {"type", "coordinates"}
    if extra:
        raise PlotError("invalid_geometry", "Unexpected GeoJSON members: " + ", ".join(sorted(extra)))
    rings = geometry.get("coordinates")
    if not isinstance(rings, list) or not rings:
        raise PlotError("empty_polygon", "The polygon has no coordinates.")
    if len(rings) != 1:
        raise PlotError("holes_not_supported", "Draw the field as one outline without holes.")
    ring = rings[0]
    if not isinstance(ring, list) or any(not isinstance(p, list) or len(p) != 2 or not all(_number(v) for v in p) for p in ring):
        raise PlotError("invalid_geometry", "Each position must be [longitude, latitude].")
    if any(not (-180 <= p[0] <= 180 and -90 <= p[1] <= 90) for p in ring):
        raise PlotError("out_of_bounds", "Coordinates are outside the valid longitude/latitude range.")
    ring = [[round(p[0], COORD_DECIMALS), round(p[1], COORD_DECIMALS)] for p in ring]
    if len(ring) >= 2 and ring[0] == ring[-1]:
        ring = ring[:-1]
    # Consecutive duplicates (double taps) are dropped rather than rejected.
    ring = [p for i, p in enumerate(ring) if i == 0 or p != ring[i - 1]]
    if len({tuple(p) for p in ring}) < MIN_VERTICES:
        raise PlotError("empty_polygon", f"A field needs at least {MIN_VERTICES} distinct corners.")
    if len(ring) > MAX_VERTICES:
        raise PlotError("too_many_vertices", f"Use at most {MAX_VERTICES} corners.")
    if len({tuple(p) for p in ring}) != len(ring):
        raise PlotError("self_intersecting", "The outline visits the same corner twice.")
    ring = ring + [ring[0]]
    if _self_intersects(ring):
        raise PlotError("self_intersecting", "The outline crosses itself.")
    area = area_ha(ring)
    if area < MIN_AREA_HA:
        raise PlotError("area_too_small", f"The field must be at least {MIN_AREA_HA} ha.")
    if area > MAX_AREA_HA:
        raise PlotError("area_too_large", f"The field must be at most {MAX_AREA_HA:g} ha.")
    if farm_lat is not None and farm_lng is not None:
        c_lat, c_lng = centroid(ring)
        if haversine_km(farm_lat, farm_lng, c_lat, c_lng) > MAX_DISTANCE_FROM_FARM_KM:
            raise PlotError("too_far_from_farm", f"The field must be within {MAX_DISTANCE_FROM_FARM_KM:g} km of the farm location.")
    # RFC 7946 exterior rings are counter-clockwise; Earth Engine accepts either, but store one canonical order.
    xy = _project(ring)
    if sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(xy, xy[1:])) < 0:
        ring = ring[::-1]
    return {"geometry": {"type": "Polygon", "coordinates": [ring]}, "area_ha": round(area, 3)}


def geometry_key(geometry: dict) -> str:
    """Stable, non-reversible cache key for a geometry (coordinates never appear in keys or logs)."""
    return hashlib.sha256(json.dumps(geometry["coordinates"], separators=(",", ":")).encode()).hexdigest()[:24]

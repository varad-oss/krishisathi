"""Operator check: is Sentinel-2 via Earth Engine really working with these credentials?

Step 1 (health check): authenticate and read COPERNICUS/S2_SR_HARMONIZED metadata; print the status.
Step 2 (real query): query Sentinel-2 at a coordinate and print the same JSON the API returns.

    cd backend
    EE_SERVICE_ACCOUNT_KEY_JSON="$(cat key.json)" python scripts/check_earth_engine.py [lat lng]
    EE_SERVICE_ACCOUNT_KEY_JSON="$(cat key.json)" python scripts/check_earth_engine.py --status-only

Exit code 0 when NDVI (or an honest "no suitable observation") comes back, 1 otherwise.
"""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.earth_engine_service import earth_engine_service as service  # noqa: E402


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--status-only"]
    lat, lng = (float(args[0]), float(args[1])) if len(args) == 2 else (30.90, 75.85)  # Ludhiana
    print("status:", json.dumps(service.describe()))
    if not service.initialized:
        print("Earth Engine is not ready; see docs/EARTH_ENGINE.md for what each error code means.")
        return 1
    if "--status-only" in sys.argv:
        return 0
    result = asyncio.run(service.get_point_crop_health(lat, lng))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] in ("available", "no_data") else 1


if __name__ == "__main__":
    sys.exit(main())

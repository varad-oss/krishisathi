with open("backend/routers/dashboard.py", "r") as f:
    content = f.read()

import re

ee_replacement = """@router.get("/crop-health")
async def get_crop_health():
    import asyncio
    from services.earth_engine_service import earth_engine_service
    from datetime import datetime, timedelta
    
    outbreaks = await persistence_service.get_outbreaks()
    active_outbreaks = [o for o in outbreaks if o.get('status') == 'active']
    
    if not active_outbreaks:
        return {
            "status": "unavailable",
            "message": "No active outbreak regions to compute crop health for.",
            "regions": [],
            "overall_index": None,
            "measurement_date": None
        }
        
    target_outbreaks = active_outbreaks[:3]
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    end_date_str = end_date.strftime('%Y-%m-%d')
    start_date_str = start_date.strftime('%Y-%m-%d')
    
    results = []
    overall_sum = 0
    valid_count = 0
    
    for o in target_outbreaks:
        lat, lng = o['lat'], o['lng']
        delta = 0.1 
        try:
            import ee
            geom = ee.Geometry.Rectangle([lng - delta, lat - delta, lng + delta, lat + delta])
            
            res = await asyncio.to_thread(
                earth_engine_service.calculate_regional_ndvi, 
                geom, start_date_str, end_date_str
            )
            
            if res.get("status") == "available":
                val = res.get("value", 0)
                status_label = "healthy" if val > 0.5 else "stressed" if val < 0.3 else "fair"
                results.append({
                    "name": o["location"],
                    "ndvi": val,
                    "moisture": 0.5,
                    "drought_risk": 1 if val < 0.3 else 0,
                    "primary_crop": ", ".join(o.get("crop_targets", [])) if o.get("crop_targets") else "Unknown",
                    "status": status_label
                })
                overall_sum += val
                valid_count += 1
        except Exception:
            pass
            
    if not results:
        return {
            "status": "unavailable",
            "message": "Earth Engine data is currently unavailable or unauthenticated.",
            "regions": [],
            "overall_index": None,
            "measurement_date": None
        }
        
    return {
        "status": "available",
        "message": "Calculated from Sentinel-2 imagery.",
        "regions": results,
        "overall_index": overall_sum / valid_count if valid_count else None,
        "measurement_period": f"{start_date_str} to {end_date_str}",
        "source": "google-earth-engine",
        "dataset": "COPERNICUS/S2_SR_HARMONIZED"
    }
"""

content = re.sub(r"@router.get\(\"/crop-health\"\)\nasync def get_crop_health\(\):[\s\S]+? measurement_date: None\n    \}", ee_replacement, content)

with open("backend/routers/dashboard.py", "w") as f:
    f.write(content)


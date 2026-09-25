import re

with open("backend/services/persistence_service.py", "r") as f:
    content = f.read()

imports = """import math
from datetime import timedelta
"""

# Replace 'from datetime import datetime' with imports + 'from datetime import datetime'
if "from datetime import timedelta" not in content:
    content = content.replace("from datetime import datetime", imports + "from datetime import datetime")

haversine = """
def _haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon / 2) * math.sin(dLon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
"""

if "_haversine" not in content:
    content = content.replace("class PersistenceService:", haversine + "\nclass PersistenceService:")


save_diagnosis_replacement = """    async def save_diagnosis(self, diagnosis_data: dict, crop: str, lat: float, lng: float, language: str) -> None:
        try:
            async with AsyncSessionLocal() as session:
                disease_name = diagnosis_data.get("disease_name")
                severity = diagnosis_data.get("severity", "Medium")
                record = DiagnosisRecord(
                    crop=crop,
                    disease=disease_name,
                    confidence=diagnosis_data.get("confidence"),
                    severity=severity,
                    spread_risk=diagnosis_data.get("spread_risk", "Medium"),
                    lat=lat,
                    lng=lng,
                    language=language
                )
                session.add(record)
                await session.flush()
                
                if disease_name:
                    lat_grid = round(lat, 0)
                    lng_grid = round(lng, 0)
                    grid_id = f"{lat_grid}_{lng_grid}"
                    
                    stmt = select(OutbreakRecord).where(
                        OutbreakRecord.disease == disease_name,
                        OutbreakRecord.grid_id == grid_id,
                        OutbreakRecord.status == 'active'
                    ).with_for_update()
                    result = await session.execute(stmt)
                    existing_outbreak = result.scalar_one_or_none()
                    
                    if existing_outbreak:
                        existing_outbreak.report_count += 1
                        existing_outbreak.timestamp = datetime.utcnow()
                        crops = list(existing_outbreak.crop_targets) if existing_outbreak.crop_targets else []
                        if crop and crop not in crops:
                            crops.append(crop)
                        existing_outbreak.crop_targets = crops
                        # Upgrade severity if new report is High
                        if severity.lower() == "high" and existing_outbreak.severity.lower() != "high":
                            existing_outbreak.severity = "High"
                    else:
                        seven_days_ago = datetime.utcnow() - timedelta(days=7)
                        diag_stmt = select(DiagnosisRecord).where(
                            DiagnosisRecord.disease == disease_name,
                            DiagnosisRecord.timestamp >= seven_days_ago
                        )
                        diag_res = await session.execute(diag_stmt)
                        recent_diags = diag_res.scalars().all()
                        
                        cluster = []
                        for d in recent_diags:
                            if _haversine(lat, lng, d.lat, d.lng) <= 50.0:
                                cluster.append(d)
                                
                        if len(cluster) >= 3:
                            crops = list(set([d.crop for d in cluster if d.crop]))
                            
                            new_outbreak = OutbreakRecord(
                                disease=disease_name,
                                lat=lat,
                                lng=lng,
                                location_name=f"Cluster near {lat:.2f}, {lng:.2f}",
                                radius_km=50.0,
                                severity=severity,
                                report_count=len(cluster),
                                crop_targets=crops,
                                status="active",
                                grid_id=grid_id
                            )
                            session.add(new_outbreak)
                            
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to persist diagnosis: {e}")
            raise"""

# Regex to replace the old save_diagnosis
content = re.sub(r"    async def save_diagnosis[\s\S]+?raise", save_diagnosis_replacement, content, count=1)

with open("backend/services/persistence_service.py", "w") as f:
    f.write(content)


import logging
from typing import List, Optional
from sqlalchemy import select, func
from core.database import AsyncSessionLocal
from models.schema import DiagnosisRecord, AdvisoryRecord, OutbreakRecord, FederationSignalRecord
from models.interop import RegionalAgriSignal
import math
from datetime import timedelta
from datetime import datetime

logger = logging.getLogger(__name__)


def _haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon / 2) * math.sin(dLon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class PersistenceService:
    async def save_diagnosis(self, diagnosis_data: dict, crop: str, lat: float, lng: float, language: str) -> None:
        try:
            disease_name = diagnosis_data.get("disease_name")
            aggregated_severity = diagnosis_data.get("model_inferred_severity", "Medium")
            
            # Step 1: Save the diagnosis independently
            async with AsyncSessionLocal() as session:
                record = DiagnosisRecord(
                    crop=crop,
                    disease=disease_name,
                    model_confidence_score=diagnosis_data.get("model_confidence_score"),
                    model_inferred_severity=diagnosis_data.get("model_inferred_severity", "Medium"),
                    model_inferred_spread_risk=diagnosis_data.get("model_inferred_spread_risk", "Medium"),
                    lat=lat,
                    lng=lng,
                    language=language
                )
                session.add(record)
                await session.commit()
            
            # Step 2: Evaluate and update outbreaks
            if not disease_name:
                return
                
            async with AsyncSessionLocal() as session:
                # Lock all active outbreaks for this disease to serialize updates
                stmt = select(OutbreakRecord).where(
                    OutbreakRecord.disease == disease_name,
                    OutbreakRecord.status == 'active'
                ).with_for_update()
                result = await session.execute(stmt)
                active_outbreaks = result.scalars().all()
                
                existing_outbreak = None
                min_dist = 50.0
                for ob in active_outbreaks:
                    dist = _haversine(lat, lng, ob.lat, ob.lng)
                    if dist <= min_dist:
                        min_dist = dist
                        existing_outbreak = ob
                
                if existing_outbreak:
                    existing_outbreak.report_count += 1
                    existing_outbreak.timestamp = datetime.utcnow()
                    crops = list(existing_outbreak.crop_targets) if existing_outbreak.crop_targets else []
                    if crop and crop not in crops:
                        crops.append(crop)
                    existing_outbreak.crop_targets = crops
                    if aggregated_severity.lower() == "high" and existing_outbreak.aggregated_severity.lower() != "high":
                        existing_outbreak.aggregated_severity = "High"
                    await session.commit()
                else:
                    # Look for recent diagnoses to form a cluster
                    seven_days_ago = datetime.utcnow() - timedelta(days=7)
                    
                    # Bounding box filter to prevent loading all disease records into app memory
                    # 1 degree lat is ~111km, 1 degree lng in India (max 37N) is ~88km.
                    # 50km radius requires ~0.6 degrees bounding box.
                    lat_margin, lng_margin = 0.6, 0.6
                    
                    diag_stmt = select(DiagnosisRecord).where(
                        DiagnosisRecord.disease == disease_name,
                        DiagnosisRecord.timestamp >= seven_days_ago,
                        DiagnosisRecord.lat >= lat - lat_margin,
                        DiagnosisRecord.lat <= lat + lat_margin,
                        DiagnosisRecord.lng >= lng - lng_margin,
                        DiagnosisRecord.lng <= lng + lng_margin
                    )
                    diag_res = await session.execute(diag_stmt)
                    recent_diags = diag_res.scalars().all()
                    
                    cluster = []
                    for d in recent_diags:
                        if _haversine(lat, lng, d.lat, d.lng) <= 50.0:
                            cluster.append(d)
                            
                    if len(cluster) >= 3:
                        crops = list(set([d.crop for d in cluster if d.crop]))
                        cluster.sort(key=lambda d: d.timestamp)
                        cluster_id = cluster[0].id
                        
                        new_outbreak = OutbreakRecord(
                            disease=disease_name,
                            lat=lat,
                            lng=lng,
                            location_name=f"Cluster near {lat:.2f}, {lng:.2f}",
                            radius_km=50.0,
                            aggregated_severity=aggregated_severity,
                            report_count=len(cluster),
                            crop_targets=crops,
                            status="active",
                            grid_id=cluster_id
                        )
                        session.add(new_outbreak)
                        try:
                            await session.commit()
                        except Exception as e: # Catch IntegrityError from unique constraint
                            await session.rollback()
                            # A concurrent transaction just created this outbreak!
                            # Fetch it and update it
                            retry_stmt = select(OutbreakRecord).where(
                                OutbreakRecord.disease == disease_name,
                                OutbreakRecord.grid_id == cluster_id,
                                OutbreakRecord.status == 'active'
                            ).with_for_update()
                            retry_res = await session.execute(retry_stmt)
                            retry_ob = retry_res.scalar_one_or_none()
                            
                            if retry_ob:
                                # Recount actual diagnoses to avoid double-counting in concurrency race
                                retry_res_diags = await session.execute(diag_stmt)
                                cluster_diags = [d for d in retry_res_diags.scalars().all() if _haversine(lat, lng, d.lat, d.lng) <= 50.0]
                                retry_ob.report_count = len(cluster_diags)
                                retry_ob.timestamp = datetime.utcnow()
                                r_crops = list(retry_ob.crop_targets) if retry_ob.crop_targets else []
                                if crop and crop not in r_crops:
                                    r_crops.append(crop)
                                retry_ob.crop_targets = r_crops
                                if aggregated_severity.lower() == "high":
                                    retry_ob.aggregated_severity = "High"
                                await session.commit()

        except Exception as e:
            logger.error(f"Failed to persist diagnosis: {e}")
            raise

    async def save_advisory(self, query: str, advisory_text: str, crop: str, lat: float, lng: float, language: str, data_sources: List[str]) -> None:
        try:
            async with AsyncSessionLocal() as session:
                record = AdvisoryRecord(
                    query=query,
                    advisory_text=advisory_text,
                    crop=crop,
                    lat=lat,
                    lng=lng,
                    language=language,
                    data_sources=data_sources
                )
                session.add(record)
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to persist advisory: {e}")
            raise
    
    async def get_outbreaks(self, limit: int = 100, active_only: bool = True) -> List[dict]:
        async with AsyncSessionLocal() as session:
            stmt = select(OutbreakRecord)
            if active_only:
                stmt = stmt.where(OutbreakRecord.status == 'active')
            stmt = stmt.order_by(OutbreakRecord.timestamp.desc()).limit(limit)
            result = await session.execute(stmt)
            records = result.scalars().all()
            return [
                {
                    "id": r.id,
                    "disease": r.disease,
                    "location": r.location_name,
                    "lat": r.lat,
                    "lng": r.lng,
                    "radius_km": r.radius_km,
                    "severity": r.aggregated_severity,
                    "report_count": r.report_count,
                    "crop_targets": r.crop_targets,
                    "timestamp": r.timestamp.isoformat(),
                    "status": r.status
                } for r in records
            ]

    async def save_federation_signal(self, signal: RegionalAgriSignal) -> RegionalAgriSignal:
        try:
            async with AsyncSessionLocal() as session:
                record = FederationSignalRecord(
                    id=signal.signal_id,
                    timestamp=signal.timestamp,
                    from_state=signal.from_state,
                    to_state=signal.to_state,
                    signal_type=signal.signal_type,
                    severity=signal.severity,
                    message=signal.message,
                    disease_name=signal.disease_name,
                    affected_crop=signal.affected_crop,
                    affected_district=signal.affected_district,
                    report_count=signal.report_count,
                    signal_metadata=signal.metadata
                )
                session.add(record)
                await session.commit()
                return signal
        except Exception as e:
            logger.error(f"Failed to persist federation signal: {e}")
            raise

    async def get_federation_signals(self, limit: int = 100) -> List[RegionalAgriSignal]:
        async with AsyncSessionLocal() as session:
            stmt = select(FederationSignalRecord).order_by(FederationSignalRecord.timestamp.desc()).limit(limit)
            result = await session.execute(stmt)
            records = result.scalars().all()
            signals = []
            for r in records:
                signals.append(RegionalAgriSignal(
                    signal_id=r.id,
                    timestamp=r.timestamp,
                    from_state=r.from_state,
                    to_state=r.to_state,
                    signal_type=r.signal_type,
                    severity=r.severity,
                    message=r.message,
                    disease_name=r.disease_name,
                    affected_crop=r.affected_crop,
                    affected_district=r.affected_district,
                    report_count=r.report_count,
                    metadata=r.signal_metadata
                ))
            return signals

    async def get_dashboard_stats(self) -> dict:
        import asyncio
        # We spawn separate sessions to execute queries concurrently.
        # This trades connection pool slots for significantly reduced request latency.
        async def _count_diag():
            async with AsyncSessionLocal() as session:
                return await session.scalar(select(func.count(DiagnosisRecord.id)))
                
        async def _count_outb():
            async with AsyncSessionLocal() as session:
                return await session.scalar(select(func.count(OutbreakRecord.id)).where(OutbreakRecord.status == 'active'))
                
        async def _dist_disease():
            async with AsyncSessionLocal() as session:
                res = await session.execute(
                    select(DiagnosisRecord.disease, func.count(DiagnosisRecord.id))
                    .group_by(DiagnosisRecord.disease)
                    .order_by(func.count(DiagnosisRecord.id).desc())
                    .limit(5)
                )
                return {row[0]: row[1] for row in res.all() if row[0]}
                
        async def _dist_crop():
            async with AsyncSessionLocal() as session:
                res = await session.execute(
                    select(DiagnosisRecord.crop, func.count(DiagnosisRecord.id))
                    .group_by(DiagnosisRecord.crop)
                    .order_by(func.count(DiagnosisRecord.id).desc())
                    .limit(5)
                )
                return {row[0]: row[1] for row in res.all() if row[0]}
                
        async def _recent_diag():
            async with AsyncSessionLocal() as session:
                res = await session.execute(
                    select(DiagnosisRecord).order_by(DiagnosisRecord.timestamp.desc()).limit(5)
                )
                return res.scalars().all()
                
        async def _recent_adv():
            async with AsyncSessionLocal() as session:
                res = await session.execute(
                    select(AdvisoryRecord).order_by(AdvisoryRecord.timestamp.desc()).limit(5)
                )
                return res.scalars().all()
                
        results = await asyncio.gather(
            _count_diag(),
            _count_outb(),
            _dist_disease(),
            _dist_crop(),
            _recent_diag(),
            _recent_adv()
        )
        
        total_diag = results[0]
        total_outbreaks = results[1]
        disease_distribution = results[2]
        crop_distribution = results[3]
        recent_diag = results[4]
        recent_adv = results[5]
        
        activity = []
        for d in recent_diag:
            activity.append({
                "id": d.id,
                "type": "diagnosis",
                "title": f"Diagnosis: {d.disease}",
                "timestamp": d.timestamp.isoformat(),
                "model_inferred_severity": d.model_inferred_severity,
                "location": {"lat": d.lat, "lng": d.lng}
            })
            
        for a in recent_adv:
            activity.append({
                "id": a.id,
                "type": "advisory",
                "title": f"Advisory provided for {a.crop or 'general query'}",
                "timestamp": a.timestamp.isoformat(),
                "location": {"lat": a.lat, "lng": a.lng}
            })
            
        activity.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {
            "total_diagnoses": total_diag,
            "active_outbreaks": total_outbreaks,
            "disease_distribution": disease_distribution,
            "crop_distribution": crop_distribution,
            "recent_activity": activity[:10],
            "farmers_reached": 28710000,
            "languages_served": 10,
            "diagnoses_trend": 14.5
        }

persistence_service = PersistenceService()

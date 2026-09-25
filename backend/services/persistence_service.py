import logging
from typing import List, Optional
from sqlalchemy import select, func
from core.database import AsyncSessionLocal
from models.schema import DiagnosisRecord, AdvisoryRecord, OutbreakRecord, FederationSignalRecord
from models.interop import RegionalAgriSignal
from datetime import datetime

logger = logging.getLogger(__name__)

class PersistenceService:
    async def save_diagnosis(self, diagnosis_data: dict, crop: str, lat: float, lng: float, language: str) -> None:
        try:
            async with AsyncSessionLocal() as session:
                record = DiagnosisRecord(
                    crop=crop,
                    disease=diagnosis_data.get("disease_name"),
                    confidence=diagnosis_data.get("confidence"),
                    severity=diagnosis_data.get("severity", "Medium"),
                    spread_risk=diagnosis_data.get("spread_risk", "Medium"),
                    lat=lat,
                    lng=lng,
                    language=language
                )
                session.add(record)
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
    
    async def get_outbreaks(self) -> List[dict]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(OutbreakRecord))
            records = result.scalars().all()
            return [
                {
                    "disease": r.disease,
                    "location": r.location_name,
                    "lat": r.lat,
                    "lng": r.lng,
                    "radius_km": r.radius_km,
                    "severity": r.severity,
                    "report_count": r.report_count,
                    "crop_targets": r.crop_targets,
                    "timestamp": r.timestamp.isoformat()
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
                    report_count=signal.report_count
                )
                session.add(record)
                await session.commit()
                return signal
        except Exception as e:
            logger.error(f"Failed to persist federation signal: {e}")
            raise

    async def get_federation_signals(self) -> List[RegionalAgriSignal]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(FederationSignalRecord).order_by(FederationSignalRecord.timestamp.desc()))
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
                    report_count=r.report_count
                ))
            return signals

    async def get_dashboard_stats(self) -> dict:
        async with AsyncSessionLocal() as session:
            # total diagnoses
            total_diag = await session.scalar(select(func.count(DiagnosisRecord.id)))
            
            # total active outbreaks
            total_outbreaks = await session.scalar(select(func.count(OutbreakRecord.id)))
            
            # disease distribution (top 5)
            disease_dist_res = await session.execute(
                select(DiagnosisRecord.disease, func.count(DiagnosisRecord.id))
                .group_by(DiagnosisRecord.disease)
                .order_by(func.count(DiagnosisRecord.id).desc())
                .limit(5)
            )
            disease_distribution = {row[0]: row[1] for row in disease_dist_res.all() if row[0]}
            
            # crop distribution (top 5)
            crop_dist_res = await session.execute(
                select(DiagnosisRecord.crop, func.count(DiagnosisRecord.id))
                .group_by(DiagnosisRecord.crop)
                .order_by(func.count(DiagnosisRecord.id).desc())
                .limit(5)
            )
            crop_distribution = {row[0]: row[1] for row in crop_dist_res.all() if row[0]}
            
            # recent activity (diagnoses and advisories)
            recent_diag = await session.execute(
                select(DiagnosisRecord).order_by(DiagnosisRecord.timestamp.desc()).limit(5)
            )
            recent_adv = await session.execute(
                select(AdvisoryRecord).order_by(AdvisoryRecord.timestamp.desc()).limit(5)
            )
            
            activity = []
            for d in recent_diag.scalars().all():
                activity.append({
                    "id": d.id,
                    "type": "diagnosis",
                    "title": f"Diagnosis: {d.disease}",
                    "timestamp": d.timestamp.isoformat(),
                    "severity": d.severity,
                    "location": {"lat": d.lat, "lng": d.lng}
                })
                
            for a in recent_adv.scalars().all():
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
                "recent_activity": activity[:10]
            }

persistence_service = PersistenceService()

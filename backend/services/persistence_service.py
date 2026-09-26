import logging
from typing import List
from sqlalchemy import select, func
from core.database import AsyncSessionLocal
from models.schema import DiagnosisRecord, AdvisoryRecord, OutbreakRecord, FederationSignalRecord
from models.interop import RegionalAgriSignal
import math
from datetime import timedelta
from datetime import datetime, timezone

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

OUTBREAK_RADIUS_KM = 50.0
OUTBREAK_MIN_REPORTS = 3
OUTBREAK_WINDOW_DAYS = 7
OUTBREAK_STALE_DAYS = 21  # outbreaks with no new report for this long are not shown as active
ELIGIBLE_CERTAINTY = ("moderate", "high")
PUBLIC_COORD_DECIMALS = 1  # ~11 km; never expose a farmer's exact position


def normalize_level(value) -> str | None:
    """Maps legacy 'Medium'/'High' values and new levels onto low | moderate | high."""
    if not value:
        return None
    v = str(value).strip().lower()
    return {"medium": "moderate", "severe": "high", "critical": "high"}.get(v, v) if v in ("low", "moderate", "medium", "high", "severe", "critical") else None


def outbreak_eligible(diagnosis: dict, lat, lng) -> bool:
    """Only confident, located disease detections may contribute to outbreak clusters."""
    return (
        diagnosis.get("diagnosis_status") == "disease_detected"
        and diagnosis.get("certainty") in ELIGIBLE_CERTAINTY
        and bool(diagnosis.get("disease_name"))
        and lat is not None and lng is not None
    )


def _public_coord(v: float) -> float:
    return round(v, PUBLIC_COORD_DECIMALS)


class PersistenceService:
    async def save_diagnosis(self, diagnosis_data: dict, crop: str, lat: float | None, lng: float | None, language: str) -> None:
        """Records a diagnosis and updates outbreak clusters.

        diagnosis_data keys: disease_name (canonical English), diagnosis_status, certainty, severity, spread_risk.
        """
        try:
            status = diagnosis_data.get("diagnosis_status")
            disease_name = diagnosis_data.get("disease_name") or status or "unknown"
            aggregated_severity = normalize_level(diagnosis_data.get("severity")) or "moderate"

            # Step 1: Save the diagnosis independently
            async with AsyncSessionLocal() as session:
                record = DiagnosisRecord(
                    crop=crop,
                    disease=disease_name,
                    diagnosis_status=status,
                    certainty=diagnosis_data.get("certainty"),
                    model_inferred_severity=normalize_level(diagnosis_data.get("severity")),
                    model_inferred_spread_risk=normalize_level(diagnosis_data.get("spread_risk")),
                    lat=lat,
                    lng=lng,
                    language=language
                )
                session.add(record)
                await session.commit()
            
            # Step 2: Evaluate and update outbreaks
            if not outbreak_eligible(diagnosis_data, lat, lng):
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
                min_dist = OUTBREAK_RADIUS_KM
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
                    if aggregated_severity == "high":
                        existing_outbreak.aggregated_severity = "high"
                    await session.commit()
                else:
                    # Look for recent diagnoses to form a cluster
                    seven_days_ago = datetime.utcnow() - timedelta(days=OUTBREAK_WINDOW_DAYS)
                    
                    # Bounding box filter to prevent loading all disease records into app memory
                    # 1 degree lat is ~111km, 1 degree lng in India (max 37N) is ~88km.
                    # 50km radius requires ~0.6 degrees bounding box.
                    lat_margin, lng_margin = 0.6, 0.6
                    
                    diag_stmt = select(DiagnosisRecord).where(
                        DiagnosisRecord.disease == disease_name,
                        DiagnosisRecord.timestamp >= seven_days_ago,
                        DiagnosisRecord.diagnosis_status == "disease_detected",
                        DiagnosisRecord.certainty.in_(ELIGIBLE_CERTAINTY),
                        DiagnosisRecord.lat >= lat - lat_margin,
                        DiagnosisRecord.lat <= lat + lat_margin,
                        DiagnosisRecord.lng >= lng - lng_margin,
                        DiagnosisRecord.lng <= lng + lng_margin
                    )
                    diag_res = await session.execute(diag_stmt)
                    recent_diags = diag_res.scalars().all()
                    
                    cluster = []
                    for d in recent_diags:
                        if _haversine(lat, lng, d.lat, d.lng) <= OUTBREAK_RADIUS_KM:
                            cluster.append(d)
                            
                    if len(cluster) >= OUTBREAK_MIN_REPORTS:
                        crops = list(set([d.crop for d in cluster if d.crop]))
                        cluster.sort(key=lambda d: d.timestamp)
                        cluster_id = cluster[0].id
                        
                        new_outbreak = OutbreakRecord(
                            disease=disease_name,
                            lat=round(lat, 2),
                            lng=round(lng, 2),
                            location_name=f"Near {_public_coord(lat)}, {_public_coord(lng)}",
                            radius_km=OUTBREAK_RADIUS_KM,
                            aggregated_severity=aggregated_severity,
                            report_count=len(cluster),
                            crop_targets=crops,
                            status="active",
                            grid_id=cluster_id
                        )
                        session.add(new_outbreak)
                        try:
                            await session.commit()
                        except Exception:  # IntegrityError from the unique active-outbreak index
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
                                cluster_diags = [d for d in retry_res_diags.scalars().all() if _haversine(lat, lng, d.lat, d.lng) <= OUTBREAK_RADIUS_KM]
                                retry_ob.report_count = len(cluster_diags)
                                retry_ob.timestamp = datetime.utcnow()
                                r_crops = list(retry_ob.crop_targets) if retry_ob.crop_targets else []
                                if crop and crop not in r_crops:
                                    r_crops.append(crop)
                                retry_ob.crop_targets = r_crops
                                if aggregated_severity == "high":
                                    retry_ob.aggregated_severity = "high"
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
        """Outbreak clusters with coordinates rounded to ~11 km. Stale clusters are excluded when active_only."""
        async with AsyncSessionLocal() as session:
            stmt = select(OutbreakRecord)
            if active_only:
                cutoff = datetime.utcnow() - timedelta(days=OUTBREAK_STALE_DAYS)
                stmt = stmt.where(OutbreakRecord.status == 'active', OutbreakRecord.timestamp >= cutoff)
            stmt = stmt.order_by(OutbreakRecord.timestamp.desc()).limit(limit)
            result = await session.execute(stmt)
            records = result.scalars().all()
            return [
                {
                    "id": r.id,
                    "disease": r.disease,
                    "location": f"Near {_public_coord(r.lat)}, {_public_coord(r.lng)}",
                    "lat": _public_coord(r.lat),
                    "lng": _public_coord(r.lng),
                    "radius_km": r.radius_km,
                    "severity": normalize_level(r.aggregated_severity) or "moderate",
                    "report_count": r.report_count,
                    "crop_targets": r.crop_targets or [],
                    "timestamp": r.timestamp.replace(tzinfo=timezone.utc).isoformat(),  # stored as naive UTC
                    "status": r.status
                } for r in records
            ]

    async def save_federation_signal(self, signal: RegionalAgriSignal) -> RegionalAgriSignal:
        try:
            async with AsyncSessionLocal() as session:
                record = FederationSignalRecord(
                    id=signal.signal_id,
                    timestamp=signal.timestamp.astimezone(timezone.utc).replace(tzinfo=None) if signal.timestamp.tzinfo else signal.timestamp,
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
                    timestamp=r.timestamp.replace(tzinfo=timezone.utc) if r.timestamp.tzinfo is None else r.timestamp,
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
        """Aggregated counts from stored records only. No external or estimated figures."""
        import asyncio
        now = datetime.utcnow()
        week_ago, two_weeks_ago, month_ago = now - timedelta(days=7), now - timedelta(days=14), now - timedelta(days=30)
        detected = DiagnosisRecord.diagnosis_status == "disease_detected"

        async def scalar(stmt):
            async with AsyncSessionLocal() as session:
                return await session.scalar(stmt) or 0

        async def rows(stmt):
            async with AsyncSessionLocal() as session:
                return (await session.execute(stmt)).all()

        def distribution(column, where):
            return (
                select(column, func.count(DiagnosisRecord.id))
                .where(where, column.is_not(None))
                .group_by(column)
                .order_by(func.count(DiagnosisRecord.id).desc())
                .limit(8)
            )

        day = func.date(DiagnosisRecord.timestamp)
        (total_diag, diag_7d, diag_prev_7d, total_adv, disease_rows, crop_rows, status_rows, daily_rows, cells, outbreaks) = await asyncio.gather(
            scalar(select(func.count(DiagnosisRecord.id))),
            scalar(select(func.count(DiagnosisRecord.id)).where(DiagnosisRecord.timestamp >= week_ago)),
            scalar(select(func.count(DiagnosisRecord.id)).where(DiagnosisRecord.timestamp >= two_weeks_ago, DiagnosisRecord.timestamp < week_ago)),
            scalar(select(func.count(AdvisoryRecord.id))),
            rows(distribution(DiagnosisRecord.disease, detected)),
            rows(distribution(DiagnosisRecord.crop, DiagnosisRecord.timestamp >= month_ago)),
            rows(distribution(DiagnosisRecord.diagnosis_status, DiagnosisRecord.timestamp >= month_ago)),
            rows(select(day, func.count(DiagnosisRecord.id)).where(DiagnosisRecord.timestamp >= month_ago).group_by(day).order_by(day)),
            rows(
                select(func.round(DiagnosisRecord.lat * 2) / 2, func.round(DiagnosisRecord.lng * 2) / 2)
                .where(DiagnosisRecord.lat.is_not(None), DiagnosisRecord.timestamp >= month_ago)
                .distinct()
            ),
            self.get_outbreaks(),
        )

        return {
            "generated_at": now.isoformat() + "Z",
            "total_diagnoses": total_diag,
            "diagnoses_last_7_days": diag_7d,
            "diagnoses_previous_7_days": diag_prev_7d,
            "total_advisories": total_adv,
            "active_outbreaks": len(outbreaks),
            "disease_distribution": {r[0]: r[1] for r in disease_rows},
            "crop_distribution_30d": {r[0]: r[1] for r in crop_rows},
            "status_distribution_30d": {r[0]: r[1] for r in status_rows},
            "daily_diagnoses_30d": [{"date": str(r[0])[:10], "count": r[1]} for r in daily_rows],
            "coverage": {"grid_cells_30d": len(cells), "grid_size_deg": 0.5},
            "provenance": {
                "source": "KrishiSathi diagnosis and advisory records",
                "kind": "ai_classified_user_reports",
                "notes": "Counts of photos submitted to KrishiSathi and classified by an AI model. They are not official crop statistics and reflect where the app is used.",
            },
        }


persistence_service = PersistenceService()

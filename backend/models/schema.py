from sqlalchemy import Column, Date, ForeignKey, Index, String, text, Float, DateTime, Integer, JSON
from core.database import Base
from datetime import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class DiagnosisRecord(Base):
    __tablename__ = "diagnoses"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    crop = Column(String, nullable=True, index=True)
    disease = Column(String, nullable=False, index=True)
    # Legacy numeric self-reported score; new records store qualitative certainty instead.
    model_confidence_score = Column(Float, nullable=True)
    model_inferred_severity = Column(String, nullable=True)
    model_inferred_spread_risk = Column(String, nullable=True)
    diagnosis_status = Column(String, nullable=True, index=True)
    certainty = Column(String, nullable=True)
    lat = Column(Float, nullable=True)  # null when the farmer did not share location
    lng = Column(Float, nullable=True)
    language = Column(String, default="en")
    farm_id = Column(String, ForeignKey("farms.id"), nullable=True, index=True)

class AdvisoryRecord(Base):
    __tablename__ = "advisories"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    query = Column(String, nullable=False)
    advisory_text = Column(String, nullable=False)
    crop = Column(String, nullable=True, index=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    language = Column(String, default="en")
    data_sources = Column(JSON, default=list)

class OutbreakRecord(Base):
    __tablename__ = "outbreaks"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    disease = Column(String, nullable=False, index=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    location_name = Column(String, nullable=False)
    radius_km = Column(Float, nullable=False)
    aggregated_severity = Column(String, nullable=False)
    report_count = Column(Integer, default=1)
    crop_targets = Column(JSON, default=list)
    status = Column(String, default="active")
    grid_id = Column(String, nullable=True)

    __table_args__ = (
        Index(
            "uq_active_outbreak",
            "disease",
            "grid_id",
            unique=True,
            sqlite_where=text("status = 'active'"),
            postgresql_where=text("status = 'active'")
        ),
    )

class FederationSignalRecord(Base):
    __tablename__ = "federation_signals"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    from_state = Column(String, nullable=False)
    to_state = Column(String, nullable=True)
    signal_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    message = Column(String, nullable=False)
    disease_name = Column(String, nullable=True)
    affected_crop = Column(String, nullable=True, index=True)
    affected_district = Column(String, nullable=True)
    report_count = Column(Integer, default=1)
    signal_metadata = Column(JSON, nullable=True)


class FarmRecord(Base):
    """Farm digital twin: a farmer's field. Access is by a bearer farm token whose SHA-256 is stored here;
    no name, phone or account is collected. Location is kept at ~110 m (3 decimals) and never published."""
    __tablename__ = "farms"

    id = Column(String, primary_key=True, default=generate_uuid)
    token_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    country_code = Column(String(2), nullable=False, default="IN")
    crop = Column(String, nullable=True, index=True)
    sowing_date = Column(Date, nullable=True)
    area_ha = Column(Float, nullable=True)

    __table_args__ = (Index("ix_farms_location", "lat", "lng"),)


class FarmSnapshotRecord(Base):
    """What the intelligence engine concluded for a farm at one time: the twin's history."""
    __tablename__ = "farm_snapshots"

    id = Column(String, primary_key=True, default=generate_uuid)
    farm_id = Column(String, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    crop = Column(String, nullable=True)
    crop_stage = Column(String, nullable=True)
    top_action = Column(String, nullable=True)
    top_severity = Column(String, nullable=True)
    risks = Column(JSON, nullable=False)          # {category: severity}
    data_quality = Column(JSON, nullable=False)   # {source: status}
    observations = Column(JSON, nullable=True)    # compact weather/soil/satellite values used

    __table_args__ = (Index("ix_farm_snapshots_farm_time", "farm_id", "created_at"),)


class AdvisoryActionRecord(Base):
    """A recommendation given to a farm and the farmer's self-reported follow-through and outcome.
    These are feedback signals, not evidence that the recommendation caused the outcome."""
    __tablename__ = "advisory_actions"

    id = Column(String, primary_key=True, default=generate_uuid)
    farm_id = Column(String, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    source_type = Column(String, nullable=False)   # intelligence | diagnosis | regenerative
    source_ref = Column(String, nullable=True)     # snapshot / diagnosis id / practice id
    action = Column(String, nullable=False, index=True)
    category = Column(String, nullable=True)
    severity = Column(String, nullable=True)
    confidence = Column(String, nullable=True)
    crop = Column(String, nullable=True, index=True)
    followed = Column(String, nullable=True)       # yes | partial | no | not_applicable
    followed_at = Column(DateTime, nullable=True)
    outcome = Column(String, nullable=True)        # improved | same | worse | diagnosis_wrong | not_sure
    outcome_at = Column(DateTime, nullable=True)

    __table_args__ = (Index("ix_advisory_actions_farm_time", "farm_id", "created_at"),)


class FarmPlotRecord(Base):
    """The farmer's optional field outline (one per farm). GeoJSON Polygon, private to the farm-token holder:
    never published, logged or used in cache keys. Farms without a plot keep using their location point."""
    __tablename__ = "farm_plots"

    id = Column(String, primary_key=True, default=generate_uuid)
    farm_id = Column(String, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, unique=True)
    geometry = Column(JSON, nullable=False)
    area_ha = Column(Float, nullable=False)
    crop = Column(String, nullable=True)
    sowing_date = Column(Date, nullable=True)   # optional crop-cycle association
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

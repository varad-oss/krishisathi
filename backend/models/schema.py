from sqlalchemy import Column, String, Float, DateTime, Integer, JSON, Boolean
from core.database import Base
from datetime import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class DiagnosisRecord(Base):
    __tablename__ = "diagnoses"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, default=datetime.utcnow)
    crop = Column(String, nullable=True)
    disease = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    severity = Column(String, nullable=False)
    spread_risk = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    language = Column(String, default="en")

class AdvisoryRecord(Base):
    __tablename__ = "advisories"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, default=datetime.utcnow)
    query = Column(String, nullable=False)
    advisory_text = Column(String, nullable=False)
    crop = Column(String, nullable=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    language = Column(String, default="en")
    data_sources = Column(JSON, default=list)

class OutbreakRecord(Base):
    __tablename__ = "outbreaks"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, default=datetime.utcnow)
    disease = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    location_name = Column(String, nullable=False)
    radius_km = Column(Float, nullable=False)
    severity = Column(String, nullable=False)
    report_count = Column(Integer, default=1)
    crop_targets = Column(JSON, default=list)

class FederationSignalRecord(Base):
    __tablename__ = "federation_signals"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, default=datetime.utcnow)
    from_state = Column(String, nullable=False)
    to_state = Column(String, nullable=False)
    signal_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    message = Column(String, nullable=False)
    disease_name = Column(String, nullable=True)
    affected_crop = Column(String, nullable=True)
    affected_district = Column(String, nullable=True)
    report_count = Column(Integer, default=1)

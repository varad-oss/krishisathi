from fastapi import APIRouter, Depends
from core.security import require_system_role
from services.earth_engine_service import earth_engine_service, EE_AVAILABLE

router = APIRouter(prefix="/api/debug", tags=["Debug & Verification"])

@router.get("/earth-engine-status", dependencies=[Depends(require_system_role)])
async def get_ee_status():
    """Debug endpoint for hackathon judges to verify Earth Engine pipeline status."""
    return {
        "earth_engine_library_installed": EE_AVAILABLE,
        "earth_engine_authenticated": getattr(earth_engine_service, 'initialized', False),
        "pipeline_mode": "LIVE" if getattr(earth_engine_service, 'initialized', False) else "UNAVAILABLE",
        "note": "Requires ee.Initialize() with valid credentials to return LIVE mode."
    }

@router.get("/db")
async def debug_db():
    try:
        from core.database import Base, engine
        from models.schema import DiagnosisRecord, OutbreakRecord
        import os
        import sqlite3
        
        tables = list(Base.metadata.tables.keys())
        
        db_path = "/tmp/krishisathi.db"
        exists = os.path.exists(db_path)
        size = os.path.getsize(db_path) if exists else 0
        
        sqlite_tables = []
        if exists:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            sqlite_tables = [r[0] for r in cursor.fetchall()]
            conn.close()
            
        return {
            "metadata_tables": tables,
            "engine_url": str(engine.url),
            "file_exists": exists,
            "file_size": size,
            "sqlite_master_tables": sqlite_tables
        }
    except Exception as e:
        return {"error": str(e)}

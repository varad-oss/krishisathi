from fastapi import APIRouter
from core.database import Base, engine
import os
import sqlite3

router = APIRouter(prefix="/api/debug", tags=["Debug"])

@router.get("/db")
async def debug_db():
    try:
        from models.schema import DiagnosisRecord, OutbreakRecord
        
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

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
        
        ddl_test = []
        try:
            from sqlalchemy.schema import CreateTable
            from sqlalchemy import text
            async with engine.begin() as conn:
                for table_name, table in Base.metadata.tables.items():
                    try:
                        create_stmt = str(CreateTable(table).compile(engine.sync_engine))
                        create_stmt = create_stmt.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS")
                        await conn.execute(text(create_stmt))
                        ddl_test.append(f"Executed DDL for {table_name}")
                    except Exception as e:
                        ddl_test.append(f"EXEC FAIL {table_name}: {repr(e)}")
        except Exception as outer_e:
            ddl_test.append(f"Outer error: {repr(outer_e)}")

        exists = os.path.exists(db_path)
        size = os.path.getsize(db_path) if exists else 0
        sqlite_tables = []
        if exists:
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                sqlite_tables = [r[0] for r in cursor.fetchall()]
                conn.close()
            except Exception as e:
                sqlite_tables.append(repr(e))

        return {
            "metadata_tables": tables,
            "engine_url": str(engine.url),
            "file_exists": exists,
            "file_size": size,
            "sqlite_master_tables": sqlite_tables,
            "ddl_test": ddl_test
        }
    except Exception as e:
        return {"error": repr(e)}


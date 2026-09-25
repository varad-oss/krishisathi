import sys
import os
import uuid
import logging
from contextlib import asynccontextmanager
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'bot', 'webhook'))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routers import diagnose, advisory, alerts, weather, dashboard, states, debug, kvk
from config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

from core.database import engine
from core.rate_limit import redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🌾 KrishiSathi API starting up...")
    
    # 1. Verify Database Connection
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection established.")
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        if settings.ENVIRONMENT == "production":
            logger.warning("Database connection failed in production. Degrading gracefully.")
            
    # 2. Verify Redis Connection
    if settings.ENVIRONMENT == "production":
        if not redis_client:
            logger.warning("Redis URL not configured in production.")
        else:
            try:
                await redis_client.ping()
                logger.info("✅ Redis connection established.")
            except Exception as e:
                logger.error(f"❌ Failed to connect to Redis: {e}")
            
    logger.info("📄 API docs available at /docs")
    yield
    logger.info("KrishiSathi API shutting down...")
    
    # Graceful Teardown
    if redis_client:
        await redis_client.aclose()
        logger.info("Redis connection closed.")
    await engine.dispose()
    logger.info("Database connection pool disposed.")


@app.get("/api/debug/db")
async def debug_db():
    try:
        from core.database import Base, engine
        from models.schema import DiagnosisRecord, OutbreakRecord
        import os
        
        tables = list(Base.metadata.tables.keys())
        
        db_path = "/tmp/krishisathi.db"
        exists = os.path.exists(db_path)
        size = os.path.getsize(db_path) if exists else 0
        
        # Test direct sqlite3
        import sqlite3
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

app = FastAPI(
    title="KrishiSathi API",
    description=(
        "🌾 AI-powered agriculture intelligence platform for Indian states. "
        "Provides crop disease diagnosis, agro-advisory, weather, outbreak alerts, "
        "and policymaker analytics — powered by Google Gemini AI."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

_db_initialized = False

@app.middleware("http")
async def ensure_db_init(request: Request, call_next):
    global _db_initialized
    if not _db_initialized and settings.ENVIRONMENT == "production":
        try:
            from core.database import Base, engine
            if "sqlite" in str(engine.url):
                async with engine.begin() as conn:
                    tables = Base.metadata.tables.keys()
                    logger.warning(f"Creating tables: {tables}")
                    if not tables:
                        from models.schema import DiagnosisRecord, OutbreakRecord
                        tables = Base.metadata.tables.keys()
                        logger.warning(f"Tables after explicit import: {tables}")
                    await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            logger.error(f"Failed to init DB: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise Exception(f"DB Init Failed: {e}")
        finally:
            _db_initialized = True
    return await call_next(request)


import time

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Request-ID"] = req_id
        
        # Structured log for quantitative observability
        logger.info(
            f"ReqID: {req_id} | {request.method} {request.url.path} "
            f"| Status: {response.status_code} | Latency: {process_time:.4f}s"
        )
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"ReqID: {req_id} | {request.method} {request.url.path} "
            f"| Status: 500 | Latency: {process_time:.4f}s | Error: {str(e)}"
        )
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=500, content={"detail": f"Internal Server Error: {str(e)}"})

origins = [o.strip() for o in settings.CORS_ALLOWED_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(diagnose.router)
app.include_router(advisory.router)
app.include_router(alerts.router)
app.include_router(weather.router)
app.include_router(dashboard.router)
app.include_router(states.router)
app.include_router(debug.router)
app.include_router(kvk.router)

try:
    from handler import router as bot_router
    app.include_router(bot_router)
    logger.info("✅ WhatsApp bot webhook loaded")
except ImportError:
    logger.info("ℹ️  WhatsApp bot webhook not loaded (Twilio not installed or bot module not found)")


@app.get("/")
async def root():
    return {
        "name": "KrishiSathi API",
        "tagline": "AI-Powered Agriculture Intelligence for Indian States",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "google_ai_services": [
            f"Gemini Models used: {settings.GEMINI_DIAGNOSIS_MODEL}, {settings.GEMINI_AGENT_MODEL}",
            "Google Earth Engine (Sentinel-2 NDVI Pipeline)",
            "Open-Meteo API (Live Weather, Precipitation, Soil Moisture)",
            "gTTS (Text-to-Speech Audio Generation for WhatsApp)",
        ],
        "endpoints": {
            "diagnose": "/api/diagnose",
            "advisory": "/api/advisory",
            "weather": "/api/weather",
            "alerts": "/api/alerts",
            "dashboard": "/api/dashboard/stats",
            "state_exchange": "/api/states/exchange/signals",
            "kvk": "/api/kvk/nearest"
        },
    }


from sqlalchemy import text
from core.database import AsyncSessionLocal
from core.rate_limit import redis_client

@app.get("/health/live")
async def health_live():
    return {"status": "ok", "service": "krishisathi-api", "liveness": True}

@app.get("/health/ready")
async def health_ready():
    status = {"status": "ok", "service": "krishisathi-api", "readiness": True, "dependencies": {}}
    
    # Check Database
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        status["dependencies"]["database"] = "ok"
    except Exception as e:
        status["dependencies"]["database"] = "down"
        status["readiness"] = False
        
    # Check Redis (if configured for production)
    if settings.ENVIRONMENT == "production":
        if not redis_client:
            status["dependencies"]["redis"] = "down"
            status["readiness"] = False
        else:
            try:
                await redis_client.ping()
                status["dependencies"]["redis"] = "ok"
            except Exception as e:
                status["dependencies"]["redis"] = "down"
                status["readiness"] = False
    
    if not status["readiness"]:
        from fastapi.responses import JSONResponse
        return JSONResponse(content=status, status_code=503)
        
    return status

@app.get("/health")
async def health_check():

    return {"status": "ok", "service": "krishisathi-api", "message": "KrishiSathi API is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

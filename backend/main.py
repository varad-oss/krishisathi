import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from config import settings
from core.database import AsyncSessionLocal, engine
from core.errors import install_error_handlers
from core.middleware import RequestContextMiddleware
from core.rate_limit import redis_client
from routers import advisory, alerts, dashboard, debug, diagnose, farm, kvk, meta, states, weather

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

_db_ready = False
_db_lock = asyncio.Lock()


async def ensure_tables() -> bool:
    """Creates missing tables once per process.

    Serverless deployments (Vercel) may not run Alembic or ASGI lifespan, so this also
    runs lazily before the first request. Alembic remains the source of truth for migrations.
    """
    global _db_ready
    if _db_ready:
        return True
    async with _db_lock:
        if _db_ready:
            return True
        try:
            from models.schema import Base
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            _db_ready = True
        except Exception as e:
            logger.error("Database initialization failed: %s", e)
    return _db_ready


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("KrishiSathi API starting (environment=%s)", settings.ENVIRONMENT)
    if await ensure_tables():
        logger.info("Database ready.")
    if redis_client:
        try:
            await redis_client.ping()
            logger.info("Redis ready.")
        except Exception as e:
            logger.error("Redis unreachable; using in-process rate limiting: %s", e)
    yield
    logger.info("KrishiSathi API shutting down.")
    if redis_client:
        await redis_client.aclose()
    await engine.dispose()


app = FastAPI(
    title="KrishiSathi API",
    description=(
        "Agricultural intelligence for Indian farmers and administrators: crop disease diagnosis, grounded "
        "advisories, weather-based alerts, soil and regenerative recommendations, and aggregated outbreak data. "
        "Every error uses the envelope {error: {code, message, request_id, retryable}}."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)
install_error_handlers(app)


@app.middleware("http")
async def lazy_db_init(request, call_next):
    await ensure_tables()
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ALLOWED_ORIGINS.split(",") if o.strip()],
    allow_origin_regex=settings.CORS_ALLOWED_ORIGIN_REGEX,
    allow_credentials=False,  # the API uses bearer tokens, never cookies
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Idempotency-Key", "X-Request-ID"],
    expose_headers=["X-Request-ID", "Retry-After"],
    max_age=600,
)
# Added last so it is outermost: every response (including CORS and errors) gets a request ID.
app.add_middleware(RequestContextMiddleware)

for module in (diagnose, advisory, alerts, weather, farm, dashboard, states, kvk, meta, debug):
    app.include_router(module.router)


@app.get("/")
async def root():
    return {
        "name": "KrishiSathi API",
        "version": app.version,
        "docs": "/docs",
        "health": {"liveness": "/health/live", "readiness": "/health/ready"},
        "sources": "/api/sources",
    }


@app.get("/health/live")
@app.get("/health", include_in_schema=False)
async def health_live():
    return {"status": "ok", "service": "krishisathi-api"}


@app.get("/health/ready")
async def health_ready():
    dependencies = {}
    ready = True
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        dependencies["database"] = "ok"
    except Exception:
        dependencies["database"] = "down"
        ready = False

    if redis_client:
        try:
            await redis_client.ping()
            dependencies["redis"] = "ok"
        except Exception:
            dependencies["redis"] = "down"
            ready = settings.ENVIRONMENT != "production" and ready
    else:
        dependencies["redis"] = "not_configured"

    body = {"status": "ok" if ready else "degraded", "service": "krishisathi-api", "ready": ready, "dependencies": dependencies}
    return JSONResponse(body, status_code=200 if ready else 503)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

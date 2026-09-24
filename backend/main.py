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

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🌾 KrishiSathi API starting up...")
    logger.info("📄 API docs available at /docs")
    yield
    logger.info("KrishiSathi API shutting down...")

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

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    logger.info(f"ReqID: {req_id} | {request.method} {request.url.path}")
    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    logger.info(f"ReqID: {req_id} | {request.method} {request.url.path} - Status: {response.status_code}")
    return response

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

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "krishisathi-api", "message": "KrishiSathi API is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

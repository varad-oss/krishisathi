import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'bot', 'webhook'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routers import diagnose, advisory, alerts, weather, dashboard, brics

app = FastAPI(
    title="KrishiSathi API",
    description=(
        "🌾 AI-powered agriculture intelligence platform for BRICS nations. "
        "Provides crop disease diagnosis, agro-advisory, weather, outbreak alerts, "
        "and policymaker analytics — powered by Google Gemini AI."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for hackathon
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core API routers
app.include_router(diagnose.router)
app.include_router(advisory.router)
app.include_router(alerts.router)
app.include_router(weather.router)
app.include_router(dashboard.router)
app.include_router(brics.router)

# WhatsApp bot webhook (optional — requires Twilio)
try:
    from handler import router as bot_router
    app.include_router(bot_router)
    print("✅ WhatsApp bot webhook loaded")
except ImportError:
    print("ℹ️  WhatsApp bot webhook not loaded (Twilio not installed or bot module not found)")


@app.on_event("startup")
async def startup_event():
    print("🌾 KrishiSathi API starting up...")
    print("📄 API docs available at /docs")


@app.on_event("shutdown")
async def shutdown_event():
    print("KrishiSathi API shutting down...")


@app.get("/")
async def root():
    return {
        "name": "KrishiSathi API",
        "tagline": "AI-Powered Agriculture Intelligence for BRICS Nations",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "google_ai_services": [
            "Gemini 2.5 Flash (Multimodal)",
            "Cloud Translation API",
            "Cloud Speech-to-Text",
            "Cloud Text-to-Speech",
            "Google Earth Engine",
            "Google Maps Platform",
            "BigQuery",
            "Firebase Firestore",
        ],
        "endpoints": {
            "diagnose": "/api/diagnose",
            "advisory": "/api/advisory",
            "weather": "/api/weather",
            "alerts": "/api/alerts",
            "dashboard": "/api/dashboard/stats",
            "brics_exchange": "/api/brics/exchange",
        },
    }


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "krishisathi-api", "message": "KrishiSathi API is running"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

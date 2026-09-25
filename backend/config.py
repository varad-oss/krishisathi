import logging
from pydantic_settings import BaseSettings
from typing import Optional

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DATABASE_URL: Optional[str] = None
    TRUST_REVERSE_PROXY: bool = False
    GOOGLE_CLOUD_PROJECT: Optional[str] = "krishisathi-demo"
    GEMINI_API_KEY: Optional[str] = None
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    OPENWEATHER_API_KEY: Optional[str] = None
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_WHATSAPP_NUMBER: Optional[str] = None
    FIREBASE_PROJECT_ID: Optional[str] = None
    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001,https://ai-krishisathi.vercel.app,https://krishisathi.app"
    
    # Model configuration
    GEMINI_DIAGNOSIS_MODEL: str = "gemini-2.5-flash"
    GEMINI_ADVISORY_MODEL: str = "gemini-2.5-flash"
    GEMINI_TRANSLATION_MODEL: str = "gemini-2.5-flash"
    GEMINI_TRANSCRIPTION_MODEL: str = "gemini-2.5-flash"
    GEMINI_AGENT_MODEL: str = "gemini-2.5-flash"
    JWT_SECRET: Optional[str] = None
# Database and Redis (Pull from Vercel Integration Env Vars)
    DATABASE_URL: Optional[str] = None
    POSTGRES_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None
    KV_URL: Optional[str] = None
    UPSTASH_REDIS_REST_URL: Optional[str] = None
    RATE_LIMIT_AI: int = 10

    class Config:
        env_file = ".env"

settings = Settings()

logger.info(f"Loaded Models - Diagnosis: {settings.GEMINI_DIAGNOSIS_MODEL}, Advisory: {settings.GEMINI_ADVISORY_MODEL}, Translation: {settings.GEMINI_TRANSLATION_MODEL}, Transcription: {settings.GEMINI_TRANSCRIPTION_MODEL}, Agent: {settings.GEMINI_AGENT_MODEL}")


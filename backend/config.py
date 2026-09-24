import logging
from pydantic_settings import BaseSettings
from typing import Optional

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    GOOGLE_CLOUD_PROJECT: Optional[str] = "krishisathi-demo"
    GEMINI_API_KEY: Optional[str] = None
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    OPENWEATHER_API_KEY: Optional[str] = None
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_WHATSAPP_NUMBER: Optional[str] = None
    FIREBASE_PROJECT_ID: Optional[str] = None
    
    # Model configuration
    GEMINI_DIAGNOSIS_MODEL: str = "gemini-1.5-flash"
    GEMINI_ADVISORY_MODEL: str = "gemini-1.5-flash"
    GEMINI_TRANSLATION_MODEL: str = "gemini-1.5-flash-8b"
    GEMINI_TRANSCRIPTION_MODEL: str = "gemini-1.5-flash"
    GEMINI_AGENT_MODEL: str = "gemini-1.5-pro"

    class Config:
        env_file = ".env"

settings = Settings()

logger.info(f"Loaded Models - Diagnosis: {settings.GEMINI_DIAGNOSIS_MODEL}, Advisory: {settings.GEMINI_ADVISORY_MODEL}, Translation: {settings.GEMINI_TRANSLATION_MODEL}, Transcription: {settings.GEMINI_TRANSCRIPTION_MODEL}, Agent: {settings.GEMINI_AGENT_MODEL}")


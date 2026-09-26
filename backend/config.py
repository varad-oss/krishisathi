import logging
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENVIRONMENT: str = "development"
    TRUST_REVERSE_PROXY: bool = False
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # Comma-separated exact origins, plus an optional regex (e.g. Vercel preview URLs).
    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001,https://ai-krishisathi.vercel.app,https://krishisathi.app"
    CORS_ALLOWED_ORIGIN_REGEX: Optional[str] = None

    # Model configuration
    GEMINI_DIAGNOSIS_MODEL: str = "gemini-2.5-flash"
    GEMINI_ADVISORY_MODEL: str = "gemini-2.5-flash"
    GEMINI_TRANSCRIPTION_MODEL: str = "gemini-2.5-flash"
    GEMINI_AGENT_MODEL: str = "gemini-2.5-flash"
    AI_TIMEOUT_SECONDS: float = 45.0
    EXTERNAL_API_TIMEOUT_SECONDS: float = 10.0

    # Federation publishing requires signed JWTs. Without a secret, publishing is disabled.
    JWT_SECRET: Optional[str] = None

    # Earth Engine service account (JSON key contents). Optional.
    EE_SERVICE_ACCOUNT_KEY_JSON: Optional[str] = None

    # Database and Redis (Vercel integrations inject these names)
    DATABASE_URL: Optional[str] = None
    POSTGRES_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None
    KV_URL: Optional[str] = None
    RATE_LIMIT_AI: int = 10


settings = Settings()

logger.info(
    "Loaded models - diagnosis: %s, advisory: %s, transcription: %s, report: %s",
    settings.GEMINI_DIAGNOSIS_MODEL,
    settings.GEMINI_ADVISORY_MODEL,
    settings.GEMINI_TRANSCRIPTION_MODEL,
    settings.GEMINI_AGENT_MODEL,
)

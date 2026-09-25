import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from config import settings

logger = logging.getLogger(__name__)

# Pull from whichever variable Vercel injects
resolved_db_url = settings.DATABASE_URL or settings.POSTGRES_URL

if settings.ENVIRONMENT == "production":
    if not resolved_db_url:
        raise RuntimeError("DATABASE_URL or POSTGRES_URL must be configured in production for persistence.")
    db_url = resolved_db_url
else:
    # Fallback to local sqlite if no DATABASE_URL is provided in development
    db_url = resolved_db_url or "sqlite+aiosqlite:///./krishisathi.db"
    if db_url.startswith("sqlite"):
        logger.info("Using SQLite for development persistence.")

# SQLAlchemy requires postgresql+asyncpg for async postgres
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(db_url, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

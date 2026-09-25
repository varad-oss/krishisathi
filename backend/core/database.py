import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from config import settings

logger = logging.getLogger(__name__)

if settings.ENVIRONMENT == "production":
    if not settings.DATABASE_URL or "sqlite" in settings.DATABASE_URL:
        logger.warning("Using SQLite in production. Forcing /tmp directory for writable filesystem.")
        db_url = "sqlite+aiosqlite:////tmp/krishisathi.db"
    else:
        db_url = settings.DATABASE_URL
else:
    # Fallback to local sqlite if no DATABASE_URL is provided in development
    db_url = settings.DATABASE_URL or "sqlite+aiosqlite:////tmp/krishisathi.db"
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

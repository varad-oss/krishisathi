import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
import urllib.parse
from config import settings

logger = logging.getLogger(__name__)

resolved_db_url = settings.DATABASE_URL or settings.POSTGRES_URL

if settings.ENVIRONMENT == "production":
    if not resolved_db_url:
        raise RuntimeError("DATABASE_URL or POSTGRES_URL must be configured in production for persistence.")
    db_url = resolved_db_url
else:
    db_url = resolved_db_url or "sqlite+aiosqlite:///./krishisathi.db"
    if db_url.startswith("sqlite"):
        logger.info("Using SQLite for development persistence.")

if db_url.startswith("postgres://") or db_url.startswith("postgresql://"):
    # Strip problematic query parameters like channel_binding that Vercel/Neon injects
    parsed = urllib.parse.urlparse(db_url)
    clean_url = parsed._replace(scheme="postgresql+asyncpg", query="ssl=require").geturl()
    
    # In Vercel serverless environments, we must disable connection pooling (NullPool)
    # because Vercel Serverless Functions suspend and drop TCP connections.
    # We also disable prepared statement caching for PgBouncer compatibility.
    engine = create_async_engine(
        clean_url,
        echo=False,
        poolclass=NullPool,
        connect_args={"prepared_statement_cache_size": 0}
    )
else:
    engine = create_async_engine(db_url, echo=False)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

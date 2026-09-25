from fastapi import Request, HTTPException
import time
import redis.asyncio as redis
import logging
from config import settings

logger = logging.getLogger(__name__)

# Production configuration enforcement
if settings.ENVIRONMENT == "production":
    if not settings.REDIS_URL:
        raise RuntimeError("REDIS_URL must be configured in production for rate limiting.")

redis_client = None
if settings.REDIS_URL:
    try:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    except Exception as e:
        logger.warning(f"Failed to initialize Redis client: {e}")

async def rate_limit(request: Request, limit: int, window_seconds: int = 60, by_ip: bool = True):
    if not redis_client:
        return # Allow bypass if Redis is absent
        return # Allow in dev/demo if Redis is absent
    
    if settings.TRUST_REVERSE_PROXY:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
    else:
        client_ip = request.client.host if request.client else "unknown"
        
    identifier = client_ip if by_ip else "global"
    key = f"rate_limit:{request.url.path}:{identifier}"
    
    current_time = int(time.time())
    window_key = f"{key}:{current_time // window_seconds}"
    
    try:
        requests_in_window = await redis_client.incr(window_key)
        if requests_in_window == 1:
            await redis_client.expire(window_key, window_seconds)
            
        if requests_in_window > limit:
            raise HTTPException(status_code=429, detail="Too many requests", headers={"Retry-After": str(window_seconds)})
    except redis.RedisError as e:
        logger.error(f"Redis error during rate limiting: {e}")
        return

async def ai_rate_limit(request: Request):
    await rate_limit(request, limit=settings.RATE_LIMIT_AI, window_seconds=60)

import logging
import time

import redis.asyncio as redis
from fastapi import Request

from config import settings
from core.errors import ApiError

logger = logging.getLogger(__name__)

# Pull from whichever variable the hosting integration injects
resolved_redis_url = settings.REDIS_URL or settings.KV_URL

if settings.ENVIRONMENT == "production" and not resolved_redis_url:
    raise RuntimeError("REDIS_URL or KV_URL must be configured in production for rate limiting.")

redis_client = None
if resolved_redis_url:
    try:
        redis_client = redis.from_url(resolved_redis_url, decode_responses=True)
    except Exception as e:
        logger.warning("Failed to initialize Redis client: %s", e)

# Per-process fixed-window counters, used when Redis is absent or failing.
# Weaker than a shared limiter (each worker counts separately) but never "unlimited".
_local_windows: dict[str, int] = {}
_MAX_LOCAL_KEYS = 10_000


def _client_ip(request: Request) -> str:
    if settings.TRUST_REVERSE_PROXY:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _local_incr(window_key: str) -> int:
    if len(_local_windows) > _MAX_LOCAL_KEYS:
        _local_windows.clear()
    _local_windows[window_key] = _local_windows.get(window_key, 0) + 1
    return _local_windows[window_key]


async def rate_limit(request: Request, limit: int, window_seconds: int = 60, by_ip: bool = True):
    identifier = _client_ip(request) if by_ip else "global"
    window_key = f"rate_limit:{request.url.path}:{identifier}:{int(time.time()) // window_seconds}"

    count = None
    if redis_client:
        try:
            count = await redis_client.incr(window_key)
            if count == 1:
                await redis_client.expire(window_key, window_seconds)
        except redis.RedisError as e:
            logger.error("Redis error during rate limiting, using in-process limiter: %s", e)
    if count is None:
        count = _local_incr(window_key)

    if count > limit:
        raise ApiError(
            429,
            "RATE_LIMITED",
            "Too many requests. Please wait a minute and try again.",
            headers={"Retry-After": str(window_seconds)},
        )


async def ai_rate_limit(request: Request):
    await rate_limit(request, limit=settings.RATE_LIMIT_AI, window_seconds=60)


async def tts_rate_limit(request: Request):
    await rate_limit(request, limit=settings.RATE_LIMIT_AI * 3, window_seconds=60)

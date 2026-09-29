"""Optional shared JSON cache on Redis. Every call degrades to a no-op when Redis is absent or failing."""
import json
import logging

from core.rate_limit import redis_client

logger = logging.getLogger(__name__)


async def cache_get(key: str):
    if not redis_client:
        return None
    try:
        cached = await redis_client.get(key)
        return json.loads(cached) if cached else None
    except Exception as e:
        logger.warning("Cache read failed for %s: %s", key, e)
        return None


async def cache_set(key: str, value, seconds: int) -> None:
    if not redis_client:
        return
    try:
        await redis_client.set(key, json.dumps(value), ex=seconds)
    except Exception as e:
        logger.warning("Cache write failed for %s: %s", key, e)

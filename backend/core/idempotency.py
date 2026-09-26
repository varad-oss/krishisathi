import json
import logging

from core.rate_limit import redis_client

logger = logging.getLogger(__name__)


async def get_idempotency_result(idempotency_key: str):
    if not redis_client:
        return None
    try:
        val = await redis_client.get(f"idem:{idempotency_key}")
        return json.loads(val) if val else None
    except Exception as e:
        logger.error("Redis error getting idempotency key: %s", e)
        return None


async def set_idempotency_result(idempotency_key: str, data: dict, expire_seconds: int = 86400):
    if not redis_client:
        return
    try:
        await redis_client.set(f"idem:{idempotency_key}", json.dumps(data), ex=expire_seconds)
    except Exception as e:
        logger.error("Redis error setting idempotency key: %s", e)

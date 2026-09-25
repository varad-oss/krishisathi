from fastapi import Request, HTTPException, Response
import json
import logging
from core.rate_limit import redis_client
from config import settings
from functools import wraps

logger = logging.getLogger(__name__)

async def get_idempotency_result(idempotency_key: str):
    if not redis_client:
        return None
    try:
        val = await redis_client.get(f"idem:{idempotency_key}")
        if val:
            return json.loads(val)
    except Exception as e:
        logger.error(f"Redis error getting idempotency key: {e}")
    return None

async def set_idempotency_result(idempotency_key: str, data: dict, expire_seconds: int = 86400):
    if not redis_client:
        return
    try:
        await redis_client.set(f"idem:{idempotency_key}", json.dumps(data), ex=expire_seconds)
    except Exception as e:
        logger.error(f"Redis error setting idempotency key: {e}")

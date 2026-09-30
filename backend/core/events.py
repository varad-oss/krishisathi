"""Structured domain events (one JSON log line each) for intelligence, diagnosis, feedback and interop.

Only ids, categories, counts, timings and statuses are logged: never images, free text, tokens or exact
coordinates. The request id ties an event to the access log line written by RequestContextMiddleware.
"""
import json
import logging

from core.errors import request_id_var

logger = logging.getLogger("krishisathi.events")


def log_event(event: str, **fields) -> None:
    try:
        logger.info(json.dumps({"event": event, "request_id": request_id_var.get(), **fields}, default=str, ensure_ascii=False))
    except Exception:  # observability must never break a request
        logger.exception("Could not log event %s", event)

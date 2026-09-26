"""ASGI middleware: request IDs, access logging, security headers, last-resort error envelope."""
import json
import logging
import time

from core.errors import error_body, request_id_var, resolve_request_id

logger = logging.getLogger("krishisathi.access")

SECURITY_HEADERS = [
    (b"x-content-type-options", b"nosniff"),
    (b"x-frame-options", b"DENY"),
    (b"referrer-policy", b"strict-origin-when-cross-origin"),
    (b"permissions-policy", b"camera=(), microphone=(), geolocation=()"),
    (b"cross-origin-opener-policy", b"same-origin"),
]


class RequestContextMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers") or [])
        request_id = resolve_request_id(headers.get(b"x-request-id", b"").decode("latin-1") or None)
        token = request_id_var.set(request_id)
        start = time.perf_counter()
        status_holder = {"status": 500, "started": False}

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_holder["status"] = message["status"]
                status_holder["started"] = True
                raw = list(message.get("headers", []))
                raw.append((b"x-request-id", request_id.encode()))
                raw.extend(SECURITY_HEADERS)
                message["headers"] = raw
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            logger.exception("Unhandled error request_id=%s path=%s", request_id, scope.get("path"))
            if not status_holder["started"]:
                body = json.dumps(error_body(500, "INTERNAL_ERROR", "An unexpected error occurred.")).encode()
                await send_wrapper({
                    "type": "http.response.start",
                    "status": 500,
                    "headers": [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode())],
                })
                await send({"type": "http.response.body", "body": body})
        finally:
            logger.info(
                "request_id=%s method=%s path=%s status=%s latency_ms=%.1f",
                request_id,
                scope.get("method"),
                scope.get("path"),
                status_holder["status"],
                (time.perf_counter() - start) * 1000,
            )
            request_id_var.reset(token)

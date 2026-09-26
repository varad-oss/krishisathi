"""Consistent API error envelope.

Every error response has the shape:

    {"error": {"code": "SERVICE_UNAVAILABLE", "message": "...", "request_id": "...", "retryable": true}}

Messages are safe for end users; internal exception text is only logged.
"""
import logging
import re
import uuid
from contextvars import ContextVar

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from models.exceptions import ServiceUnavailableException

logger = logging.getLogger(__name__)

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")
_SAFE_REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")

_STATUS_CODES = {
    400: ("INVALID_INPUT", False),
    401: ("UNAUTHORIZED", False),
    403: ("FORBIDDEN", False),
    404: ("NOT_FOUND", False),
    405: ("METHOD_NOT_ALLOWED", False),
    413: ("PAYLOAD_TOO_LARGE", False),
    415: ("UNSUPPORTED_MEDIA_TYPE", False),
    422: ("INVALID_INPUT", False),
    429: ("RATE_LIMITED", True),
    500: ("INTERNAL_ERROR", True),
    501: ("NOT_IMPLEMENTED", False),
    502: ("UPSTREAM_ERROR", True),
    503: ("SERVICE_UNAVAILABLE", True),
    504: ("TIMEOUT", True),
}


class ApiError(HTTPException):
    """HTTPException carrying an explicit machine-readable code."""

    def __init__(self, status_code: int, code: str, message: str, retryable: bool | None = None, headers: dict | None = None):
        super().__init__(status_code=status_code, detail=message, headers=headers)
        self.code = code
        self.message = message
        self.retryable = _STATUS_CODES.get(status_code, ("", False))[1] if retryable is None else retryable


def resolve_request_id(incoming: str | None) -> str:
    if incoming and _SAFE_REQUEST_ID.match(incoming):
        return incoming
    return uuid.uuid4().hex


def error_body(status_code: int, code: str | None, message: str, retryable: bool | None = None) -> dict:
    default_code, default_retryable = _STATUS_CODES.get(status_code, ("ERROR", False))
    return {
        "error": {
            "code": code or default_code,
            "message": message,
            "request_id": request_id_var.get(),
            "retryable": default_retryable if retryable is None else retryable,
        }
    }


def _from_detail(status_code: int, detail) -> tuple[str | None, str]:
    """Accepts legacy `detail` shapes: a string, or {"error": "...", "message": "..."}."""
    if isinstance(detail, dict):
        code = detail.get("error")
        return (code.upper() if isinstance(code, str) else None), str(detail.get("message") or "Request failed.")
    if isinstance(detail, str) and detail:
        return None, detail
    return None, "Request failed."


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def _api_error(request: Request, exc: ApiError):
        return JSONResponse(error_body(exc.status_code, exc.code, exc.message, exc.retryable), status_code=exc.status_code, headers=exc.headers)

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(request: Request, exc: StarletteHTTPException):
        code, message = _from_detail(exc.status_code, exc.detail)
        return JSONResponse(error_body(exc.status_code, code, message), status_code=exc.status_code, headers=getattr(exc, "headers", None))

    @app.exception_handler(RequestValidationError)
    async def _validation_error(request: Request, exc: RequestValidationError):
        fields = []
        for err in exc.errors()[:10]:
            loc = ".".join(str(p) for p in err.get("loc", []) if p not in ("body", "query", "form"))
            msg = str(err.get("msg", "invalid"))
            fields.append({"field": loc, "message": msg})
        body = error_body(422, "INVALID_INPUT", "Some of the submitted information is invalid.")
        body["error"]["fields"] = fields
        return JSONResponse(body, status_code=422)

    @app.exception_handler(ServiceUnavailableException)
    async def _service_unavailable(request: Request, exc: ServiceUnavailableException):
        return JSONResponse(error_body(503, "SERVICE_UNAVAILABLE", exc.message), status_code=503)

    # Unhandled exceptions are turned into a 500 envelope by RequestContextMiddleware.

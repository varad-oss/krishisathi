import logging

import jwt
from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from config import settings
from core.errors import ApiError

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


class Principal(BaseModel):
    user_id: str
    role: str


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Security(security)) -> Principal:
    """Validates an HS256 JWT signed with settings.JWT_SECRET.

    Fails closed: when no secret is configured, authenticated endpoints are disabled
    rather than accepting arbitrary tokens.
    """
    if not settings.JWT_SECRET:
        raise ApiError(503, "AUTH_NOT_CONFIGURED", "Authenticated publishing is not configured on this server.", retryable=False)
    if credentials is None:
        raise ApiError(401, "UNAUTHORIZED", "Authentication required.")

    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise ApiError(401, "TOKEN_EXPIRED", "Token expired.")
    except jwt.PyJWTError:
        raise ApiError(401, "UNAUTHORIZED", "Invalid token.")

    user_id = payload.get("sub")
    if not user_id:
        raise ApiError(401, "UNAUTHORIZED", "Invalid token: missing subject.")
    return Principal(user_id=str(user_id), role=str(payload.get("role", "user")))


def require_system_role(principal: Principal = Depends(get_current_user)) -> Principal:
    if principal.role not in ("system", "admin"):
        raise ApiError(403, "FORBIDDEN", "Forbidden: insufficient privileges.")
    return principal

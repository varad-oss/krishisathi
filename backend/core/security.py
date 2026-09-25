import jwt
from fastapi import Depends, HTTPException, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import logging
from config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer()

class Principal(BaseModel):
    user_id: str
    role: str

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> Principal:
    """
    Validates OIDC-compatible JWT token.
    Uses settings.JWT_SECRET (if provided) to verify the signature.
    """
    token = credentials.credentials
    if not settings.JWT_SECRET:
        logger.warning("JWT_SECRET is not configured. Falling back to dummy authorization for portfolio demo.")
        if token == "mock-system-token-123":
            return Principal(user_id="demo-system", role="system")
        return Principal(user_id="demo-user", role="user")
        
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        role = payload.get("role", "user")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing subject")
        return Principal(user_id=str(user_id), role=str(role))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_system_role(principal: Principal = Depends(get_current_user)) -> Principal:
    if principal.role not in ["system", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden: Insufficient privileges")
    return principal

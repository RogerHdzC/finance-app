from fastapi import Request
from app.exceptions.base import ForbiddenError
from app.core.config import settings

def _require_allowed_origin(request: Request) -> None:
    if not settings.enforce_origin:
        return
    if not settings.allowed_origins:
        return

    origin = request.headers.get("origin")
    if origin is None:
        raise ForbiddenError(code="ORIGIN_REQUIRED", detail="Origin header required.")
    if origin not in settings.allowed_origins:
        raise ForbiddenError(code="ORIGIN_NOT_ALLOWED", detail="Origin not allowed.")
from __future__ import annotations
import os
from dataclasses import dataclass
from app.exceptions.base import InternalServerError

def _parse_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "y", "on")

def _parse_csv(value: str) -> list[str]:
    # Soporta: "a,b,c" o "a, b, c"
    if not value:
        return []
    return [x.strip() for x in value.split(",") if x.strip()]

@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "dev")
    database_url: str = os.getenv("DATABASE_URL", "")
    
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "")
    jwt_access_token_expires_seconds: int = int(os.getenv("JWT_EXPIRATION_DELTA_SECONDS", "3600"))
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_issuer: str = os.getenv("JWT_ISSUER", "finance_api")
    jwt_audience: str = os.getenv("JWT_AUDIENCE", "finance_api_users")
    
    jwt_refresh_token_expires_seconds: int = int(os.getenv("JWT_REFRESH_EXPIRATION_SECONDS", str(30 * 24 * 3600)))
    jwt_refresh_rotate: bool = os.getenv("JWT_REFRESH_ROTATE", "true").lower() in ("1", "true", "yes")
    
    allowed_origins: list[str] = tuple(_parse_csv(os.getenv("ALLOWED_ORIGINS", "")))
    allowed_hosts: list[str] = tuple(_parse_csv(os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")))
    enforce_origin: bool = _parse_bool(os.getenv("ENFORCE_ORIGIN", "false"), default=False)
    max_body_bytes: int = int(os.getenv("MAX_BODY_BYTES", "1000000"))

settings = Settings()

def validate_settings() -> None:
    missing: list[str] = []

    if not settings.database_url:
        missing.append("DATABASE_URL")
    if not settings.jwt_secret_key:
        missing.append("JWT_SECRET_KEY")
        
    if settings.app_env in ("prod", "production"):
        if not settings.allowed_hosts:
            missing.append("ALLOWED_HOSTS")

    if missing:
        raise InternalServerError(
            code="CONFIG_ERROR",
            detail="Missing required environment variables.",
            meta={"missing": missing},
        )

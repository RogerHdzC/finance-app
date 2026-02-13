import hmac
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.refresh_token import RefreshToken
from app.exceptions.base import UnauthorizedError, ConflictError

def _now() -> datetime:
    return datetime.now(tz=timezone.utc)

def _as_utc_aware(dt: datetime) -> datetime:
    # SQLite puede devolverte naive incluso si declaras timezone=True
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def hash_refresh_token(token: str) -> str:
    return hmac.new(
        settings.jwt_secret_key.encode("utf-8"),
        token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

def mint_refresh_token() -> str:
    return "rft_" + secrets.token_urlsafe(48)

class RefreshTokenService:
    @staticmethod
    def issue(db: Session, *, user_id: UUID) -> str:
        plain = mint_refresh_token()
        token_hash = hash_refresh_token(plain)

        issued_at = _now()
        expires_at = issued_at + timedelta(seconds=settings.jwt_refresh_token_expires_seconds)

        row = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            issued_at=issued_at,
            expires_at=expires_at,
            revoked_at=None,
            replaced_by_id=None,
        )
        db.add(row)
        db.commit()
        return plain

    @staticmethod
    def verify(db: Session, *, refresh_token_plain: str) -> RefreshToken:
        token_hash = hash_refresh_token(refresh_token_plain)
        row: RefreshToken | None = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

        if not row:
            raise UnauthorizedError(code="UNAUTHORIZED", detail="Invalid refresh token.")

        if row.revoked_at is not None:
            raise ConflictError(code="CONFLICT", detail="Refresh token has been revoked.")

        if _as_utc_aware(row.expires_at) <= _now():
            raise UnauthorizedError(code="UNAUTHORIZED", detail="Invalid refresh token.")

        return row

    @staticmethod
    def rotate(db: Session, *, row: RefreshToken) -> str:
        # Create new token
        new_plain = mint_refresh_token()
        new_hash = hash_refresh_token(new_plain)

        issued_at = _now()
        expires_at = issued_at + timedelta(seconds=settings.jwt_refresh_token_expires_seconds)

        new_row = RefreshToken(
            user_id=row.user_id,
            token_hash=new_hash,
            issued_at=issued_at,
            expires_at=expires_at,
            revoked_at=None,
            replaced_by_id=None,
        )
        db.add(new_row)

        # Revoke old token and link
        row.revoked_at = _now()
        row.replaced_by_id = new_row.id

        db.commit()
        return new_plain

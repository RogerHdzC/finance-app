from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.exceptions.base import UnauthorizedError

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from uuid import UUID

from app.services.auth import AuthService
from app.models.user import User

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
        
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not token:
        raise UnauthorizedError(code="UNAUTHORIZED", detail="Missing or invalid token.")

    user_id: UUID = AuthService.verify_access_token(token)
    user = db.get(User, user_id)

    if not user:
        raise UnauthorizedError(code="UNAUTHORIZED", detail="Invalid authentication credentials.")

    return user
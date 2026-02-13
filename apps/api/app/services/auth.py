from __future__ import annotations

import jwt
from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import exists, or_

from app.core.config import settings
from app.core.security import pwd_context
from app.exceptions.user import UsernameAlreadyExistsError, EmailAlreadyExistsError
from app.exceptions.auth import AuthenticationError, PasswordTooWeakError
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.refresh_tokens import RefreshTokenService


class AuthService:
    _SPECIALS = set("!@#$%^&*()-_=+[]{}|;:'\",.<>?/")

    @staticmethod
    def validate_password(password: str) -> None:
        """
        Validate password policy.
        Raises PasswordTooWeakError if it doesn't comply.
        """
        errors = []

        if len(password) < 8:
            errors.append({"field": "password", "reason": "Must be at least 8 characters long."})

        if not any(c.isupper() for c in password):
            errors.append({"field": "password", "reason": "Must include at least one uppercase letter."})

        if not any(c.islower() for c in password):
            errors.append({"field": "password", "reason": "Must include at least one lowercase letter."})

        if not any(c.isdigit() for c in password):
            errors.append({"field": "password", "reason": "Must include at least one digit."})

        if not any(c in AuthService._SPECIALS for c in password):
            errors.append({"field": "password", "reason": "Must include at least one special character."})

        if errors:
            raise PasswordTooWeakError(errors=errors)

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, password_hash: str) -> bool:
        return pwd_context.verify(plain_password, password_hash)

    @staticmethod
    def create_access_token(*, user_id: UUID, expires_in_seconds: Optional[int] = None) -> tuple[str, int]:
        """
        Create a signed JWT access token.
        """
        now = datetime.now(tz=timezone.utc)
        exp_seconds = expires_in_seconds or settings.jwt_access_token_expires_seconds

        payload = {
            "sub": str(user_id),                      
            "iat": int(now.timestamp()),              
            "exp": int((now + timedelta(seconds=exp_seconds)).timestamp()),
            "iss": settings.jwt_issuer,               
            "aud": settings.jwt_audience,             
        }

        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        return token, exp_seconds

    @staticmethod
    def verify_access_token(token: str) -> UUID:
        """
        Verify JWT and return user_id (UUID) if valid.
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
                issuer=getattr(settings, "jwt_issuer", None) or None,
                audience=getattr(settings, "jwt_audience", None) or None,
                options={
                    "require": ["exp", "iat", "sub"],
                },
            )
            sub = payload.get("sub")
            if not sub:
                raise AuthenticationError(detail="Token missing subject.")
            return UUID(sub)

        except jwt.ExpiredSignatureError:
            raise AuthenticationError(detail="Token has expired.")
        except (jwt.InvalidTokenError, ValueError):
            raise AuthenticationError(detail="Invalid token.")

    @staticmethod
    def create_user(db: Session, data: UserCreate) -> User:
        """
        Create a new user with the provided data.
        Checks for username/email uniqueness and password strength.
        """
        username_taken = db.query(exists().where(User.username == data.username)).scalar()
        if username_taken:
            raise UsernameAlreadyExistsError()

        email_taken = db.query(exists().where(User.email == data.email)).scalar()
        if email_taken:
            raise EmailAlreadyExistsError()

        AuthService.validate_password(data.password)

        user = User(
            name=data.name,
            lastname=data.lastname,
            username=data.username,
            email=data.email,
            password_hash=AuthService.hash_password(data.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(db: Session, identifier: str, password: str) -> Tuple[User, str, int, str]:
        """
        Authenticate a user by username or email and password.
        Returns the user object and an access token if authentication is successful.
        """
        user = db.query(User).filter(or_(User.username == identifier, User.email == identifier)).first()
        if not user or not AuthService.verify_password(password, user.password_hash):
            raise AuthenticationError(detail="Invalid credentials.")

        access_token, expires_in = AuthService.create_access_token(user_id=user.id)
        refresh_token = RefreshTokenService.issue(db=db, user_id=user.id)

        return user, access_token, expires_in, refresh_token

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> tuple[str, int, str]:
        row = RefreshTokenService.verify(db=db, refresh_token_plain=refresh_token)

        access_token, expires_in = AuthService.create_access_token(user_id=row.user_id)

        if settings.jwt_refresh_rotate:
            new_refresh = RefreshTokenService.rotate(db=db, row=row)
        else:
            new_refresh = refresh_token

        return access_token, expires_in, new_refresh

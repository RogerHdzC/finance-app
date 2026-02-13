from __future__ import annotations
from dataclasses import dataclass, field
from app.exceptions.base import NotFoundError, BadRequestError, UnauthorizedError, ValidationError
from typing import Any, Dict, List

@dataclass
class AuthenticationError(UnauthorizedError):
    """Raised when authentication fails."""
    code: str = "auth.authentication_failed"
    detail: str = "Invalid username or password."
    
@dataclass
class TokenExpiredError(NotFoundError):
    """Raised when a token has expired."""
    code: str = "auth.token_expired"
    detail: str = "The authentication token has expired."
    
@dataclass
class TokenInvalidError(NotFoundError):
    """Raised when a token is invalid."""
    code: str = "auth.token_invalid"
    detail: str = "The authentication token is invalid."
    
@dataclass
class UserNotAuthenticatedError(NotFoundError):
    """Raised when a user is not authenticated."""
    code: str = "auth.user_not_authenticated"
    detail: str = "User is not authenticated."
    
@dataclass
class UserNotAuthorizedError(NotFoundError):
    """Raised when a user is not authorized to perform an action."""
    code: str = "auth.user_not_authorized"
    detail: str = "User is not authorized to perform this action."

@dataclass
class PasswordTooWeakError(ValidationError):
    meta: Dict[str, Any] = field(default_factory=dict)

    def __init__(self, *, errors: List[Dict[str, str]]):
        super().__init__()
        self.meta = {"errors": errors}
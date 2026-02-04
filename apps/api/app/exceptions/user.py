from __future__ import annotations
from dataclasses import dataclass
from app.exceptions.base import ConflictError, NotFoundError

@dataclass
class UsernameAlreadyExistsError(ConflictError):
    """Raised when a username already exists."""
    code: str = "user.username_already_exists"
    detail: str = "The username is already taken."
    
@dataclass
class EmailAlreadyExistsError(ConflictError):
    """Raised when an email already exists."""
    code: str = "user.email_already_exists"
    detail: str = "The email is already registered."
    
@dataclass
class UserNotFoundError(NotFoundError):
    """Raised when a user is not found."""
    code: str = "user.not_found"
    detail: str = "The requested user does not exist."
    

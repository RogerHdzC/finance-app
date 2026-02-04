from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

@dataclass
class DomainError(Exception):
    """Base class for all domain-level errors."""
    code: str = "domain_error"
    detail: str = "A domain error occurred."
    meta: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return self.detail

@dataclass
class BadRequestError(DomainError):
    """Raised when a bad request is made."""
    code: str = "bad_request"
    detail: str = "The request was invalid or cannot be served."
    
@dataclass
class NotFoundError(DomainError):
    """Raised when a requested resource is not found."""
    code: str = "not_found"
    detail: str = "The requested resource was not found."

@dataclass
class ConflictError(DomainError):
    """Raised when a resource already exists."""
    code: str = "conflict"
    detail: str = "The resource already exists."

@dataclass
class UnauthorizedError(DomainError):
    """Raised when authentication is required and has failed or has not yet been provided."""
    code: str = "unauthorized"
    detail: str = "Authentication is required and has failed or has not yet been provided."
    
@dataclass
class ForbiddenError(DomainError):
    """Raised when the user does not have permission to access the requested resource."""
    code: str = "forbidden"
    detail: str = "You do not have permission to access this resource."
    
@dataclass
class InternalServerError(DomainError):
    """Raised when an internal server error occurs."""
    code: str = "internal_server_error"
    detail: str = "An internal server error occurred."
    

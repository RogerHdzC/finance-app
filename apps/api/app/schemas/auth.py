from __future__ import annotations
from pydantic import Field, BaseModel, ConfigDict
from typing import Literal
from uuid import UUID

from app.schemas.user import UserRead

class AuthPayload(BaseModel):
    """
    Docstring para AuthPayload
    Used for user authentication.
    """
    identifier: str = Field(..., min_length=3, max_length=64, description="Username or email")
    password: str = Field(..., min_length=8, max_length=255)
    model_config = ConfigDict(from_attributes=True)

class AuthResponse(BaseModel):
    """
    Docstring para AuthResponse
    Standard response model for authentication endpoints.
    """
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="Opaque refresh token (store client-side securely)")
    token_type: Literal["Bearer", "bearer"] = "Bearer"
    expires_in: int = Field(..., description="Access token TTL in seconds")
    user: UserRead
    
class RefreshPayload(BaseModel):
    """
    Docstring para RefreshPayload
    Payload for token refresh endpoint.
    """
    refresh_token: str = Field(..., min_length=20, description="Refresh token issued during login")
    
class RefreshResponse(BaseModel):
    """
    Docstring para RefreshResponse
    Response model for token refresh endpoint.
    """
    access_token: str
    refresh_token: str = Field(..., description="New refresh token if rotation is enabled")
    token_type: Literal["Bearer", "bearer"] = "Bearer"
    expires_in: int = Field(..., description="Seconds until expiration")
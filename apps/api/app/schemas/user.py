from pydantic import Field, EmailStr, BaseModel, ConfigDict
from typing import List
from uuid import UUID
from datetime import datetime
from app.schemas.timeStamp import TimeStampBase

class UserCreate(BaseModel):
    """
    Docstring para UserCreate
    Used for creating a new user.
    """
    name: str = Field(..., min_length=1, max_length=50)
    lastname: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=3, max_length =32)
    email: EmailStr = Field(..., min_length=11, max_length =50)
    password: str = Field(..., min_length=8, max_length=255)
    model_config = ConfigDict(from_attributes=True)
    
class UserRead(TimeStampBase):
    """
    Docstring para UserRead
    Used for reading user information.
    """
    id: UUID
    name: str
    lastname: str
    username: str
    email: str

class PageMeta(BaseModel):
    total: int
    limit: int
    offset: int
    total_pages: int

class UsersResponse(BaseModel):
    """
    Docstring para UsersResponse
    Standard response model for user-related endpoints.
    """
    user: List[UserRead] = Field(default_factory=list, description="List of users")
    meta: PageMeta

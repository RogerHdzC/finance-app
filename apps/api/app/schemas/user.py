from pydantic import Field, EmailStr, BaseModel, ConfigDict
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

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List 

from app.core.deps import get_db
from app.core.openapi import COMMON_ERROR_RESPONSES
from app.schemas.user import (UserCreate, UserRead)
from app.services.user import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses = COMMON_ERROR_RESPONSES
)

@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db)
) -> UserRead:
    """
    Create a new user.
    """
    
    return UserService.create_user(db=db, data=payload)

@router.get(
    "",
    response_model=List[UserRead],
    status_code=status.HTTP_200_OK
)
def get_users(
    db: Session = Depends(get_db)
) -> List[UserRead]:
    """
    Retrieve all users.
    """
    return UserService.get_users(db=db)


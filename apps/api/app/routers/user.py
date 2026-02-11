from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List 
from uuid import UUID

from app.core.deps import get_db
from app.core.openapi import COMMON_ERROR_RESPONSES
from app.schemas.user import (UserCreate, UserRead, UsersResponse)
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

@router.delete(
    "/{user_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a user by their ID.
    """
    return UserService.delete_user(db=db, user_id=user_id)

@router.get(
    "",
    response_model=UsersResponse,
    status_code=status.HTTP_200_OK
)
def get_users(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
) -> UsersResponse:
    """
    Retrieve all users and number of total pages.
    """
    users, total, total_pages = UserService.get_users(db=db, limit=limit, offset=offset)
    return UsersResponse(
        user=users,
        meta={
            "total": total,
            "limit": limit,
            "offset": offset,
            "total_pages": total_pages
        }
    )

@router.get(
    "/{user_id}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK
)
def get_user_by_id(
    user_id: UUID,
    db: Session = Depends(get_db)
) -> UserRead:
    """
    Retrieve a user by their ID.
    """
    return UserService.get_user_by_id(db=db, user_id=user_id)
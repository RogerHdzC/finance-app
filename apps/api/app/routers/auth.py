from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.openapi import COMMON_ERROR_RESPONSES
from app.services.auth import AuthService
from app.schemas.user import UserCreate, UserRead
from app.schemas.auth import AuthPayload, AuthResponse, RefreshPayload, RefreshResponse
from app.core.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses = COMMON_ERROR_RESPONSES
)

@router.post(
    "/register",
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
    
    return AuthService.create_user(db=db, data=payload)

@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK
)
def login(
    payload: AuthPayload,
    db: Session = Depends(get_db)
) -> AuthResponse:
    """
    Authenticate a user and return an access token.
    """
    user, jwt_token, expires_in, refresh_token = AuthService.authenticate_user(
    db=db,
    identifier=payload.identifier,
    password=payload.password,
    )
    return AuthResponse(
    access_token=jwt_token,
    refresh_token=refresh_token,
    token_type="Bearer",
    expires_in=expires_in,
    user=user,
    )
    
@router.post(
    "/refresh",
    response_model=RefreshResponse,
    status_code=status.HTTP_200_OK
)
def refresh(
    payload: RefreshPayload,
    db: Session = Depends(get_db)
) -> RefreshResponse:
    """
    Refresh an access token using a refresh token.
    """
    access_token, expires_in, new_refresh = AuthService.refresh_access_token(
        db=db,
        refresh_token=payload.refresh_token,
    )

    return RefreshResponse(
        access_token=access_token,
        refresh_token=new_refresh,
        token_type="Bearer",
        expires_in=expires_in,
    )
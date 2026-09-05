from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_roles
from app.auth.security import create_access_token, verify_password
from app.config import get_settings
from app.database import get_db
from app.models import User
from app.schemas.auth import LogoutResponse, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), database: Session = Depends(get_db)) -> TokenResponse:
    user = database.query(User).filter(User.email == form_data.username.strip().lower()).first()
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")
    settings = get_settings()
    return TokenResponse(
        access_token=create_access_token(str(user.id), user.role.name),
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserResponse)
def current_user(user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        role=user.role.name,
        created_at=user.created_at,
    )


@router.post("/logout", response_model=LogoutResponse)
def logout(user: User = Depends(get_current_user)) -> LogoutResponse:
    return LogoutResponse(message=f"Session cleared for {user.email}. Discard the access token on the client.")


@router.get("/admin-check", response_model=UserResponse)
def admin_check(user: User = Depends(require_roles("ADMIN"))) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        role=user.role.name,
        created_at=user.created_at,
    )

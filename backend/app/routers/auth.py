from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_roles
from app.auth.security import create_access_token, verify_password
from app.config import get_settings
from app.database import get_db
from app.models import User
from app.schemas.auth import LogoutResponse, TokenResponse, UserResponse
from app.services.audit import record_security_event

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    database: Session = Depends(get_db),
) -> TokenResponse:
    user = database.query(User).filter(User.email == form_data.username.strip().lower()).first()
    client_ip = request.client.host if request.client else None
    password_too_long = len(form_data.password.encode("utf-8")) > 72
    if user is None or password_too_long or not verify_password(form_data.password, user.hashed_password) or not user.is_active:
        record_security_event(
            database,
            "LOGIN_FAILURE",
            "Failed sign-in attempt",
            actor_id=user.id if user else None,
            ip_address=client_ip,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    record_security_event(database, "LOGIN_SUCCESS", "Successful sign-in", actor_id=user.id, ip_address=client_ip)
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
def logout(request: Request, user: User = Depends(get_current_user), database: Session = Depends(get_db)) -> LogoutResponse:
    record_security_event(
        database,
        "LOGOUT",
        "User logged out",
        actor_id=user.id,
        ip_address=request.client.host if request.client else None,
    )
    return LogoutResponse(message="Session cleared. Discard the access token on the client.")


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

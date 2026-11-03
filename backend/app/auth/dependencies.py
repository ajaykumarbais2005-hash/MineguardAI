from collections.abc import Callable

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload

from app.auth.security import decode_access_token
from app.database import get_db
from app.models import User
from app.services.audit import record_security_event

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_current_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    database: Session = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    client_ip = request.client.host if request.client else None
    if token is None:
        record_security_event(database, "AUTH_FAILURE", "Missing bearer token", ip_address=client_ip)
        raise credentials_error

    try:
        payload = decode_access_token(token)
        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject.isdecimal():
            raise ValueError("Invalid token subject")
        user_id = int(subject)
        if user_id < 1:
            raise ValueError("Invalid token subject")
    except (TypeError, ValueError, jwt.InvalidTokenError) as error:
        record_security_event(database, "AUTH_FAILURE", "Invalid bearer token", ip_address=client_ip)
        raise credentials_error from error

    user = database.query(User).options(joinedload(User.role)).filter(User.id == user_id).first()
    if user is None:
        record_security_event(database, "AUTH_FAILURE", "Token subject does not identify an active account", ip_address=client_ip)
        raise credentials_error
    if not user.is_active:
        record_security_event(database, "AUTH_FAILURE", "Inactive account authentication attempt", actor_id=user.id, ip_address=client_ip)
        raise credentials_error
    return user


def require_roles(*allowed_roles: str) -> Callable:
    def role_dependency(
        request: Request,
        database: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role.name not in allowed_roles:
            record_security_event(
                database,
                "ACCESS_DENIED",
                f"Role {current_user.role.name} denied access to {request.url.path}",
                actor_id=current_user.id,
                ip_address=request.client.host if request.client else None,
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user

    return role_dependency

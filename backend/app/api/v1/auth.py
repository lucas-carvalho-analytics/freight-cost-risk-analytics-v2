from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.auth.security import create_access_token, verify_password
from app.core.config import settings
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserMeResponse


router = APIRouter(prefix="/auth")


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    email = payload.email.strip().lower()
    user = db.scalar(select(User).where(User.email == email))

    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user.",
        )

    access_token = create_access_token(subject=str(user.id))

    db.add(
        AuditLog(
            user_id=user.id,
            action="login_success",
            endpoint="/api/v1/auth/login",
        )
    )
    db.commit()

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserMeResponse)
def read_current_user(
    current_user: User = Depends(get_current_active_user),
) -> UserMeResponse:
    return UserMeResponse.model_validate(current_user)

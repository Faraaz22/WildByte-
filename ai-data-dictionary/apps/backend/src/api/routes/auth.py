"""Auth routes: login, logout, me."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from src.api.dependencies import CurrentUser, get_current_user
from src.config.database import get_db
from src.config.settings import get_settings
from src.models.user import User
from src.schemas.auth import LoginRequest, TokenResponse, UserResponse
from src.utils.auth import create_access_token, verify_password
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """
    Authenticate with username and password.
    Returns a JWT access token. No sign-up; use seeded admin user.
    """
    result = await db.execute(
        select(User).where(
            User.username == body.username,
            User.deleted_at.is_(None),
        )
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )
    user.last_login_at = datetime.now(timezone.utc)

    access_token = create_access_token(subject=user.id)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in_hours=settings.jwt_expiration_hours,
    )


@router.post("/logout")
async def logout() -> dict:
    """
    Logout. Client should discard the token.
    Server does not store tokens; no server-side invalidation.
    """
    return {"message": "Logged out. Discard the token on the client."}


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser) -> UserResponse:
    """Return the current authenticated user."""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role.value,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
    )

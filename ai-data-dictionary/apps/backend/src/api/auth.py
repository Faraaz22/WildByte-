"""Authentication API endpoints."""

from datetime import timedelta
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import get_db
from src.config.settings import get_settings
from src.models.user import User, UserRole
from src.utils.auth import JWTHandler, PasswordHasher

router = APIRouter()
security = HTTPBearer()
settings = get_settings()


# Pydantic schemas
class LoginRequest(BaseModel):
    """Login request payload."""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Refresh token response."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User information response."""

    id: int
    email: str
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool


# Dependency to get current user from token
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token
        db: Database session
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    payload = JWTHandler.decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None or not isinstance(user_id, int):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    return user


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Login endpoint to authenticate user and get tokens.
    
    Args:
        login_data: Login credentials
        db: Database session
        
    Returns:
        Access token, refresh token, and user information
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not PasswordHasher.verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    # Create tokens
    token_data = {"sub": user.id, "email": user.email, "role": user.role.value}
    access_token = JWTHandler.create_access_token(token_data)
    refresh_token = JWTHandler.create_refresh_token({"sub": user.id})
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role.value,
            "is_active": user.is_active,
        },
    )


@router.post("/logout")
async def logout(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Logout endpoint.
    
    Note: Since we're using stateless JWT tokens, actual logout is handled
    client-side by deleting the tokens. This endpoint is here for completeness
    and could be extended to implement token blacklisting if needed.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    return {"message": "Successfully logged out", "user_id": current_user.id}


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_access_token(
    refresh_data: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Refresh access token using a refresh token.
    
    Args:
        refresh_data: Refresh token
        db: Database session
        
    Returns:
        New access token
        
    Raises:
        HTTPException: If refresh token is invalid
    """
    payload = JWTHandler.decode_token(refresh_data.refresh_token)
    
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None or not isinstance(user_id, int):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify user still exists and is active
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create new access token
    token_data = {"sub": user.id, "email": user.email, "role": user.role.value}
    access_token = JWTHandler.create_access_token(token_data)
    
    return RefreshTokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role.value,
        is_active=current_user.is_active,
    )

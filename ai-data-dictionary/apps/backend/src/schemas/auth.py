"""Pydantic schemas for Auth API."""

from pydantic import BaseModel, Field, ConfigDict


class LoginRequest(BaseModel):
    """Login request body."""

    username: str = Field(..., min_length=1, description="Username")
    password: str = Field(..., min_length=1, description="Password")


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in_hours: int = Field(..., description="Token expiry in hours")


class UserResponse(BaseModel):
    """Current user response (no sensitive fields)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    role: str
    full_name: str | None = None
    is_active: bool = True

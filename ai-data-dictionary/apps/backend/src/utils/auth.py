"""Authentication utilities: password hashing and JWT."""

from datetime import datetime, timezone, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from src.config.settings import get_settings

settings = get_settings()


def hash_password(password: str) -> str:
    """Hash a password with bcrypt (cost 12)."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    except Exception:
        return False


def create_access_token(
    subject: str | int,
    *,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Create a JWT access token."""
    if not settings.jwt_secret_key:
        raise ValueError("JWT_SECRET_KEY must be set")
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(hours=settings.jwt_expiration_hours))
    to_encode: dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "type": "access",
    }
    if extra_claims:
        to_encode.update(extra_claims)
    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and validate a JWT; returns payload or None if invalid."""
    if not settings.jwt_secret_key:
        return None
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None

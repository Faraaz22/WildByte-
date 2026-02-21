"""Authentication utilities: password hashing and JWT."""

from datetime import datetime, timezone, timedelta
from typing import Any, Optional

import bcrypt
from jose import JWTError, jwt

from src.config.settings import get_settings

settings = get_settings()


# ---------------------------------------------------------------------------
# Password (used by api/auth.py and scripts/init_db.py as PasswordHasher)
# ---------------------------------------------------------------------------

class PasswordHasher:
    """Password hashing utilities using bcrypt."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password with bcrypt (cost 12)."""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its bcrypt hash."""
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except Exception:
            return False


# ---------------------------------------------------------------------------
# JWT (used by api/auth.py as JWTHandler)
# ---------------------------------------------------------------------------

class JWTHandler:
    """JWT token creation and validation."""

    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create a JWT access token. data should include at least 'sub' (subject)."""
        if not settings.jwt_secret_key:
            raise ValueError("JWT_SECRET_KEY must be set")
        to_encode = data.copy()
        now = datetime.now(timezone.utc)
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(hours=settings.jwt_expiration_hours)
        to_encode.update({"exp": expire, "iat": now, "type": "access"})
        return jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create a JWT refresh token (7-day expiry)."""
        if not settings.jwt_secret_key:
            raise ValueError("JWT_SECRET_KEY must be set")
        to_encode = data.copy()
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=7)
        to_encode.update({"exp": expire, "iat": now, "type": "refresh"})
        return jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """Decode and verify a JWT; returns payload or None if invalid."""
        if not settings.jwt_secret_key:
            return None
        try:
            return jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
        except JWTError:
            return None

    @staticmethod
    def verify_token(token: str) -> bool:
        """Return True if the token is valid."""
        return JWTHandler.decode_token(token) is not None


# ---------------------------------------------------------------------------
# Module-level helpers (for code that prefers functions)
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """Hash a password with bcrypt (cost 12)."""
    return PasswordHasher.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash."""
    return PasswordHasher.verify_password(plain_password, hashed_password)


def create_access_token(
    subject: str | int,
    *,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Create a JWT access token (function API)."""
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


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """Decode and validate an access JWT; returns payload or None if invalid."""
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

"""
ChatFlow - Security & Authentication
"""

from datetime import datetime, timedelta
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(
    subject: str | Any,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict] = None,
) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        "iat": datetime.utcnow(),
    }

    if additional_claims:
        to_encode.update(additional_claims)

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: str | Any,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT refresh token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "iat": datetime.utcnow(),
    }

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_token(token: str, token_type: str = "access") -> Optional[str]:
    """Verify a token and return the subject (user_id)."""
    payload = decode_token(token)
    if payload is None:
        return None
    if payload.get("type") != token_type:
        return None
    return payload.get("sub")


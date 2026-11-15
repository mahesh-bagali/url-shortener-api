
"""Password hashing and JWT authentication helpers."""

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from sqlmodel import Session

from app.config import settings
from app.database.session import get_session
from app.models import User


password_hash = PasswordHash((Argon2Hasher(),))

bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2."""
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its stored hash."""
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    """Create a signed JWT access token for a user."""

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> User:
    """Verify a JWT and return the authenticated user."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise credentials_exception

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
        )

        user_id = int(payload.get("sub", ""))

    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise credentials_exception

    user = session.get(User, user_id)

    if user is None:
        raise credentials_exception

    return user

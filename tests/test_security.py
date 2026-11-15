
from types import SimpleNamespace
from unittest.mock import Mock

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.config import settings
from app.services.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)


class TestPasswordSecurity:

    def test_password_is_hashed(self):
        password = "StrongPassword123!"

        hashed_password = hash_password(password)

        assert hashed_password != password
        assert hashed_password.startswith("$argon2")

    def test_correct_password_is_verified(self):
        password = "StrongPassword123!"
        hashed_password = hash_password(password)

        assert verify_password(password, hashed_password) is True

    def test_incorrect_password_is_rejected(self):
        hashed_password = hash_password("StrongPassword123!")

        assert verify_password("WrongPassword123!", hashed_password) is False


class TestJWTSecurity:

    def test_access_token_is_created(self):
        token = create_access_token(user_id=123)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_access_token_contains_correct_user_id(self):
        token = create_access_token(user_id=123)

        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
        )

        assert payload["sub"] == "123"

    def test_invalid_token_is_rejected(self):
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid.token.value",
        )

        session = Mock()

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials, session)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Could not validate credentials"


class TestCurrentUser:

    def test_missing_credentials_are_rejected(self):
        session = Mock()

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(None, session)

        assert exc_info.value.status_code == 401
        assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}

    def test_nonexistent_user_is_rejected(self):
        token = create_access_token(user_id=999)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token,
        )

        session = Mock()
        session.get.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials, session)

        assert exc_info.value.status_code == 401
        session.get.assert_called_once()

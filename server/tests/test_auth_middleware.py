"""Tests for JWT authentication middleware (Task 2.1).

Validates Requirement 1.5: JWT token-based session management with 7-day expiry.
"""

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from jose import jwt

from app.config import settings
from app.middleware.auth import create_access_token, decode_access_token, get_current_user


class TestCreateAccessToken:
    """Test JWT token creation."""

    def test_creates_valid_token(self):
        user_id = str(uuid.uuid4())
        token = create_access_token(user_id)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_correct_subject(self):
        user_id = str(uuid.uuid4())
        token = create_access_token(user_id)
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        assert payload["sub"] == user_id

    def test_token_has_expiration(self):
        user_id = str(uuid.uuid4())
        token = create_access_token(user_id)
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        assert "exp" in payload

    def test_token_expires_in_7_days(self):
        user_id = str(uuid.uuid4())
        before = datetime.now(timezone.utc).replace(microsecond=0)
        token = create_access_token(user_id)
        after = datetime.now(timezone.utc) + timedelta(seconds=1)

        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        expected_min = before + timedelta(days=7)
        expected_max = after + timedelta(days=7)
        assert expected_min <= exp <= expected_max


class TestDecodeAccessToken:
    """Test JWT token decoding and validation."""

    def test_decodes_valid_token(self):
        user_id = str(uuid.uuid4())
        token = create_access_token(user_id)
        payload = decode_access_token(token)
        assert payload["sub"] == user_id

    def test_raises_on_expired_token(self):
        user_id = str(uuid.uuid4())
        expire = datetime.now(timezone.utc) - timedelta(hours=1)
        payload = {"sub": user_id, "exp": expire}
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)
        assert exc_info.value.status_code == 401
        assert "过期" in exc_info.value.detail

    def test_raises_on_invalid_token(self):
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token("not-a-valid-token")
        assert exc_info.value.status_code == 401
        assert "无效" in exc_info.value.detail

    def test_raises_on_wrong_secret(self):
        user_id = str(uuid.uuid4())
        token = jwt.encode(
            {"sub": user_id, "exp": datetime.now(timezone.utc) + timedelta(days=1)},
            "wrong-secret",
            algorithm=settings.jwt_algorithm,
        )
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)
        assert exc_info.value.status_code == 401


class TestGetCurrentUser:
    """Test get_current_user FastAPI dependency."""

    @pytest.mark.asyncio
    async def test_returns_active_user(self):
        user_id = uuid.uuid4()
        token = create_access_token(str(user_id))

        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.status = "active"
        mock_user.token_invalidated_at = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        credentials = MagicMock()
        credentials.credentials = token

        user = await get_current_user(credentials=credentials, db=mock_db)
        assert user.id == user_id

    @pytest.mark.asyncio
    async def test_raises_on_invalid_token(self):
        mock_db = AsyncMock()
        credentials = MagicMock()
        credentials.credentials = "invalid-token"

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=mock_db)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_raises_when_user_not_found(self):
        user_id = uuid.uuid4()
        token = create_access_token(str(user_id))

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        credentials = MagicMock()
        credentials.credentials = token

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=mock_db)
        assert exc_info.value.status_code == 401
        assert "不存在" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_raises_when_user_disabled(self):
        user_id = uuid.uuid4()
        token = create_access_token(str(user_id))

        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.status = "disabled"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        credentials = MagicMock()
        credentials.credentials = token

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=mock_db)
        assert exc_info.value.status_code == 401
        assert "禁用" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_raises_when_token_missing_sub(self):
        expire = datetime.now(timezone.utc) + timedelta(days=1)
        token = jwt.encode(
            {"exp": expire},
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

        mock_db = AsyncMock()
        credentials = MagicMock()
        credentials.credentials = token

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials, db=mock_db)
        assert exc_info.value.status_code == 401

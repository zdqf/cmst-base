"""Tests for user registration and login API (Task 2.2).

Validates Requirements:
- 1.1: Register with phone + code, return auth token
- 1.2: Login with valid credentials, return auth token
- 1.3: Invalid verification code returns error
- 1.4: Duplicate phone returns "该手机号已注册"
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.auth_service import (
    VALID_SMS_CODE,
    login_user,
    register_user,
    verify_sms_code,
)


# ---------------------------------------------------------------------------
# Schema validation tests
# ---------------------------------------------------------------------------


class TestRegisterRequestSchema:
    def test_valid_request(self):
        req = RegisterRequest(phone="13800138000", code="123456")
        assert req.phone == "13800138000"
        assert req.code == "123456"

    def test_invalid_phone_format(self):
        with pytest.raises(ValueError):
            RegisterRequest(phone="12345", code="123456")

    def test_invalid_phone_prefix(self):
        with pytest.raises(ValueError):
            RegisterRequest(phone="10800138000", code="123456")


class TestLoginRequestSchema:
    def test_valid_request(self):
        req = LoginRequest(phone="13900139000", code="123456")
        assert req.phone == "13900139000"

    def test_invalid_phone(self):
        with pytest.raises(ValueError):
            LoginRequest(phone="abc", code="123456")


class TestTokenResponseSchema:
    def test_default_token_type(self):
        resp = TokenResponse(access_token="some-token")
        assert resp.token_type == "bearer"

    def test_custom_token_type(self):
        resp = TokenResponse(access_token="tok", token_type="custom")
        assert resp.token_type == "custom"


# ---------------------------------------------------------------------------
# Service layer tests
# ---------------------------------------------------------------------------


class TestVerifySmsCode:
    def test_valid_code(self):
        assert verify_sms_code("13800138000", VALID_SMS_CODE) is True

    def test_invalid_code(self):
        assert verify_sms_code("13800138000", "000000") is False

    def test_empty_code(self):
        assert verify_sms_code("13800138000", "") is False


class TestRegisterUser:
    @pytest.mark.asyncio
    async def test_register_success(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        user, token = await register_user(mock_db, "13800138000", VALID_SMS_CODE)
        assert user.phone == "13800138000"
        assert isinstance(token, str)
        assert len(token) > 0
        mock_db.add.assert_called_once()
        mock_db.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_register_invalid_code(self):
        mock_db = AsyncMock()
        with pytest.raises(ValueError, match="验证码无效"):
            await register_user(mock_db, "13800138000", "wrong")

    @pytest.mark.asyncio
    async def test_register_duplicate_phone(self):
        existing_user = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_user

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        with pytest.raises(ValueError, match="该手机号已注册"):
            await register_user(mock_db, "13800138000", VALID_SMS_CODE)


class TestLoginUser:
    @pytest.mark.asyncio
    async def test_login_success(self):
        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()
        mock_user.phone = "13800138000"
        mock_user.last_login_at = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        user, token = await login_user(mock_db, "13800138000", VALID_SMS_CODE)
        assert user.id == mock_user.id
        assert isinstance(token, str)
        assert len(token) > 0
        # last_login_at should be updated
        assert user.last_login_at is not None
        mock_db.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_login_invalid_code(self):
        mock_db = AsyncMock()
        with pytest.raises(ValueError, match="验证码无效"):
            await login_user(mock_db, "13800138000", "wrong")

    @pytest.mark.asyncio
    async def test_login_phone_not_registered(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        with pytest.raises(ValueError, match="该手机号未注册"):
            await login_user(mock_db, "13800138000", VALID_SMS_CODE)


# ---------------------------------------------------------------------------
# Router / endpoint tests
# ---------------------------------------------------------------------------


class TestRegisterEndpoint:
    def test_register_success(self):
        from unittest.mock import patch
        from fastapi.testclient import TestClient
        from app.main import app

        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()
        mock_user.phone = "13800138000"

        with patch("app.routers.auth.register_user", new_callable=AsyncMock) as mock_reg:
            mock_reg.return_value = (mock_user, "fake-jwt-token")
            with patch("app.routers.auth.get_db"):
                client = TestClient(app)
                response = client.post(
                    "/api/v1/auth/register",
                    json={"phone": "13800138000", "code": "123456"},
                )
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["access_token"] == "fake-jwt-token"
        assert body["data"]["token_type"] == "bearer"

    def test_register_invalid_code_error(self):
        from fastapi.testclient import TestClient
        from app.main import app

        with patch("app.routers.auth.register_user", new_callable=AsyncMock) as mock_reg:
            mock_reg.side_effect = ValueError("验证码无效")
            with patch("app.routers.auth.get_db"):
                client = TestClient(app)
                response = client.post(
                    "/api/v1/auth/register",
                    json={"phone": "13800138000", "code": "000000"},
                )
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 400
        assert body["message"] == "验证码无效"

    def test_register_duplicate_phone_error(self):
        from fastapi.testclient import TestClient
        from app.main import app

        with patch("app.routers.auth.register_user", new_callable=AsyncMock) as mock_reg:
            mock_reg.side_effect = ValueError("该手机号已注册")
            with patch("app.routers.auth.get_db"):
                client = TestClient(app)
                response = client.post(
                    "/api/v1/auth/register",
                    json={"phone": "13800138000", "code": "123456"},
                )
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 400
        assert body["message"] == "该手机号已注册"

    def test_register_invalid_phone_returns_422(self):
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.post(
            "/api/v1/auth/register",
            json={"phone": "123", "code": "123456"},
        )
        assert response.status_code == 422


class TestLoginEndpoint:
    def test_login_success(self):
        from fastapi.testclient import TestClient
        from app.main import app

        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()

        with patch("app.routers.auth.login_user", new_callable=AsyncMock) as mock_login:
            mock_login.return_value = (mock_user, "fake-jwt-token")
            with patch("app.routers.auth.get_db"):
                client = TestClient(app)
                response = client.post(
                    "/api/v1/auth/login",
                    json={"phone": "13800138000", "code": "123456"},
                )
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["access_token"] == "fake-jwt-token"

    def test_login_invalid_code_error(self):
        from fastapi.testclient import TestClient
        from app.main import app

        with patch("app.routers.auth.login_user", new_callable=AsyncMock) as mock_login:
            mock_login.side_effect = ValueError("验证码无效")
            with patch("app.routers.auth.get_db"):
                client = TestClient(app)
                response = client.post(
                    "/api/v1/auth/login",
                    json={"phone": "13800138000", "code": "000000"},
                )
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 400
        assert body["message"] == "验证码无效"

    def test_login_phone_not_registered_error(self):
        from fastapi.testclient import TestClient
        from app.main import app

        with patch("app.routers.auth.login_user", new_callable=AsyncMock) as mock_login:
            mock_login.side_effect = ValueError("该手机号未注册")
            with patch("app.routers.auth.get_db"):
                client = TestClient(app)
                response = client.post(
                    "/api/v1/auth/login",
                    json={"phone": "13800138000", "code": "123456"},
                )
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 400
        assert body["message"] == "该手机号未注册"

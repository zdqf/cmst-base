"""Tests for admin password login service (Task 3.2).

Validates Requirements:
- 1.1: Valid phone + correct password returns JWT with user_id, role="admin", iat, exp
- 1.2: Wrong password returns "手机号或密码错误"
- 1.3: Non-admin user rejected with same error message
- 1.6: Password length 6-32 characters (validated at schema level)
- 1.7: Phone format validation (validated at schema level)
- 24.1: bcrypt cost factor >= 12
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from jose import jwt

from app.config import settings
from app.exceptions import AppException
from app.schemas.auth import AdminLoginRequest
from app.services.auth_service import (
    BCRYPT_ROUNDS,
    _hash_password_sync,
    _verify_password_sync,
    admin_login,
)


# ---------------------------------------------------------------------------
# Password hashing tests
# ---------------------------------------------------------------------------


class TestPasswordHashing:
    """Test bcrypt password hashing and verification."""

    def test_hash_password_returns_bcrypt_hash(self):
        hashed = _hash_password_sync("test123")
        assert hashed.startswith("$2b$") or hashed.startswith("$2a$")

    def test_verify_password_correct(self):
        hashed = _hash_password_sync("mypassword")
        assert _verify_password_sync("mypassword", hashed) is True

    def test_verify_password_wrong(self):
        hashed = _hash_password_sync("mypassword")
        assert _verify_password_sync("wrongpassword", hashed) is False

    def test_bcrypt_cost_factor_at_least_12(self):
        """Requirement 24.1: bcrypt cost factor >= 12."""
        hashed = _hash_password_sync("test123")
        # bcrypt hash format: $2b$<rounds>$...
        parts = hashed.split("$")
        rounds = int(parts[2])
        assert rounds >= 12

    def test_hash_password_different_each_time(self):
        """bcrypt should produce different hashes for the same password (salt)."""
        h1 = _hash_password_sync("samepassword")
        h2 = _hash_password_sync("samepassword")
        assert h1 != h2

    def test_bcrypt_rounds_configured(self):
        """Verify the bcrypt rounds constant is >= 12."""
        assert BCRYPT_ROUNDS >= 12


# ---------------------------------------------------------------------------
# Admin login service tests
# ---------------------------------------------------------------------------


class TestAdminLogin:
    """Test admin_login function."""

    def _make_admin_user(self, password: str = "admin123") -> MagicMock:
        """Create a mock admin user with a hashed password."""
        user = MagicMock()
        user.id = uuid.uuid4()
        user.phone = "13800138000"
        user.is_admin = True
        user.password_hash = _hash_password_sync(password)
        user.last_login_at = None
        return user

    def _make_mock_db(self, user=None) -> AsyncMock:
        """Create a mock db session that returns the given user."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user
        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result
        return mock_db

    @pytest.mark.asyncio
    async def test_login_success(self):
        """Requirement 1.1: Valid credentials return (User, JWT)."""
        password = "admin123"
        user = self._make_admin_user(password)
        db = self._make_mock_db(user)

        result_user, token = await admin_login(db, "13800138000", password)

        assert result_user.id == user.id
        assert isinstance(token, str)
        assert len(token) > 0
        db.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_login_success_updates_last_login(self):
        """Success: User.last_login_at should be updated."""
        password = "admin123"
        user = self._make_admin_user(password)
        db = self._make_mock_db(user)

        result_user, _ = await admin_login(db, "13800138000", password)

        assert result_user.last_login_at is not None

    @pytest.mark.asyncio
    async def test_login_success_jwt_contains_required_claims(self):
        """Requirement 1.1: JWT contains sub, role="admin", iat, exp."""
        password = "admin123"
        user = self._make_admin_user(password)
        db = self._make_mock_db(user)

        _, token = await admin_login(db, "13800138000", password)

        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        assert payload["sub"] == str(user.id)
        assert payload["role"] == "admin"
        assert "iat" in payload
        assert "exp" in payload

    @pytest.mark.asyncio
    async def test_login_wrong_password(self):
        """Requirement 1.2: Wrong password raises AppException with generic message."""
        user = self._make_admin_user("correctpassword")
        db = self._make_mock_db(user)

        with pytest.raises(AppException) as exc_info:
            await admin_login(db, "13800138000", "wrongpassword")

        assert exc_info.value.code == 400
        assert exc_info.value.message == "手机号或密码错误"

    @pytest.mark.asyncio
    async def test_login_phone_not_found(self):
        """Requirement 1.2: Non-existent phone raises same generic error."""
        db = self._make_mock_db(None)

        with pytest.raises(AppException) as exc_info:
            await admin_login(db, "13800138000", "anypassword")

        assert exc_info.value.code == 400
        assert exc_info.value.message == "手机号或密码错误"

    @pytest.mark.asyncio
    async def test_login_non_admin_rejected(self):
        """Requirement 1.3: Non-admin user rejected with same error."""
        user = self._make_admin_user("admin123")
        user.is_admin = False
        db = self._make_mock_db(user)

        with pytest.raises(AppException) as exc_info:
            await admin_login(db, "13800138000", "admin123")

        assert exc_info.value.code == 400
        assert exc_info.value.message == "手机号或密码错误"

    @pytest.mark.asyncio
    async def test_login_no_password_set(self):
        """Admin without password_hash should be rejected."""
        user = self._make_admin_user("admin123")
        user.password_hash = None
        db = self._make_mock_db(user)

        with pytest.raises(AppException) as exc_info:
            await admin_login(db, "13800138000", "admin123")

        assert exc_info.value.code == 400
        assert exc_info.value.message == "手机号或密码错误"

    @pytest.mark.asyncio
    async def test_login_empty_password_hash(self):
        """Admin with empty password_hash string should be rejected."""
        user = self._make_admin_user("admin123")
        user.password_hash = ""
        db = self._make_mock_db(user)

        with pytest.raises(AppException) as exc_info:
            await admin_login(db, "13800138000", "admin123")

        assert exc_info.value.code == 400
        assert exc_info.value.message == "手机号或密码错误"

    @pytest.mark.asyncio
    async def test_error_messages_identical(self):
        """All failure paths must return the exact same error message (no info leak)."""
        password = "admin123"
        admin_user = self._make_admin_user(password)
        non_admin_user = self._make_admin_user(password)
        non_admin_user.is_admin = False
        no_pw_user = self._make_admin_user(password)
        no_pw_user.password_hash = None

        error_messages = []

        # Phone not found
        db = self._make_mock_db(None)
        with pytest.raises(AppException) as exc_info:
            await admin_login(db, "13800138000", password)
        error_messages.append(exc_info.value.message)

        # Non-admin
        db = self._make_mock_db(non_admin_user)
        with pytest.raises(AppException) as exc_info:
            await admin_login(db, "13800138000", password)
        error_messages.append(exc_info.value.message)

        # No password set
        db = self._make_mock_db(no_pw_user)
        with pytest.raises(AppException) as exc_info:
            await admin_login(db, "13800138000", password)
        error_messages.append(exc_info.value.message)

        # Wrong password
        db = self._make_mock_db(admin_user)
        with pytest.raises(AppException) as exc_info:
            await admin_login(db, "13800138000", "wrongpw")
        error_messages.append(exc_info.value.message)

        # All messages must be identical
        assert len(set(error_messages)) == 1
        assert error_messages[0] == "手机号或密码错误"

    @pytest.mark.asyncio
    async def test_no_db_changes_on_failure(self):
        """Failure: db.flush should NOT be called."""
        db = self._make_mock_db(None)

        with pytest.raises(AppException):
            await admin_login(db, "13800138000", "anypassword")

        db.flush.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_raises_app_exception_not_value_error(self):
        """Must raise AppException, not ValueError."""
        db = self._make_mock_db(None)

        with pytest.raises(AppException):
            await admin_login(db, "13800138000", "anypassword")

        # Ensure it's NOT a ValueError
        try:
            await admin_login(db, "13800138000", "anypassword")
        except AppException:
            pass
        except ValueError:
            pytest.fail("admin_login should raise AppException, not ValueError")


# ---------------------------------------------------------------------------
# Phone format validation tests (Requirement 1.7)
# ---------------------------------------------------------------------------


class TestPhoneFormatValidation:
    """Test AdminLoginRequest phone format validation: ^1[3-9]\\d{9}$."""

    def test_valid_phone_13x(self):
        req = AdminLoginRequest(phone="13800138000", password="admin123")
        assert req.phone == "13800138000"

    def test_valid_phone_15x(self):
        req = AdminLoginRequest(phone="15912345678", password="admin123")
        assert req.phone == "15912345678"

    def test_valid_phone_19x(self):
        req = AdminLoginRequest(phone="19900001111", password="admin123")
        assert req.phone == "19900001111"

    def test_invalid_phone_starts_with_10(self):
        with pytest.raises(ValueError):
            AdminLoginRequest(phone="10800138000", password="admin123")

    def test_invalid_phone_starts_with_12(self):
        with pytest.raises(ValueError):
            AdminLoginRequest(phone="12800138000", password="admin123")

    def test_invalid_phone_too_short(self):
        with pytest.raises(ValueError):
            AdminLoginRequest(phone="1380013800", password="admin123")

    def test_invalid_phone_too_long(self):
        with pytest.raises(ValueError):
            AdminLoginRequest(phone="138001380001", password="admin123")

    def test_invalid_phone_non_numeric(self):
        with pytest.raises(ValueError):
            AdminLoginRequest(phone="1380013800a", password="admin123")

    def test_invalid_phone_empty(self):
        with pytest.raises(ValueError):
            AdminLoginRequest(phone="", password="admin123")

    def test_invalid_phone_not_starting_with_1(self):
        with pytest.raises(ValueError):
            AdminLoginRequest(phone="23800138000", password="admin123")

    def test_schema_password_min_length(self):
        """Requirement 1.6: Schema rejects password < 6 chars."""
        with pytest.raises(ValueError):
            AdminLoginRequest(phone="13800138000", password="12345")

    def test_schema_password_max_length(self):
        """Requirement 1.6: Schema rejects password > 32 chars."""
        with pytest.raises(ValueError):
            AdminLoginRequest(phone="13800138000", password="a" * 33)

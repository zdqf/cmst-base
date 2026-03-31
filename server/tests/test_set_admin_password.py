"""Tests for set_admin_password service (Task 3.3).

Validates Requirements:
- 1.4: First-time password set uses bcrypt (cost factor >= 12)
- 1.5: Changing existing password requires correct old_password
- 1.6: Password length must be 6-32 characters
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions import AppException, ForbiddenError
from app.services.auth_service import (
    hash_password,
    set_admin_password,
    verify_password,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_admin_user(password: str | None = None) -> MagicMock:
    """Create a mock admin user, optionally with an existing password."""
    user = MagicMock()
    user.id = uuid.uuid4()
    user.phone = "13800138000"
    user.is_admin = True
    user.password_hash = hash_password(password) if password else None
    user.updated_at = None
    return user


def _make_db() -> AsyncMock:
    return AsyncMock()


# ---------------------------------------------------------------------------
# First-time password setup (Requirement 1.4)
# ---------------------------------------------------------------------------


class TestFirstTimePasswordSetup:
    """When user.password_hash is None, old_password is not required."""

    @pytest.mark.asyncio
    async def test_set_password_first_time(self):
        user = _make_admin_user()
        db = _make_db()

        await set_admin_password(db, user, "newpass123")

        assert user.password_hash is not None
        assert verify_password("newpass123", user.password_hash)
        db.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_set_password_first_time_with_old_password_ignored(self):
        """Providing old_password when none exists should still succeed."""
        user = _make_admin_user()
        db = _make_db()

        await set_admin_password(db, user, "newpass123", old_password="anything")

        assert verify_password("newpass123", user.password_hash)

    @pytest.mark.asyncio
    async def test_password_stored_as_bcrypt(self):
        """Requirement 1.4: password hashed with bcrypt, cost >= 12."""
        user = _make_admin_user()
        db = _make_db()

        await set_admin_password(db, user, "secure123")

        assert user.password_hash.startswith("$2b$") or user.password_hash.startswith("$2a$")
        rounds = int(user.password_hash.split("$")[2])
        assert rounds >= 12


# ---------------------------------------------------------------------------
# Password change (Requirement 1.5)
# ---------------------------------------------------------------------------


class TestPasswordChange:
    """When user.password_hash exists, old_password must be provided and correct."""

    @pytest.mark.asyncio
    async def test_change_password_success(self):
        old_pw = "oldpass123"
        user = _make_admin_user(old_pw)
        db = _make_db()

        await set_admin_password(db, user, "newpass456", old_password=old_pw)

        assert verify_password("newpass456", user.password_hash)
        assert not verify_password(old_pw, user.password_hash)

    @pytest.mark.asyncio
    async def test_change_password_missing_old_password(self):
        """Requirement 1.5: old_password required when password_hash exists."""
        user = _make_admin_user("existing123")
        db = _make_db()

        with pytest.raises(AppException) as exc_info:
            await set_admin_password(db, user, "newpass456")

        assert exc_info.value.code == 400
        assert "旧密码" in exc_info.value.message
        db.flush.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_change_password_wrong_old_password(self):
        user = _make_admin_user("correct123")
        db = _make_db()

        with pytest.raises(AppException) as exc_info:
            await set_admin_password(db, user, "newpass456", old_password="wrong")

        assert exc_info.value.code == 400
        assert "旧密码" in exc_info.value.message
        db.flush.assert_not_awaited()


# ---------------------------------------------------------------------------
# Password length validation (Requirement 1.6)
# ---------------------------------------------------------------------------


class TestPasswordLengthValidation:
    """Password must be 6-32 characters."""

    @pytest.mark.asyncio
    async def test_password_too_short(self):
        user = _make_admin_user()
        db = _make_db()

        with pytest.raises(AppException) as exc_info:
            await set_admin_password(db, user, "12345")  # 5 chars

        assert exc_info.value.code == 400
        db.flush.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_password_too_long(self):
        user = _make_admin_user()
        db = _make_db()

        with pytest.raises(AppException) as exc_info:
            await set_admin_password(db, user, "a" * 33)  # 33 chars

        assert exc_info.value.code == 400
        db.flush.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_password_min_boundary(self):
        """6 characters should be accepted."""
        user = _make_admin_user()
        db = _make_db()

        await set_admin_password(db, user, "123456")

        assert verify_password("123456", user.password_hash)

    @pytest.mark.asyncio
    async def test_password_max_boundary(self):
        """32 characters should be accepted."""
        user = _make_admin_user()
        db = _make_db()
        pw = "a" * 32

        await set_admin_password(db, user, pw)

        assert verify_password(pw, user.password_hash)


# ---------------------------------------------------------------------------
# Non-admin rejection
# ---------------------------------------------------------------------------


class TestNonAdminRejection:
    """Non-admin users cannot set passwords."""

    @pytest.mark.asyncio
    async def test_non_admin_rejected(self):
        user = _make_admin_user()
        user.is_admin = False
        db = _make_db()

        with pytest.raises(ForbiddenError):
            await set_admin_password(db, user, "newpass123")

        db.flush.assert_not_awaited()

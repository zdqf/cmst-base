"""Property-based tests for admin password login (Task 3.6).

Uses hypothesis to verify universal correctness properties of admin_login.

**Validates: Requirements 1.1, 1.2, 1.3**
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from hypothesis import given, settings, assume, HealthCheck
from hypothesis import strategies as st

from app.exceptions import AppException
from app.services.auth_service import admin_login


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# Passwords: printable ASCII strings, length 6-32 (matching Requirement 1.6)
password_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "P", "S")),
    min_size=6,
    max_size=32,
)

# Valid Chinese phone numbers matching ^1[3-9]\d{9}$
phone_strategy = st.from_regex(r"^1[3-9]\d{9}$", fullmatch=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_admin_user(phone: str, hashed_pw: str) -> MagicMock:
    """Create a mock admin user with a pre-set password hash."""
    user = MagicMock()
    user.id = uuid.uuid4()
    user.phone = phone
    user.is_admin = True
    user.password_hash = hashed_pw
    user.last_login_at = None
    return user


def _make_mock_db(user=None) -> AsyncMock:
    """Create a mock async db session returning the given user on query."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_result
    return mock_db


# ---------------------------------------------------------------------------
# P1: 正确密码必须登录成功
# ∀ user ∈ Users, password ∈ Strings:
#   user.is_admin ∧ user.password_hash == bcrypt(password)
#   ⟹ admin_login(user.phone, password) returns (user, valid_token)
#
# **Validates: Requirements 1.1**
# ---------------------------------------------------------------------------


class TestP1CorrectPasswordMustSucceed:
    """P1: Correct password must result in successful login."""

    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    @given(password=password_strategy, phone=phone_strategy)
    @pytest.mark.asyncio
    async def test_correct_password_always_succeeds(self, password: str, phone: str):
        """**Validates: Requirements 1.1**

        For any admin user, supplying the correct password to admin_login
        must return the user and a non-empty JWT token string.

        We patch verify_password to return True (simulating bcrypt match)
        and hash_password to return a sentinel, keeping the property test
        fast while still exercising the full admin_login control flow.
        """
        sentinel_hash = "hashed:" + password
        user = _make_admin_user(phone, sentinel_hash)
        db = _make_mock_db(user)

        with patch(
            "app.services.auth_service.verify_password", return_value=True
        ):
            result_user, token = await admin_login(db, phone, password)

        assert result_user.id == user.id
        assert isinstance(token, str) and len(token) > 0


# ---------------------------------------------------------------------------
# P2: 错误密码必须登录失败
# ∀ user ∈ Users, wrong_password ∈ Strings:
#   bcrypt(wrong_password) ≠ user.password_hash
#   ⟹ admin_login(user.phone, wrong_password) raises AppException
#
# **Validates: Requirements 1.2**
# ---------------------------------------------------------------------------


class TestP2WrongPasswordMustFail:
    """P2: Wrong password must result in login failure."""

    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    @given(
        correct_password=password_strategy,
        wrong_password=password_strategy,
        phone=phone_strategy,
    )
    @pytest.mark.asyncio
    async def test_wrong_password_always_raises(
        self, correct_password: str, wrong_password: str, phone: str
    ):
        """**Validates: Requirements 1.2**

        For any admin user, supplying a password different from the stored
        one must raise an AppException with code 400 and the generic error
        message "手机号或密码错误".

        We patch verify_password to return False (simulating bcrypt mismatch).
        """
        assume(correct_password != wrong_password)

        sentinel_hash = "hashed:" + correct_password
        user = _make_admin_user(phone, sentinel_hash)
        db = _make_mock_db(user)

        with patch(
            "app.services.auth_service.verify_password", return_value=False
        ):
            with pytest.raises(AppException) as exc_info:
                await admin_login(db, phone, wrong_password)

        assert exc_info.value.code == 400
        assert exc_info.value.message == "手机号或密码错误"


# ---------------------------------------------------------------------------
# P3: 非管理员不能密码登录
# ∀ user ∈ Users:
#   ¬user.is_admin ⟹ admin_login(user.phone, any_password) raises AppException
#
# **Validates: Requirements 1.3**
# ---------------------------------------------------------------------------


class TestP3NonAdminCannotLogin:
    """P3: Non-admin users must be rejected regardless of password."""

    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    @given(password=password_strategy, phone=phone_strategy)
    @pytest.mark.asyncio
    async def test_non_admin_always_rejected(self, password: str, phone: str):
        """**Validates: Requirements 1.3**

        For any non-admin user, admin_login must raise an AppException
        with code 400, even if the password would otherwise be correct.
        The error message must be the generic "手机号或密码错误" to avoid
        leaking whether the account exists.
        """
        sentinel_hash = "hashed:" + password
        user = _make_admin_user(phone, sentinel_hash)
        user.is_admin = False  # make non-admin
        db = _make_mock_db(user)

        # verify_password should never be reached for non-admin,
        # but we don't patch it — the function should reject before checking.
        with pytest.raises(AppException) as exc_info:
            await admin_login(db, phone, password)

        assert exc_info.value.code == 400
        assert exc_info.value.message == "手机号或密码错误"

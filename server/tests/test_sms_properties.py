"""Property-based tests for SMS verification code service (Task 4.5).

Uses hypothesis to verify universal correctness properties of SMS code
send and verify logic.

**Validates: Requirements 3.2, 3.5, 4.1, 4.4**
"""

from unittest.mock import AsyncMock, patch

import pytest
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from app.exceptions import RateLimitError
from app.services.sms_service import send_sms_code, verify_sms_code


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# Valid Chinese phone numbers matching ^1[3-9]\d{9}$
phone_strategy = st.from_regex(r"^1[3-9]\d{9}$", fullmatch=True)

# 6-digit numeric verification codes
code_strategy = st.from_regex(r"^\d{6}$", fullmatch=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_mock_redis(data: dict | None = None):
    """Create a mock Redis client with an in-memory dict backend."""
    store = data if data is not None else {}
    mock = AsyncMock()

    async def _get(key):
        return store.get(key)

    async def _set(key, value, ex=None):
        store[key] = str(value)

    async def _exists(key):
        return key in store

    async def _incr(key):
        store[key] = str(int(store.get(key, "0")) + 1)
        return int(store[key])

    async def _delete(key):
        store.pop(key, None)

    mock.get = AsyncMock(side_effect=_get)
    mock.set = AsyncMock(side_effect=_set)
    mock.exists = AsyncMock(side_effect=_exists)
    mock.incr = AsyncMock(side_effect=_incr)
    mock.delete = AsyncMock(side_effect=_delete)
    mock._store = store
    return mock


def _make_mock_provider(success: bool = True):
    """Create a mock SMS provider that always succeeds (or fails)."""
    provider = AsyncMock()
    provider.send_code = AsyncMock(return_value=success)
    return provider


# ---------------------------------------------------------------------------
# P4: 验证码一次性使用
# ∀ phone, code:
#   verify_sms_code(phone, code) == True
#   ⟹ verify_sms_code(phone, code) == False  (第二次调用)
#
# **Validates: Requirements 3.2, 4.1, 4.4**
# ---------------------------------------------------------------------------


class TestP4OneTimeUse:
    """P4: Verification code can only be used once."""

    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    @given(phone=phone_strategy, code=code_strategy)
    @pytest.mark.asyncio
    async def test_code_invalid_after_first_use(self, phone: str, code: str):
        """**Validates: Requirements 3.2, 4.1, 4.4**

        For any phone and code, if verify_sms_code returns True on the
        first call, the second call with the same phone and code must
        return False. This ensures one-time use semantics.
        """
        code_key = f"sms_code:{phone}"
        mock_redis = _make_mock_redis({code_key: code})

        with patch(
            "app.services.sms_service.is_redis_available",
            new_callable=AsyncMock,
            return_value=True,
        ), patch(
            "app.services.sms_service.get_redis",
            return_value=mock_redis,
        ):
            first_result = await verify_sms_code(phone, code)
            second_result = await verify_sms_code(phone, code)

        assert first_result is True
        assert second_result is False


# ---------------------------------------------------------------------------
# P5: 验证码过期失效
# ∀ phone, code, t:
#   send_sms_code(phone) at time t
#   ∧ now() > t + 300s
#   ⟹ verify_sms_code(phone, code) == False
#
# **Validates: Requirements 3.5**
# ---------------------------------------------------------------------------


class TestP5ExpiryInvalidation:
    """P5: Expired verification codes must fail verification."""

    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    @given(phone=phone_strategy, code=code_strategy)
    @pytest.mark.asyncio
    async def test_expired_code_returns_false(self, phone: str, code: str):
        """**Validates: Requirements 3.5**

        For any phone and code, if the code is not present in Redis
        (simulating expiry after 300s TTL), verify_sms_code must
        return False.

        We simulate expiry by providing an empty Redis store — the code
        key does not exist, which is exactly what happens after TTL expires.
        """
        mock_redis = _make_mock_redis({})  # empty = code expired

        with patch(
            "app.services.sms_service.is_redis_available",
            new_callable=AsyncMock,
            return_value=True,
        ), patch(
            "app.services.sms_service.get_redis",
            return_value=mock_redis,
        ):
            result = await verify_sms_code(phone, code)

        assert result is False


# ---------------------------------------------------------------------------
# P6: 频率限制
# ∀ phone:
#   send_sms_code(phone) at time t
#   ∧ now() < t + 60s
#   ⟹ send_sms_code(phone) raises RateLimitError
#
# **Validates: Requirements 4.4**
# ---------------------------------------------------------------------------


class TestP6RateLimit:
    """P6: Sending within 60s rate window must raise RateLimitError."""

    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    @given(phone=phone_strategy)
    @pytest.mark.asyncio
    async def test_rate_limit_within_60s(self, phone: str):
        """**Validates: Requirements 4.4**

        For any valid phone number, if the rate limit key already exists
        in Redis (simulating a send within the last 60 seconds),
        send_sms_code must raise a RateLimitError with HTTP 429.
        """
        rate_key = f"sms_rate:{phone}"
        mock_redis = _make_mock_redis({rate_key: "1"})

        with patch(
            "app.services.sms_service.is_redis_available",
            new_callable=AsyncMock,
            return_value=True,
        ), patch(
            "app.services.sms_service.get_redis",
            return_value=mock_redis,
        ):
            with pytest.raises(RateLimitError) as exc_info:
                await send_sms_code(phone)

        assert exc_info.value.code == 429
        assert "60秒" in exc_info.value.message

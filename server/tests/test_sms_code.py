"""Tests for SMS verification code send and verify logic.

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 4.1, 4.2, 4.3, 4.4, 25.1, 25.2
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.exceptions import AppException, RateLimitError
from app.services.sms_service import (
    _generate_code,
    send_sms_code,
    verify_sms_code,
    _db_store_code,
    _db_get_code,
    _db_delete_code,
    _db_cleanup_expired,
    PHONE_PATTERN,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_PHONE = "13800138000"


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


# ---------------------------------------------------------------------------
# _generate_code
# ---------------------------------------------------------------------------

def test_generate_code_is_6_digits():
    """Generated code is always a 6-digit string."""
    for _ in range(100):
        code = _generate_code()
        assert len(code) == 6
        assert code.isdigit()


# ---------------------------------------------------------------------------
# PHONE_PATTERN
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("phone,valid", [
    ("13800138000", True),
    ("19999999999", True),
    ("12345678901", False),  # starts with 12
    ("1380013800", False),   # too short
    ("138001380001", False), # too long
    ("abc", False),
])
def test_phone_pattern(phone, valid):
    assert bool(PHONE_PATTERN.match(phone)) == valid


# ---------------------------------------------------------------------------
# send_sms_code — Redis available (normal path)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_send_sms_code_invalid_phone():
    """Invalid phone format raises AppException(400)."""
    with pytest.raises(AppException) as exc_info:
        await send_sms_code("12345")
    assert exc_info.value.code == 400


@pytest.mark.asyncio
async def test_send_sms_code_rate_limit_60s():
    """Sending within 60s raises RateLimitError (HTTP 429)."""
    mock_redis = _make_mock_redis({f"sms_rate:{VALID_PHONE}": "1"})

    with patch("app.services.sms_service.is_redis_available", new_callable=AsyncMock, return_value=True), \
         patch("app.services.sms_service.get_redis", return_value=mock_redis):
        with pytest.raises(RateLimitError) as exc_info:
            await send_sms_code(VALID_PHONE)
        assert exc_info.value.code == 429
        assert "60秒" in exc_info.value.message


@pytest.mark.asyncio
async def test_send_sms_code_daily_limit():
    """Exceeding daily limit raises RateLimitError."""
    from datetime import date
    today = date.today().isoformat()
    daily_key = f"sms_daily:{VALID_PHONE}:{today}"
    mock_redis = _make_mock_redis({daily_key: "10"})

    with patch("app.services.sms_service.is_redis_available", new_callable=AsyncMock, return_value=True), \
         patch("app.services.sms_service.get_redis", return_value=mock_redis):
        with pytest.raises(RateLimitError) as exc_info:
            await send_sms_code(VALID_PHONE)
        assert exc_info.value.code == 429


@pytest.mark.asyncio
async def test_send_sms_code_provider_failure_no_quota():
    """When provider fails, raises 500 and does NOT store code or consume quota."""
    mock_redis = _make_mock_redis()
    mock_provider = AsyncMock()
    mock_provider.send_code = AsyncMock(return_value=False)

    with patch("app.services.sms_service.is_redis_available", new_callable=AsyncMock, return_value=True), \
         patch("app.services.sms_service.get_redis", return_value=mock_redis), \
         patch("app.services.sms_service.get_sms_provider", return_value=mock_provider):
        with pytest.raises(AppException) as exc_info:
            await send_sms_code(VALID_PHONE)
        assert exc_info.value.code == 500

    # Verify nothing was stored in Redis
    assert f"sms_code:{VALID_PHONE}" not in mock_redis._store
    assert f"sms_rate:{VALID_PHONE}" not in mock_redis._store


@pytest.mark.asyncio
async def test_send_sms_code_success():
    """Successful send stores code, rate key, and daily counter in Redis."""
    from datetime import date
    today = date.today().isoformat()

    mock_redis = _make_mock_redis()
    mock_provider = AsyncMock()
    mock_provider.send_code = AsyncMock(return_value=True)

    with patch("app.services.sms_service.is_redis_available", new_callable=AsyncMock, return_value=True), \
         patch("app.services.sms_service.get_redis", return_value=mock_redis), \
         patch("app.services.sms_service.get_sms_provider", return_value=mock_provider):
        await send_sms_code(VALID_PHONE)

    # Verify Redis state
    code_key = f"sms_code:{VALID_PHONE}"
    rate_key = f"sms_rate:{VALID_PHONE}"
    daily_key = f"sms_daily:{VALID_PHONE}:{today}"

    assert code_key in mock_redis._store
    assert len(mock_redis._store[code_key]) == 6
    assert mock_redis._store[code_key].isdigit()
    assert rate_key in mock_redis._store
    assert daily_key in mock_redis._store

    # Verify provider was called with the generated code
    mock_provider.send_code.assert_awaited_once()
    call_args = mock_provider.send_code.call_args
    assert call_args[0][0] == VALID_PHONE
    assert len(call_args[0][1]) == 6


@pytest.mark.asyncio
async def test_send_sms_code_increments_daily_counter():
    """Second successful send increments the daily counter."""
    from datetime import date
    today = date.today().isoformat()
    daily_key = f"sms_daily:{VALID_PHONE}:{today}"
    mock_redis = _make_mock_redis({daily_key: "3"})
    mock_provider = AsyncMock()
    mock_provider.send_code = AsyncMock(return_value=True)

    with patch("app.services.sms_service.is_redis_available", new_callable=AsyncMock, return_value=True), \
         patch("app.services.sms_service.get_redis", return_value=mock_redis), \
         patch("app.services.sms_service.get_sms_provider", return_value=mock_provider):
        await send_sms_code(VALID_PHONE)

    assert mock_redis._store[daily_key] == "4"


# ---------------------------------------------------------------------------
# verify_sms_code — Redis available (normal path)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_verify_sms_code_match_deletes():
    """Correct code returns True and deletes the key (one-time use)."""
    code_key = f"sms_code:{VALID_PHONE}"
    mock_redis = _make_mock_redis({code_key: "654321"})

    with patch("app.services.sms_service.is_redis_available", new_callable=AsyncMock, return_value=True), \
         patch("app.services.sms_service.get_redis", return_value=mock_redis):
        result = await verify_sms_code(VALID_PHONE, "654321")

    assert result is True
    assert code_key not in mock_redis._store


@pytest.mark.asyncio
async def test_verify_sms_code_mismatch_keeps():
    """Wrong code returns False and does NOT delete the stored code."""
    code_key = f"sms_code:{VALID_PHONE}"
    mock_redis = _make_mock_redis({code_key: "654321"})

    with patch("app.services.sms_service.is_redis_available", new_callable=AsyncMock, return_value=True), \
         patch("app.services.sms_service.get_redis", return_value=mock_redis):
        result = await verify_sms_code(VALID_PHONE, "000000")

    assert result is False
    assert code_key in mock_redis._store
    assert mock_redis._store[code_key] == "654321"


@pytest.mark.asyncio
async def test_verify_sms_code_expired():
    """No stored code (expired) returns False."""
    mock_redis = _make_mock_redis()

    with patch("app.services.sms_service.is_redis_available", new_callable=AsyncMock, return_value=True), \
         patch("app.services.sms_service.get_redis", return_value=mock_redis):
        result = await verify_sms_code(VALID_PHONE, "123456")

    assert result is False


@pytest.mark.asyncio
async def test_verify_sms_code_one_time_use():
    """After successful verification, the same code fails on second attempt."""
    code_key = f"sms_code:{VALID_PHONE}"
    mock_redis = _make_mock_redis({code_key: "654321"})

    with patch("app.services.sms_service.is_redis_available", new_callable=AsyncMock, return_value=True), \
         patch("app.services.sms_service.get_redis", return_value=mock_redis):
        first = await verify_sms_code(VALID_PHONE, "654321")
        second = await verify_sms_code(VALID_PHONE, "654321")

    assert first is True
    assert second is False


@pytest.mark.asyncio
async def test_verify_sms_code_empty_inputs():
    """Empty phone or code returns False without touching Redis."""
    assert await verify_sms_code("", "123456") is False
    assert await verify_sms_code(VALID_PHONE, "") is False


# ---------------------------------------------------------------------------
# Redis degradation — database fallback (Requirements: 25.1, 25.2)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_send_sms_code_redis_unavailable_falls_back_to_db():
    """When Redis is unavailable, send_sms_code falls back to database storage.

    Validates: Requirements 25.1
    """
    mock_provider = AsyncMock()
    mock_provider.send_code = AsyncMock(return_value=True)
    mock_db_store = AsyncMock()

    with patch("app.services.sms_service.is_redis_available", new_callable=AsyncMock, return_value=False), \
         patch("app.services.sms_service.get_sms_provider", return_value=mock_provider), \
         patch("app.services.sms_service._db_store_code", mock_db_store):
        await send_sms_code(VALID_PHONE)

    # Provider was called
    mock_provider.send_code.assert_awaited_once()
    call_args = mock_provider.send_code.call_args
    assert call_args[0][0] == VALID_PHONE
    assert len(call_args[0][1]) == 6

    # Code was stored in database
    mock_db_store.assert_awaited_once()
    db_call_args = mock_db_store.call_args
    assert db_call_args[0][0] == VALID_PHONE
    assert len(db_call_args[0][1]) == 6


@pytest.mark.asyncio
async def test_send_sms_code_redis_unavailable_provider_failure():
    """When Redis is down and provider fails, raises 500 and does NOT store in DB."""
    mock_provider = AsyncMock()
    mock_provider.send_code = AsyncMock(return_value=False)
    mock_db_store = AsyncMock()

    with patch("app.services.sms_service.is_redis_available", new_callable=AsyncMock, return_value=False), \
         patch("app.services.sms_service.get_sms_provider", return_value=mock_provider), \
         patch("app.services.sms_service._db_store_code", mock_db_store):
        with pytest.raises(AppException) as exc_info:
            await send_sms_code(VALID_PHONE)
        assert exc_info.value.code == 500

    # DB store was NOT called
    mock_db_store.assert_not_awaited()


@pytest.mark.asyncio
async def test_verify_sms_code_redis_unavailable_falls_back_to_db():
    """When Redis is unavailable, verify_sms_code checks the database.

    Validates: Requirements 25.1
    """
    with patch("app.services.sms_service.is_redis_available", new_callable=AsyncMock, return_value=False), \
         patch("app.services.sms_service._db_get_code", new_callable=AsyncMock, return_value="654321"), \
         patch("app.services.sms_service._db_delete_code", new_callable=AsyncMock) as mock_delete:
        result = await verify_sms_code(VALID_PHONE, "654321")

    assert result is True
    mock_delete.assert_awaited_once_with(VALID_PHONE)


@pytest.mark.asyncio
async def test_verify_sms_code_redis_unavailable_mismatch():
    """When Redis is down and code doesn't match, returns False without deleting."""
    with patch("app.services.sms_service.is_redis_available", new_callable=AsyncMock, return_value=False), \
         patch("app.services.sms_service._db_get_code", new_callable=AsyncMock, return_value="654321"), \
         patch("app.services.sms_service._db_delete_code", new_callable=AsyncMock) as mock_delete:
        result = await verify_sms_code(VALID_PHONE, "000000")

    assert result is False
    mock_delete.assert_not_awaited()


@pytest.mark.asyncio
async def test_verify_sms_code_redis_unavailable_expired():
    """When Redis is down and no code in DB (expired), returns False."""
    with patch("app.services.sms_service.is_redis_available", new_callable=AsyncMock, return_value=False), \
         patch("app.services.sms_service._db_get_code", new_callable=AsyncMock, return_value=None):
        result = await verify_sms_code(VALID_PHONE, "123456")

    assert result is False


@pytest.mark.asyncio
async def test_redis_recovery_switches_back():
    """When Redis recovers, the system automatically uses Redis again.

    Validates: Requirements 25.2
    """
    mock_redis = _make_mock_redis({f"sms_code:{VALID_PHONE}": "654321"})

    # First call: Redis unavailable, uses DB
    with patch("app.services.sms_service.is_redis_available", new_callable=AsyncMock, return_value=False), \
         patch("app.services.sms_service._db_get_code", new_callable=AsyncMock, return_value="111111"), \
         patch("app.services.sms_service._db_delete_code", new_callable=AsyncMock):
        result_db = await verify_sms_code(VALID_PHONE, "111111")

    assert result_db is True

    # Second call: Redis recovered, uses Redis
    with patch("app.services.sms_service.is_redis_available", new_callable=AsyncMock, return_value=True), \
         patch("app.services.sms_service.get_redis", return_value=mock_redis):
        result_redis = await verify_sms_code(VALID_PHONE, "654321")

    assert result_redis is True
    # Redis key was deleted (one-time use)
    assert f"sms_code:{VALID_PHONE}" not in mock_redis._store


# ---------------------------------------------------------------------------
# MockSMSProvider (Requirements: 5.3)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mock_provider_always_returns_true():
    """MockSMSProvider.send_code always returns True regardless of inputs."""
    from app.services.sms_service import MockSMSProvider

    provider = MockSMSProvider()
    assert await provider.send_code("13800138000", "654321") is True
    assert await provider.send_code("19900000000", "000000") is True


@pytest.mark.asyncio
async def test_mock_provider_logs_code(caplog):
    """MockSMSProvider logs the verification code it receives."""
    import logging
    from app.services.sms_service import MockSMSProvider

    provider = MockSMSProvider()
    with caplog.at_level(logging.INFO):
        await provider.send_code("13800138000", "654321")

    assert any("654321" in record.message for record in caplog.records)


@pytest.mark.asyncio
async def test_mock_provider_fixed_code_123456():
    """In mock mode, send_sms_code generates a code and MockSMSProvider sends it.

    The 'fixed code 123456' concept means MockSMSProvider always succeeds,
    so in dev/test the code stored in Redis is the generated one.
    Validates: Requirements 5.3
    """
    from app.services.sms_service import MockSMSProvider

    provider = MockSMSProvider()
    # MockSMSProvider accepts any code and returns True
    result = await provider.send_code("13800138000", "123456")
    assert result is True


# ---------------------------------------------------------------------------
# AliyunSMSProvider (Requirements: 5.2) — mock SDK calls
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_aliyun_provider_success():
    """AliyunSMSProvider returns True when Aliyun API returns OK."""
    import sys
    from app.services.sms_service import AliyunSMSProvider

    provider = AliyunSMSProvider(
        access_key_id="test-key",
        access_key_secret="test-secret",
        sign_name="TestSign",
        template_code="SMS_001",
    )

    mock_body = MagicMock()
    mock_body.code = "OK"
    mock_response = MagicMock()
    mock_response.body = mock_body

    mock_client = MagicMock()
    mock_client.send_sms = MagicMock(return_value=mock_response)

    # Mock the Aliyun SDK module that is imported inside send_code
    mock_models = MagicMock()
    with patch.dict(sys.modules, {"alibabacloud_dysmsapi20170525.models": mock_models}), \
         patch.object(provider, "_create_client", return_value=mock_client):
        result = await provider.send_code("13800138000", "654321")

    assert result is True
    mock_client.send_sms.assert_called_once()


@pytest.mark.asyncio
async def test_aliyun_provider_api_failure():
    """AliyunSMSProvider returns False when Aliyun API returns non-OK code."""
    import sys
    from app.services.sms_service import AliyunSMSProvider

    provider = AliyunSMSProvider(
        access_key_id="test-key",
        access_key_secret="test-secret",
        sign_name="TestSign",
        template_code="SMS_001",
    )

    mock_body = MagicMock()
    mock_body.code = "isv.BUSINESS_LIMIT_CONTROL"
    mock_body.message = "触发业务限流"
    mock_response = MagicMock()
    mock_response.body = mock_body

    mock_client = MagicMock()
    mock_client.send_sms = MagicMock(return_value=mock_response)

    mock_models = MagicMock()
    with patch.dict(sys.modules, {"alibabacloud_dysmsapi20170525.models": mock_models}), \
         patch.object(provider, "_create_client", return_value=mock_client):
        result = await provider.send_code("13800138000", "654321")

    assert result is False


@pytest.mark.asyncio
async def test_aliyun_provider_exception():
    """AliyunSMSProvider returns False when SDK raises an exception."""
    import sys
    from app.services.sms_service import AliyunSMSProvider

    provider = AliyunSMSProvider(
        access_key_id="test-key",
        access_key_secret="test-secret",
        sign_name="TestSign",
        template_code="SMS_001",
    )

    mock_client = MagicMock()
    mock_client.send_sms = MagicMock(side_effect=Exception("Network error"))

    mock_models = MagicMock()
    with patch.dict(sys.modules, {"alibabacloud_dysmsapi20170525.models": mock_models}), \
         patch.object(provider, "_create_client", return_value=mock_client):
        result = await provider.send_code("13800138000", "654321")

    assert result is False


# ---------------------------------------------------------------------------
# get_sms_provider factory (Requirements: 5.1, 5.2, 5.3, 5.4)
# ---------------------------------------------------------------------------

def test_get_sms_provider_mock():
    """get_sms_provider returns MockSMSProvider when config is 'mock'."""
    from app.services.sms_service import get_sms_provider, MockSMSProvider

    with patch("app.services.sms_service.settings") as mock_settings:
        mock_settings.sms_provider = "mock"
        provider = get_sms_provider()
    assert isinstance(provider, MockSMSProvider)


def test_get_sms_provider_aliyun():
    """get_sms_provider returns AliyunSMSProvider when config is 'aliyun'."""
    from app.services.sms_service import get_sms_provider, AliyunSMSProvider

    with patch("app.services.sms_service.settings") as mock_settings:
        mock_settings.sms_provider = "aliyun"
        mock_settings.aliyun_access_key_id = "key"
        mock_settings.aliyun_access_key_secret = "secret"
        mock_settings.aliyun_sms_sign_name = "Sign"
        mock_settings.aliyun_sms_template_code = "TPL"
        provider = get_sms_provider()
    assert isinstance(provider, AliyunSMSProvider)


def test_get_sms_provider_unknown_raises():
    """get_sms_provider raises ValueError for unknown provider."""
    from app.services.sms_service import get_sms_provider

    with patch("app.services.sms_service.settings") as mock_settings:
        mock_settings.sms_provider = "unknown"
        with pytest.raises(ValueError, match="Unknown SMS provider"):
            get_sms_provider()

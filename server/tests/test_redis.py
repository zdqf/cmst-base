"""Tests for Redis connection management and graceful degradation."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from redis.exceptions import ConnectionError as RedisConnectionError

import app.redis as redis_mod


@pytest.fixture(autouse=True)
def _reset_redis_state():
    """Reset module-level state before each test."""
    redis_mod._pool = None
    redis_mod._redis = None
    redis_mod._available = False
    yield
    redis_mod._pool = None
    redis_mod._redis = None
    redis_mod._available = False


# ---------------------------------------------------------------------------
# init_redis
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_init_redis_success():
    """init_redis sets _available=True when Redis is reachable."""
    mock_redis = AsyncMock()
    mock_redis.ping = AsyncMock(return_value=True)

    with patch("app.redis.ConnectionPool.from_url") as mock_pool_cls, \
         patch("app.redis.Redis", return_value=mock_redis):
        mock_pool_cls.return_value = MagicMock()
        await redis_mod.init_redis()

    assert redis_mod._available is True
    assert redis_mod._redis is mock_redis


@pytest.mark.asyncio
async def test_init_redis_failure_degrades_gracefully():
    """init_redis sets _available=False and logs warning when Redis is unreachable."""
    with patch("app.redis.ConnectionPool.from_url", side_effect=RedisConnectionError("refused")):
        await redis_mod.init_redis()

    assert redis_mod._available is False


# ---------------------------------------------------------------------------
# close_redis
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_close_redis():
    """close_redis cleans up client and pool."""
    mock_redis = AsyncMock()
    mock_pool = AsyncMock()
    redis_mod._redis = mock_redis
    redis_mod._pool = mock_pool
    redis_mod._available = True

    await redis_mod.close_redis()

    mock_redis.aclose.assert_awaited_once()
    mock_pool.aclose.assert_awaited_once()
    assert redis_mod._redis is None
    assert redis_mod._pool is None
    assert redis_mod._available is False


@pytest.mark.asyncio
async def test_close_redis_when_not_initialized():
    """close_redis is safe to call when nothing was initialized."""
    await redis_mod.close_redis()
    assert redis_mod._available is False


# ---------------------------------------------------------------------------
# get_redis
# ---------------------------------------------------------------------------

def test_get_redis_returns_client():
    """get_redis returns the current Redis client."""
    sentinel = object()
    redis_mod._redis = sentinel
    assert redis_mod.get_redis() is sentinel


def test_get_redis_returns_none_when_not_initialized():
    """get_redis returns None before init."""
    assert redis_mod.get_redis() is None


# ---------------------------------------------------------------------------
# is_redis_available
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_is_redis_available_true():
    """is_redis_available returns True when ping succeeds."""
    mock_redis = AsyncMock()
    mock_redis.ping = AsyncMock(return_value=True)
    redis_mod._redis = mock_redis
    redis_mod._available = False  # was down

    result = await redis_mod.is_redis_available()

    assert result is True
    assert redis_mod._available is True


@pytest.mark.asyncio
async def test_is_redis_available_false_on_error():
    """is_redis_available returns False and logs warning when ping fails."""
    mock_redis = AsyncMock()
    mock_redis.ping = AsyncMock(side_effect=RedisConnectionError("gone"))
    redis_mod._redis = mock_redis
    redis_mod._available = True  # was up

    result = await redis_mod.is_redis_available()

    assert result is False
    assert redis_mod._available is False


@pytest.mark.asyncio
async def test_is_redis_available_false_when_no_client():
    """is_redis_available returns False when client is None."""
    redis_mod._redis = None

    result = await redis_mod.is_redis_available()

    assert result is False


# ---------------------------------------------------------------------------
# redis_available (sync)
# ---------------------------------------------------------------------------

def test_redis_available_reflects_state():
    """redis_available returns the last-known availability flag."""
    redis_mod._available = True
    assert redis_mod.redis_available() is True

    redis_mod._available = False
    assert redis_mod.redis_available() is False


# ---------------------------------------------------------------------------
# Auto-recovery scenario
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_auto_recovery_after_reconnect():
    """When Redis comes back, is_redis_available flips _available to True."""
    mock_redis = AsyncMock()
    # First call fails, second succeeds
    mock_redis.ping = AsyncMock(side_effect=[RedisConnectionError("down"), True])
    redis_mod._redis = mock_redis
    redis_mod._available = True

    # Goes down
    result1 = await redis_mod.is_redis_available()
    assert result1 is False
    assert redis_mod._available is False

    # Comes back
    result2 = await redis_mod.is_redis_available()
    assert result2 is True
    assert redis_mod._available is True

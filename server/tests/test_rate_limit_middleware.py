"""Tests for the API rate limiting middleware.

Validates: Requirements 18.1, 18.2, 18.3
"""

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.middleware.rate_limit import RateLimitMiddleware


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_test_app(rate_limit: int = 5, window: int = 60):
    """Create a minimal FastAPI app with the rate limit middleware."""
    from fastapi import FastAPI

    app = FastAPI()
    app.add_middleware(RateLimitMiddleware, rate_limit=rate_limit, window=window)

    @app.get("/test")
    async def test_endpoint():
        return {"ok": True}

    return app


def _make_mock_redis(execute_return):
    """Create a mock Redis client with a pipeline that returns given results.

    execute_return can be a single list (always returns that) or a list of
    lists (side_effect for sequential calls).
    """
    mock_redis = MagicMock()
    mock_pipe = AsyncMock()

    if isinstance(execute_return, list) and execute_return and isinstance(execute_return[0], list):
        mock_pipe.execute = AsyncMock(side_effect=execute_return)
    else:
        mock_pipe.execute = AsyncMock(return_value=execute_return)

    # pipeline() returns an async context manager
    mock_pipe.__aenter__ = AsyncMock(return_value=mock_pipe)
    mock_pipe.__aexit__ = AsyncMock(return_value=False)
    mock_redis.pipeline.return_value = mock_pipe

    return mock_redis


# ---------------------------------------------------------------------------
# Unit tests: _check_rate_limit
# ---------------------------------------------------------------------------


class TestCheckRateLimit:
    """Requirement 18.1 — sliding window rate limiting."""

    @pytest.mark.asyncio
    async def test_allows_when_under_limit(self):
        """Requests under the limit should be allowed."""
        mock_redis = _make_mock_redis([0, 1, 3, True])

        with patch("app.middleware.rate_limit.is_redis_available", return_value=True), \
             patch("app.middleware.rate_limit.get_redis", return_value=mock_redis):
            mw = RateLimitMiddleware(app=AsyncMock())
            result = await mw._check_rate_limit("test_key", limit=5, window=60)

        assert result is False  # not exceeded

    @pytest.mark.asyncio
    async def test_blocks_when_over_limit(self):
        """Requests over the limit should be blocked."""
        mock_redis = _make_mock_redis([0, 1, 6, True])

        with patch("app.middleware.rate_limit.is_redis_available", return_value=True), \
             patch("app.middleware.rate_limit.get_redis", return_value=mock_redis):
            mw = RateLimitMiddleware(app=AsyncMock())
            result = await mw._check_rate_limit("test_key", limit=5, window=60)

        assert result is True  # exceeded

    @pytest.mark.asyncio
    async def test_allows_at_exact_limit(self):
        """Requests at exactly the limit should be allowed (> not >=)."""
        mock_redis = _make_mock_redis([0, 1, 5, True])

        with patch("app.middleware.rate_limit.is_redis_available", return_value=True), \
             patch("app.middleware.rate_limit.get_redis", return_value=mock_redis):
            mw = RateLimitMiddleware(app=AsyncMock())
            result = await mw._check_rate_limit("test_key", limit=5, window=60)

        assert result is False  # exactly at limit, not exceeded


class TestRedisDegradation:
    """Requirement 18.3 — graceful degradation when Redis is unavailable."""

    @pytest.mark.asyncio
    async def test_allows_when_redis_unavailable(self):
        """When Redis is unavailable, all requests should be allowed."""
        with patch("app.middleware.rate_limit.is_redis_available", return_value=False):
            mw = RateLimitMiddleware(app=AsyncMock())
            result = await mw._check_rate_limit("test_key", limit=5, window=60)

        assert result is False

    @pytest.mark.asyncio
    async def test_allows_when_redis_client_none(self):
        """When Redis client is None, all requests should be allowed."""
        with patch("app.middleware.rate_limit.is_redis_available", return_value=True), \
             patch("app.middleware.rate_limit.get_redis", return_value=None):
            mw = RateLimitMiddleware(app=AsyncMock())
            result = await mw._check_rate_limit("test_key", limit=5, window=60)

        assert result is False

    @pytest.mark.asyncio
    async def test_allows_when_redis_raises_exception(self):
        """When Redis raises an exception during pipeline, requests should be allowed."""
        mock_redis = MagicMock()
        mock_pipe = AsyncMock()
        mock_pipe.execute = AsyncMock(side_effect=Exception("connection lost"))
        mock_pipe.__aenter__ = AsyncMock(return_value=mock_pipe)
        mock_pipe.__aexit__ = AsyncMock(return_value=False)
        mock_redis.pipeline.return_value = mock_pipe

        with patch("app.middleware.rate_limit.is_redis_available", return_value=True), \
             patch("app.middleware.rate_limit.get_redis", return_value=mock_redis):
            mw = RateLimitMiddleware(app=AsyncMock())
            result = await mw._check_rate_limit("test_key", limit=5, window=60)

        assert result is False

    @pytest.mark.asyncio
    async def test_logs_warning_when_redis_unavailable(self, caplog):
        """A warning should be logged when Redis is unavailable."""
        with patch("app.middleware.rate_limit.is_redis_available", return_value=False):
            mw = RateLimitMiddleware(app=AsyncMock())
            with caplog.at_level(logging.WARNING):
                await mw._check_rate_limit("test_key", limit=5, window=60)

        assert any("rate limiting disabled" in r.message.lower() for r in caplog.records)


# ---------------------------------------------------------------------------
# Integration tests: middleware with HTTP requests
# ---------------------------------------------------------------------------


@pytest.fixture
def app():
    """Create a test app with a low rate limit for testing."""
    return _create_test_app(rate_limit=3, window=60)


@pytest_asyncio.fixture
async def client(app):
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_returns_429_when_rate_exceeded(client):
    """Requirement 18.2 — HTTP 429 when rate limit exceeded."""
    mock_redis = _make_mock_redis([
        [0, 1, 1, True],
        [0, 1, 2, True],
        [0, 1, 3, True],
        [0, 1, 4, True],  # exceeds limit of 3
    ])

    with patch("app.middleware.rate_limit.is_redis_available", return_value=True), \
         patch("app.middleware.rate_limit.get_redis", return_value=mock_redis):
        # First 3 requests should succeed
        for _ in range(3):
            resp = await client.get("/test")
            assert resp.status_code == 200

        # 4th request should be rate limited
        resp = await client.get("/test")
        assert resp.status_code == 429
        body = resp.json()
        assert body["code"] == 429
        assert body["message"] == "请求过于频繁"


@pytest.mark.asyncio
async def test_allows_all_when_redis_down(client):
    """Requirement 18.3 — all requests allowed when Redis is down."""
    with patch("app.middleware.rate_limit.is_redis_available", return_value=False):
        for _ in range(10):
            resp = await client.get("/test")
            assert resp.status_code == 200

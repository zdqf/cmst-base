"""Tests for the unified exception hierarchy and global exception handlers.

Validates: Requirements 16.1, 16.2, 16.3
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.exceptions import (
    AppException,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    UnauthorizedError,
)
from app.main import create_app


# ---------------------------------------------------------------------------
# Unit tests: exception class hierarchy
# ---------------------------------------------------------------------------


class TestAppException:
    def test_default_values(self):
        exc = AppException()
        assert exc.code == 400
        assert exc.message == "请求错误"

    def test_custom_values(self):
        exc = AppException(code=422, message="参数错误")
        assert exc.code == 422
        assert exc.message == "参数错误"

    def test_is_exception(self):
        assert issubclass(AppException, Exception)


class TestNotFoundError:
    def test_default(self):
        exc = NotFoundError()
        assert exc.code == 404
        assert exc.message == "资源不存在"

    def test_custom_message(self):
        exc = NotFoundError("用户不存在")
        assert exc.code == 404
        assert exc.message == "用户不存在"

    def test_is_app_exception(self):
        assert issubclass(NotFoundError, AppException)


class TestUnauthorizedError:
    def test_default(self):
        exc = UnauthorizedError()
        assert exc.code == 401
        assert exc.message == "未授权"

    def test_custom_message(self):
        exc = UnauthorizedError("令牌已过期")
        assert exc.code == 401
        assert exc.message == "令牌已过期"

    def test_is_app_exception(self):
        assert issubclass(UnauthorizedError, AppException)


class TestForbiddenError:
    def test_default(self):
        exc = ForbiddenError()
        assert exc.code == 403
        assert exc.message == "无权限"

    def test_custom_message(self):
        exc = ForbiddenError("仅管理员可操作")
        assert exc.code == 403
        assert exc.message == "仅管理员可操作"

    def test_is_app_exception(self):
        assert issubclass(ForbiddenError, AppException)


class TestRateLimitError:
    def test_default(self):
        exc = RateLimitError()
        assert exc.code == 429
        assert exc.message == "请求过于频繁"

    def test_custom_message(self):
        exc = RateLimitError("请60秒后再试")
        assert exc.code == 429
        assert exc.message == "请60秒后再试"

    def test_is_app_exception(self):
        assert issubclass(RateLimitError, AppException)


# ---------------------------------------------------------------------------
# Integration tests: global exception handlers via the FastAPI app
# ---------------------------------------------------------------------------


@pytest.fixture
def app():
    """Create a fresh app with test routes that raise exceptions."""
    test_app = create_app()
    # Ensure debug mode is off so ServerErrorMiddleware doesn't intercept
    # unhandled exceptions with a plaintext traceback response.
    test_app.debug = False

    @test_app.get("/test/not-found")
    async def raise_not_found():
        raise NotFoundError("测试资源不存在")

    @test_app.get("/test/unauthorized")
    async def raise_unauthorized():
        raise UnauthorizedError()

    @test_app.get("/test/forbidden")
    async def raise_forbidden():
        raise ForbiddenError()

    @test_app.get("/test/rate-limit")
    async def raise_rate_limit():
        raise RateLimitError("请60秒后再试")

    @test_app.get("/test/app-exception")
    async def raise_app_exception():
        raise AppException(code=422, message="参数错误")

    @test_app.get("/test/unexpected")
    async def raise_unexpected():
        raise RuntimeError("some internal detail that should not leak")

    return test_app


@pytest_asyncio.fixture
async def client(app):
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_not_found_handler(client):
    resp = await client.get("/test/not-found")
    assert resp.status_code == 404
    body = resp.json()
    assert body["code"] == 404
    assert body["message"] == "测试资源不存在"


@pytest.mark.asyncio
async def test_unauthorized_handler(client):
    resp = await client.get("/test/unauthorized")
    assert resp.status_code == 401
    body = resp.json()
    assert body["code"] == 401
    assert body["message"] == "未授权"


@pytest.mark.asyncio
async def test_forbidden_handler(client):
    resp = await client.get("/test/forbidden")
    assert resp.status_code == 403
    body = resp.json()
    assert body["code"] == 403
    assert body["message"] == "无权限"


@pytest.mark.asyncio
async def test_rate_limit_handler(client):
    resp = await client.get("/test/rate-limit")
    assert resp.status_code == 429
    body = resp.json()
    assert body["code"] == 429
    assert body["message"] == "请60秒后再试"


@pytest.mark.asyncio
async def test_custom_app_exception_handler(client):
    resp = await client.get("/test/app-exception")
    assert resp.status_code == 422
    body = resp.json()
    assert body["code"] == 422
    assert body["message"] == "参数错误"


@pytest.mark.asyncio
async def test_unexpected_exception_returns_500(client):
    """Requirement 16.3: unexpected exceptions return 500 with generic message."""
    resp = await client.get("/test/unexpected")
    assert resp.status_code == 500
    body = resp.json()
    assert body["code"] == 500
    assert body["message"] == "服务器内部错误"
    # Must NOT leak internal details
    assert "internal detail" not in body["message"]

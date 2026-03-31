"""Tests for the request logging middleware and sensitive data masking.

Validates: Requirements 17.1, 17.2
"""

import logging

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import create_app
from app.middleware.logging import mask_phone, sanitize_log_message


# ---------------------------------------------------------------------------
# Unit tests: masking helpers
# ---------------------------------------------------------------------------


class TestMaskPhone:
    """Requirement 17.2 — phone number masking."""

    def test_masks_middle_four_digits(self):
        assert mask_phone("13812345678") == "138****5678"

    def test_masks_phone_in_sentence(self):
        text = "用户手机号 13912345678 已注册"
        assert mask_phone(text) == "用户手机号 139****5678 已注册"

    def test_masks_multiple_phones(self):
        text = "from 13800001111 to 15900002222"
        result = mask_phone(text)
        assert "138****1111" in result
        assert "159****2222" in result

    def test_no_phone_unchanged(self):
        text = "no phone here 12345"
        assert mask_phone(text) == text

    def test_short_number_unchanged(self):
        assert mask_phone("1381234") == "1381234"


class TestSanitizeLogMessage:
    """Requirement 17.2 — combined sanitisation."""

    def test_masks_phone(self):
        result = sanitize_log_message("phone=13812345678")
        assert "138****5678" in result

    def test_plain_text_unchanged(self):
        text = "GET /api/v1/health -> 200"
        assert sanitize_log_message(text) == text


# ---------------------------------------------------------------------------
# Integration tests: middleware logs requests
# ---------------------------------------------------------------------------


@pytest.fixture
def app():
    """Create a fresh app for middleware testing."""
    return create_app()


@pytest_asyncio.fixture
async def client(app):
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_middleware_logs_request(client, caplog):
    """Requirement 17.1 — logs method, path, status, duration."""
    with caplog.at_level(logging.INFO, logger="app.request"):
        resp = await client.get("/api/v1/health")

    assert resp.status_code == 200
    # At least one log record should contain the request info
    assert any(
        "GET" in r.message and "/api/v1/health" in r.message and "200" in r.message
        for r in caplog.records
    )


@pytest.mark.asyncio
async def test_middleware_logs_duration(client, caplog):
    """Requirement 17.1 — duration is present in the log."""
    with caplog.at_level(logging.INFO, logger="app.request"):
        await client.get("/api/v1/health")

    # Duration format: (X.XXXs)
    assert any("s)" in r.message for r in caplog.records)


@pytest.mark.asyncio
async def test_middleware_masks_phone_in_path(client, caplog):
    """Requirement 17.2 — phone numbers in the URL path are masked."""
    with caplog.at_level(logging.INFO, logger="app.request"):
        # This will 404 but the middleware still logs the request
        await client.get("/api/v1/users/13812345678")

    log_messages = " ".join(r.message for r in caplog.records)
    assert "138****5678" in log_messages
    assert "13812345678" not in log_messages


@pytest.mark.asyncio
async def test_middleware_masks_phone_in_query(client, caplog):
    """Requirement 17.2 — phone numbers in query params are masked."""
    with caplog.at_level(logging.INFO, logger="app.request"):
        await client.get("/api/v1/health?phone=13912345678")

    log_messages = " ".join(r.message for r in caplog.records)
    assert "139****5678" in log_messages
    assert "13912345678" not in log_messages


@pytest.mark.asyncio
async def test_password_not_logged_in_path(client, caplog):
    """Requirement 17.2 — password values should not appear in logs.

    The middleware masks the URL; passwords typically travel in request
    bodies (which we intentionally do NOT log).  This test confirms that
    the middleware does not log request bodies at all.
    """
    with caplog.at_level(logging.INFO, logger="app.request"):
        await client.post(
            "/api/v1/auth/admin/login",
            json={"phone": "13800001111", "password": "secret123"},
        )

    log_messages = " ".join(r.message for r in caplog.records)
    # The password value must never appear in any log record
    assert "secret123" not in log_messages

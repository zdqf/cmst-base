"""SMS service provider abstraction with Redis fallback to database.

Requirements:
- 5.1: BaseSMSProvider defines a unified SMS sending interface
- 5.2: AliyunSMSProvider used when sms_provider="aliyun"
- 5.3: MockSMSProvider used when sms_provider="mock", fixed code 123456, always succeeds
- 5.4: Switch providers via config without modifying business code
- 25.1: When Redis is unavailable, fall back to database temporary storage
- 25.2: When Redis recovers, automatically switch back to Redis
"""

import logging
import random
import re
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session_factory
from app.exceptions import AppException, RateLimitError
from app.models.sms_code_temp import SmsCodeTemp
from app.redis import get_redis, is_redis_available

logger = logging.getLogger(__name__)


class BaseSMSProvider(ABC):
    """Abstract base class for SMS providers.

    All SMS providers must implement the send_code method.
    """

    @abstractmethod
    async def send_code(self, phone: str, code: str) -> bool:
        """Send a verification code to the given phone number.

        Args:
            phone: Target phone number.
            code: Verification code to send.

        Returns:
            True if the SMS was sent successfully, False otherwise.
        """
        ...


class AliyunSMSProvider(BaseSMSProvider):
    """Aliyun SMS provider using alibabacloud-dysmsapi SDK."""

    def __init__(
        self,
        access_key_id: str,
        access_key_secret: str,
        sign_name: str,
        template_code: str,
    ):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.sign_name = sign_name
        self.template_code = template_code

    def _create_client(self):
        """Create the Aliyun SMS API client."""
        from alibabacloud_dysmsapi20170525.client import Client
        from alibabacloud_tea_openapi.models import Config

        config = Config(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
            endpoint="dysmsapi.aliyuncs.com",
        )
        return Client(config)

    async def send_code(self, phone: str, code: str) -> bool:
        """Send verification code via Aliyun SMS API.

        Args:
            phone: Target phone number.
            code: Verification code to send.

        Returns:
            True if the SMS was sent successfully, False otherwise.
        """
        import json

        from alibabacloud_dysmsapi20170525.models import SendSmsRequest

        try:
            client = self._create_client()
            request = SendSmsRequest(
                phone_numbers=phone,
                sign_name=self.sign_name,
                template_code=self.template_code,
                template_param=json.dumps({"code": code}),
            )
            response = client.send_sms(request)
            body = response.body

            if body.code == "OK":
                logger.info("SMS sent successfully to %s***%s", phone[:3], phone[-4:])
                return True

            logger.error(
                "Aliyun SMS failed: code=%s, message=%s",
                body.code,
                body.message,
            )
            return False
        except Exception:
            logger.exception("Aliyun SMS API error for phone %s***%s", phone[:3], phone[-4:])
            return False


class MockSMSProvider(BaseSMSProvider):
    """Mock SMS provider for development/testing.

    Always returns success and logs the verification code.
    Fixed code: 123456.
    """

    async def send_code(self, phone: str, code: str) -> bool:
        """Log the verification code and return success.

        Args:
            phone: Target phone number.
            code: Verification code to send.

        Returns:
            Always True.
        """
        logger.info(
            "[MockSMS] Verification code for %s***%s: %s",
            phone[:3],
            phone[-4:],
            code,
        )
        return True


def get_sms_provider() -> BaseSMSProvider:
    """Factory function that returns the SMS provider based on config.

    Returns:
        An instance of BaseSMSProvider (AliyunSMSProvider or MockSMSProvider).

    Raises:
        ValueError: If sms_provider config value is not recognized.
    """
    provider = settings.sms_provider.lower()

    if provider == "aliyun":
        return AliyunSMSProvider(
            access_key_id=settings.aliyun_access_key_id,
            access_key_secret=settings.aliyun_access_key_secret,
            sign_name=settings.aliyun_sms_sign_name,
            template_code=settings.aliyun_sms_template_code,
        )
    elif provider == "mock":
        return MockSMSProvider()
    else:
        raise ValueError(f"Unknown SMS provider: {provider}")


PHONE_PATTERN = re.compile(r"^1[3-9]\d{9}$")


def _generate_code() -> str:
    """Generate a 6-digit random numeric verification code."""
    return f"{random.randint(0, 999999):06d}"


# ---------------------------------------------------------------------------
# Database fallback helpers (Requirements: 25.1, 25.2)
# ---------------------------------------------------------------------------


async def _db_store_code(phone: str, code: str, ttl: int) -> None:
    """Store a verification code in the database as a Redis fallback.

    Uses PostgreSQL upsert (INSERT ... ON CONFLICT UPDATE) so that
    a new code for the same phone replaces the old one.
    """
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)
    async with async_session_factory() as session:
        stmt = (
            pg_insert(SmsCodeTemp)
            .values(phone=phone, code=code, expires_at=expires_at)
            .on_conflict_do_update(
                index_elements=["phone"],
                set_={"code": code, "expires_at": expires_at},
            )
        )
        await session.execute(stmt)
        await session.commit()
    logger.info("SMS code stored in database fallback for %s***%s", phone[:3], phone[-4:])


async def _db_get_code(phone: str) -> str | None:
    """Retrieve a non-expired verification code from the database."""
    now = datetime.now(timezone.utc)
    async with async_session_factory() as session:
        stmt = (
            select(SmsCodeTemp.code)
            .where(SmsCodeTemp.phone == phone, SmsCodeTemp.expires_at > now)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


async def _db_delete_code(phone: str) -> None:
    """Delete a verification code from the database."""
    async with async_session_factory() as session:
        stmt = delete(SmsCodeTemp).where(SmsCodeTemp.phone == phone)
        await session.execute(stmt)
        await session.commit()


async def _db_cleanup_expired() -> int:
    """Remove expired SMS codes from the database. Returns count deleted."""
    now = datetime.now(timezone.utc)
    async with async_session_factory() as session:
        stmt = delete(SmsCodeTemp).where(SmsCodeTemp.expires_at <= now)
        result = await session.execute(stmt)
        await session.commit()
        count = result.rowcount
        if count > 0:
            logger.info("Cleaned up %d expired SMS codes from database", count)
        return count


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def send_sms_code(phone: str) -> None:
    """Send an SMS verification code to the given phone number.

    Generates a 6-digit random code, enforces rate limits (60s interval,
    10 per day per number), sends via the configured provider, and stores
    the code in Redis. When Redis is unavailable, falls back to database
    storage with relaxed rate limiting.

    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 25.1, 25.2

    Args:
        phone: Chinese mobile phone number matching ^1[3-9]\\d{9}$.

    Raises:
        AppException: If phone format is invalid.
        RateLimitError: If 60s rate limit or daily limit exceeded.
        AppException: If SMS provider fails (HTTP 500), quota is NOT consumed.
    """
    # Validate phone format
    if not PHONE_PATTERN.match(phone):
        raise AppException(code=400, message="手机号格式错误")

    redis_up = await is_redis_available()

    if redis_up:
        await _send_sms_code_redis(phone)
    else:
        logger.warning("Redis unavailable, using database fallback for SMS code")
        await _send_sms_code_db(phone)


async def _send_sms_code_redis(phone: str) -> None:
    """Send SMS code with Redis storage (normal path)."""
    redis = get_redis()
    if redis is None:
        raise AppException(code=500, message="服务暂时不可用，请稍后重试")

    rate_key = f"sms_rate:{phone}"
    today = date.today().isoformat()
    daily_key = f"sms_daily:{phone}:{today}"
    code_key = f"sms_code:{phone}"

    # Check 60-second rate limit
    if await redis.exists(rate_key):
        raise RateLimitError(message="请60秒后再试")

    # Check daily limit
    daily_count = await redis.get(daily_key)
    if daily_count is not None and int(daily_count) >= settings.sms_daily_limit:
        raise RateLimitError(message="今日发送次数已达上限")

    # Generate code and send via provider
    code = _generate_code()
    provider = get_sms_provider()
    success = await provider.send_code(phone, code)

    if not success:
        raise AppException(code=500, message="短信发送失败，请稍后重试")

    # Store code and update rate/daily counters only after successful send
    await redis.set(code_key, code, ex=settings.sms_code_ttl)
    await redis.set(rate_key, "1", ex=settings.sms_rate_limit)

    # Increment daily counter (set TTL on first increment)
    if await redis.exists(daily_key):
        await redis.incr(daily_key)
    else:
        await redis.set(daily_key, 1, ex=86400)


async def _send_sms_code_db(phone: str) -> None:
    """Send SMS code with database fallback storage (degraded mode).

    Rate limiting is relaxed in degraded mode since sliding window
    is not easily implemented in the database.
    """
    code = _generate_code()
    provider = get_sms_provider()
    success = await provider.send_code(phone, code)

    if not success:
        raise AppException(code=500, message="短信发送失败，请稍后重试")

    await _db_store_code(phone, code, settings.sms_code_ttl)


async def verify_sms_code(phone: str, code: str) -> bool:
    """Verify an SMS verification code.

    If the code matches, it is deleted (one-time use).
    If it does not match, the stored code is left intact.
    Checks Redis first; if Redis is unavailable, checks the database.

    Requirements: 4.1, 4.2, 4.3, 4.4, 25.1, 25.2

    Args:
        phone: Phone number the code was sent to.
        code: The verification code to check.

    Returns:
        True if the code matches, False otherwise.
    """
    if not phone or not code:
        return False

    redis_up = await is_redis_available()

    if redis_up:
        return await _verify_sms_code_redis(phone, code)
    else:
        logger.warning("Redis unavailable, using database fallback for SMS verification")
        return await _verify_sms_code_db(phone, code)


async def _verify_sms_code_redis(phone: str, code: str) -> bool:
    """Verify SMS code from Redis (normal path)."""
    redis = get_redis()
    if redis is None:
        return False

    code_key = f"sms_code:{phone}"
    stored_code = await redis.get(code_key)

    if stored_code is None:
        return False

    if stored_code == code:
        await redis.delete(code_key)
        return True

    return False


async def _verify_sms_code_db(phone: str, code: str) -> bool:
    """Verify SMS code from database fallback (degraded mode)."""
    stored_code = await _db_get_code(phone)

    if stored_code is None:
        return False

    if stored_code == code:
        await _db_delete_code(phone)
        return True

    return False

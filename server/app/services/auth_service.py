"""Authentication service layer — registration and login logic.

Requirements:
- 1.1: Register user with phone + code, return user and token
- 1.2: Login user with phone + code, return user and token
- 1.3: Invalid verification code returns error
- 1.4: Duplicate phone returns "该手机号已注册"
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.auth import create_access_token
from app.models.user import User


# Placeholder valid SMS code — will be replaced with real SMS service
VALID_SMS_CODE = "123456"


def verify_sms_code(phone: str, code: str) -> bool:
    """Verify SMS verification code.

    Placeholder implementation: accepts "123456" as valid for any phone.
    """
    return code == VALID_SMS_CODE


async def register_user(db: AsyncSession, phone: str, code: str) -> tuple[User, str]:
    """Register a new user.

    Args:
        db: Database session.
        phone: User phone number.
        code: SMS verification code.

    Returns:
        Tuple of (created User, JWT token string).

    Raises:
        ValueError: If code is invalid or phone already registered.
    """
    if not verify_sms_code(phone, code):
        raise ValueError("验证码无效")

    result = await db.execute(select(User).where(User.phone == phone))
    existing = result.scalar_one_or_none()
    if existing is not None:
        raise ValueError("该手机号已注册")

    user = User(phone=phone)
    db.add(user)
    await db.flush()

    token = create_access_token(str(user.id))
    return user, token


async def login_user(db: AsyncSession, phone: str, code: str) -> tuple[User, str]:
    """Login an existing user.

    Args:
        db: Database session.
        phone: User phone number.
        code: SMS verification code.

    Returns:
        Tuple of (User, JWT token string).

    Raises:
        ValueError: If code is invalid or phone not registered.
    """
    if not verify_sms_code(phone, code):
        raise ValueError("验证码无效")

    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()
    if user is None:
        raise ValueError("该手机号未注册")

    user.last_login_at = datetime.now(timezone.utc)
    await db.flush()

    token = create_access_token(str(user.id))
    return user, token

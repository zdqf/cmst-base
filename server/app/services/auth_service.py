"""Authentication service layer — registration and login logic.

Requirements:
- 1.1: Register user with phone + code, return user and token
- 1.2: Login user with phone + code, return user and token
- 1.3: Invalid verification code returns error
- 1.4: Duplicate phone returns "该手机号已注册"
- 1.1 (admin): Admin password login with bcrypt verification
- 1.2 (admin): Wrong password returns generic error
- 1.3 (admin): Non-admin users rejected
- 1.6 (admin): Password length 6-32 characters
- 1.7 (admin): Phone format ^1[3-9]\\d{9}$
- 24.1: bcrypt cost factor >= 12
"""

import asyncio
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.exceptions import AppException
from app.middleware.auth import create_access_token
from app.models.user import User
from app.services.sms_service import verify_sms_code as sms_verify_code


# bcrypt cost factor >= 12 (Requirement 24.1)
BCRYPT_ROUNDS = 12


async def register_user(db: AsyncSession, phone: str, code: str) -> tuple[User, str]:
    """Register a new user.

    Args:
        db: Database session.
        phone: User phone number.
        code: SMS verification code.

    Returns:
        Tuple of (created User, JWT token string).

    Raises:
        AppException: If code is invalid or phone already registered.
    """
    if not await sms_verify_code(phone, code):
        raise AppException(code=400, message="验证码无效")

    result = await db.execute(select(User).where(User.phone == phone))
    existing = result.scalar_one_or_none()
    if existing is not None:
        raise AppException(code=400, message="该手机号已注册")

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
        AppException: If code is invalid or phone not registered.
    """
    if not await sms_verify_code(phone, code):
        raise AppException(code=400, message="验证码无效")

    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()
    if user is None:
        raise AppException(code=400, message="该手机号未注册")

    user.last_login_at = datetime.now(timezone.utc)
    await db.flush()

    token = create_access_token(str(user.id))
    return user, token


def _create_admin_token(user_id: str) -> str:
    """Create a JWT access token with admin role claim.

    Args:
        user_id: The user's UUID as a string.

    Returns:
        Encoded JWT token string with role="admin".
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.jwt_expire_days)
    payload = {
        "sub": user_id,
        "role": "admin",
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def _verify_password_sync(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a bcrypt hash (non-blocking)."""
    return await asyncio.to_thread(_verify_password_sync, plain_password, hashed_password)


def _hash_password_sync(password: str) -> str:
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


async def hash_password(password: str) -> str:
    """Hash a password using bcrypt with cost factor >= 12 (non-blocking)."""
    return await asyncio.to_thread(_hash_password_sync, password)


async def set_admin_password(
    db: AsyncSession,
    user: User,
    password: str,
    old_password: str | None = None,
) -> None:
    """Set or change an admin user's password.

    First-time setup (no existing password_hash): old_password is not required.
    Password change (password_hash exists): old_password must be provided and correct.

    Args:
        db: Database session.
        user: The admin user whose password is being set.
        password: New password (6-32 characters).
        old_password: Current password (required when changing an existing password).

    Raises:
        ForbiddenError: If the user is not an admin.
        AppException: If password length is invalid, old_password is missing when
            required, or old_password is incorrect.

    Validates: Requirements 1.4, 1.5, 1.6
    """
    from app.exceptions import ForbiddenError

    # Must be admin
    if not user.is_admin:
        raise ForbiddenError("仅管理员可设置密码")

    # Password length validation (Requirement 1.6)
    if len(password) < 6 or len(password) > 32:
        raise AppException(code=400, message="密码长度必须在6-32个字符之间")

    # If password already set, old_password is required (Requirement 1.5)
    if user.password_hash:
        if not old_password:
            raise AppException(code=400, message="修改密码需要提供旧密码")
        if not await verify_password(old_password, user.password_hash):
            raise AppException(code=400, message="旧密码错误")

    # Hash and store (Requirement 1.4 — bcrypt cost >= 12)
    user.password_hash = await hash_password(password)
    await db.flush()


async def admin_login(db: AsyncSession, phone: str, password: str) -> tuple[User, str]:
    """Admin password login.

    Validates phone/password credentials and admin status.
    Returns a JWT token with role="admin" on success.

    Args:
        db: Database session.
        phone: Admin phone number (must match ^1[3-9]\\d{9}$).
        password: Password (6-32 characters).

    Returns:
        Tuple of (User, JWT token string).

    Raises:
        AppException: Always with message "手机号或密码错误" regardless of
            the specific failure reason (phone not found, not admin, wrong password).
    """
    error_msg = "手机号或密码错误"

    # Look up user by phone
    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()

    if user is None:
        raise AppException(code=400, message=error_msg)

    # Reject non-admin users
    if not user.is_admin:
        raise AppException(code=400, message=error_msg)

    # Reject users without a password set
    if not user.password_hash:
        raise AppException(code=400, message=error_msg)

    # Verify password
    if not await verify_password(password, user.password_hash):
        raise AppException(code=400, message=error_msg)

    # Update last login timestamp
    user.last_login_at = datetime.now(timezone.utc)
    await db.flush()

    # Create JWT with admin role
    token = _create_admin_token(str(user.id))
    return user, token


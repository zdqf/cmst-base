"""JWT authentication middleware and utilities.

Requirement 1.5: JWT token-based session management with 7-day expiry.
"""

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, ExpiredSignatureError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User

security = HTTPBearer()


def create_access_token(user_id: str) -> str:
    """Create a JWT access token for the given user ID.

    Args:
        user_id: The user's UUID as a string.

    Returns:
        Encoded JWT token string.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.jwt_expire_days)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token.

    Args:
        token: The JWT token string.

    Returns:
        Decoded token payload dict.

    Raises:
        HTTPException: 401 if token is expired or invalid.
    """
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌已过期，请重新登录",
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """FastAPI dependency that extracts and validates the current user.

    Extracts Bearer token from Authorization header, decodes it,
    queries the user from the database, and validates user status.

    Args:
        credentials: Bearer token from Authorization header.
        db: Database session.

    Returns:
        The authenticated User object.

    Raises:
        HTTPException: 401 if token is invalid/expired or user not found/disabled.
    """
    payload = decode_access_token(credentials.credentials)
    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账户已被禁用",
        )

    # Check if token was issued before invalidation (Requirement 8.3)
    if user.token_invalidated_at is not None:
        token_iat = payload.get("iat")
        if token_iat is not None:
            issued_at = datetime.fromtimestamp(token_iat, tz=timezone.utc)
            if issued_at < user.token_invalidated_at:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="认证令牌已失效，请重新登录",
                )

    return user

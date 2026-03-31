"""Admin user management router.

Requirements:
- 8.1: Paginated user list with phone, registration time, last login
- 8.2: Search users by phone number
- 8.3: Disable user account and invalidate auth tokens
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.auth import SetPasswordRequest
from app.schemas.common import ApiResponse, PaginatedResponse, PaginationParams
from app.schemas.admin_user import AdminUserItem
from app.services.auth_service import set_admin_password

router = APIRouter(prefix="/api/v1/admin/users", tags=["管理后台-用户管理"])


async def get_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency that ensures the current user is an admin."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无管理员权限",
        )
    return current_user


@router.get("", response_model=ApiResponse)
async def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=20),
    phone: str | None = Query(default=None, description="手机号搜索"),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """List all users with pagination and optional phone search.

    Requirement 8.1: Paginated user list
    Requirement 8.2: Phone number search
    """
    base_filter = select(User)
    count_filter = select(func.count(User.id))

    if phone:
        base_filter = base_filter.where(User.phone.contains(phone))
        count_filter = count_filter.where(User.phone.contains(phone))

    # Total count
    count_result = await db.execute(count_filter)
    total = count_result.scalar_one()

    # Paginated query
    offset = (page - 1) * page_size
    query = (
        base_filter
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    users = result.scalars().all()

    items = [AdminUserItem.model_validate(u) for u in users]
    paginated = PaginatedResponse[AdminUserItem].create(
        items=items, total=total, page=page, page_size=page_size
    )
    return ApiResponse(data=paginated.model_dump(mode="json"))


@router.put("/{user_id}/disable", response_model=ApiResponse)
async def disable_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """Disable a user account and invalidate their auth tokens.

    Requirement 8.3: Disable user and invalidate tokens.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        return ApiResponse(code=404, message="用户不存在")

    if user.status == "disabled":
        return ApiResponse(code=400, message="该用户已被禁用")

    # Disable user and invalidate tokens
    now = datetime.now(timezone.utc)
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(status="disabled", token_invalidated_at=now)
    )

    return ApiResponse(message="用户已禁用")


@router.post("/set-password", response_model=ApiResponse)
async def set_password(
    req: SetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
) -> ApiResponse:
    """Set or change admin password.

    Requires admin authentication.

    Requirements:
    - 1.4: First-time password setup with bcrypt (cost >= 12)
    - 1.5: Password change requires old password verification
    - 1.6: Password length 6-32 characters
    """
    await set_admin_password(db, current_user, req.password, req.old_password)
    return ApiResponse(message="密码设置成功")

"""Admin order management router.

Requirements:
- 13.1: Paginated order list with order_no, user info, amount, status, time
- 13.2: Update order status (pending/paid/shipped/completed/cancelled)
- 13.3: Filter orders by status and date range
"""

import uuid
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.order import Order
from app.models.user import User
from app.routers.admin.users import get_admin_user
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.order import AdminOrderListItem, AdminOrderStatusUpdate

router = APIRouter(prefix="/api/v1/admin/orders", tags=["管理后台-订单管理"])


@router.get("", response_model=ApiResponse)
async def list_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=20),
    status: str | None = Query(default=None, description="状态筛选: pending/paid/shipped/completed/cancelled"),
    start_date: date | None = Query(default=None, description="开始日期 (YYYY-MM-DD)"),
    end_date: date | None = Query(default=None, description="结束日期 (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """List all orders with pagination and optional status/date filters.

    Requirement 13.1: Paginated order list.
    Requirement 13.3: Filter by status and date range.
    """
    base_query = select(Order)
    count_query = select(func.count(Order.id))

    if status:
        base_query = base_query.where(Order.status == status)
        count_query = count_query.where(Order.status == status)

    if start_date:
        start_dt = datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc)
        base_query = base_query.where(Order.created_at >= start_dt)
        count_query = count_query.where(Order.created_at >= start_dt)

    if end_date:
        end_dt = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59, tzinfo=timezone.utc)
        base_query = base_query.where(Order.created_at <= end_dt)
        count_query = count_query.where(Order.created_at <= end_dt)

    # Total count
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    # Paginated query
    offset = (page - 1) * page_size
    query = base_query.order_by(Order.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    orders = result.scalars().all()

    items = [AdminOrderListItem.model_validate(o) for o in orders]
    paginated = PaginatedResponse[AdminOrderListItem].create(
        items=items, total=total, page=page, page_size=page_size,
    )
    return ApiResponse(data=paginated.model_dump(mode="json"))


@router.put("/{order_id}/status", response_model=ApiResponse)
async def update_order_status(
    order_id: uuid.UUID,
    body: AdminOrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """Update order status and record the updated_at timestamp.

    Requirement 13.2: Update order status and record operation time.
    """
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if order is None:
        return ApiResponse(code=404, message="订单不存在")

    now = datetime.now(timezone.utc)
    await db.execute(
        update(Order)
        .where(Order.id == order_id)
        .values(status=body.status, updated_at=now)
    )

    return ApiResponse(message="订单状态已更新", data={"status": body.status, "updated_at": now.isoformat()})

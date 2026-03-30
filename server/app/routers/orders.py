"""Orders router — authenticated order endpoints.

Requirements:
- 7.4: POST /api/v1/orders — create order with stock validation
- 7.5: Insufficient stock returns error
- 7.6: Deduct stock on order creation
- 7.7: GET /api/v1/orders — paginated order list, time descending
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.common import ApiResponse, PaginationParams
from app.schemas.order import CreateOrderRequest, OrderItemResponse, OrderResponse
from app.services.order_service import create_order, list_orders

router = APIRouter(prefix="/api/v1/orders", tags=["订单"])


@router.post("", response_model=ApiResponse)
async def create_order_endpoint(
    req: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """Create a new order. Validates stock before creation."""
    try:
        order = await create_order(db, current_user.id, req.items)
    except ValueError as e:
        return ApiResponse(code=400, message=str(e))

    order_data = OrderResponse(
        id=order.id,
        order_no=order.order_no,
        total_amount=order.total_amount,
        status=order.status,
        items=[
            OrderItemResponse(
                product_id=item.product_id,
                product_name=item.product.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in order.items
        ],
        created_at=order.created_at,
    )
    return ApiResponse(message="订单创建成功", data=order_data.model_dump(mode="json"))


@router.get("", response_model=ApiResponse)
async def list_orders_endpoint(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """List orders for the current user, paginated, time descending."""
    result = await list_orders(
        db, current_user.id, pagination.page, pagination.page_size
    )
    return ApiResponse(data=result.model_dump(mode="json"))

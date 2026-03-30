"""Order Pydantic schemas for API request/response models.

Requirements:
- 7.4: Create order with stock validation
- 7.5: Insufficient stock returns error
- 7.6: Deduct stock after order creation
- 7.7: Order list in time descending order with pagination
"""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class OrderItemRequest(BaseModel):
    """Single item in a create-order request."""

    product_id: uuid.UUID
    quantity: int = Field(ge=1, description="数量，最小为 1")


class CreateOrderRequest(BaseModel):
    """Request body for creating an order."""

    items: list[OrderItemRequest] = Field(min_length=1, description="订单商品列表，至少 1 项")


class OrderItemResponse(BaseModel):
    """Order item detail in an order response."""

    product_id: uuid.UUID
    product_name: str
    quantity: int
    unit_price: Decimal

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    """Full order detail response."""

    id: uuid.UUID
    order_no: str
    total_amount: Decimal
    status: str
    items: list[OrderItemResponse]
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderListItem(BaseModel):
    """Order summary for list view."""

    id: uuid.UUID
    order_no: str
    total_amount: Decimal
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Admin order schemas (Requirements 13.1, 13.2, 13.3)
# ---------------------------------------------------------------------------

VALID_ORDER_STATUSES = ("pending", "paid", "shipped", "completed", "cancelled")


class AdminOrderListItem(BaseModel):
    """Order summary for admin list view.

    Requirement 13.1: order_no, user_id, total_amount, status, created_at.
    """

    id: uuid.UUID
    order_no: str
    user_id: uuid.UUID
    total_amount: Decimal
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminOrderStatusUpdate(BaseModel):
    """Request body for updating order status.

    Requirement 13.2: Update order status.
    """

    status: str = Field(
        ...,
        description="订单状态: pending/paid/shipped/completed/cancelled",
        pattern=f"^({'|'.join(VALID_ORDER_STATUSES)})$",
    )

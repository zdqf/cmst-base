"""Payment Pydantic schemas for API request/response models."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class CreatePaymentRequest(BaseModel):
    """Request to create a payment for an order."""

    order_id: uuid.UUID = Field(..., description="Order ID to pay for")
    method: str = Field(
        default="alipay",
        description="Payment method: alipay / wechat / mock",
        pattern="^(alipay|wechat|mock)$",
    )


class PaymentResponse(BaseModel):
    """Payment creation response."""

    payment_id: uuid.UUID
    order_id: uuid.UUID
    method: str
    amount: Decimal
    status: str
    pay_url: Optional[str] = None
    trade_no: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaymentStatusResponse(BaseModel):
    """Payment status query response."""

    payment_id: str
    order_id: str
    method: str
    amount: str
    status: str
    trade_no: Optional[str] = None
    paid_at: Optional[str] = None

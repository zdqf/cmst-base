"""Cart Pydantic schemas for API request/response models.

Requirements:
- 7.3: Cart add, update, remove, and list operations
"""

import uuid
from decimal import Decimal

from pydantic import BaseModel, Field


class CartAddRequest(BaseModel):
    """Request to add a product to the cart."""

    product_id: uuid.UUID
    quantity: int = Field(default=1, ge=1, description="数量，最小为 1")


class CartUpdateRequest(BaseModel):
    """Request to update cart item quantity."""

    quantity: int = Field(ge=1, description="数量，最小为 1")


class CartItemResponse(BaseModel):
    """Cart item response with product info."""

    id: uuid.UUID
    product_id: uuid.UUID
    product_name: str
    quantity: int
    unit_price: Decimal

    model_config = {"from_attributes": True}

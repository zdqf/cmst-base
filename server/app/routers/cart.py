"""Cart router — authenticated cart operation endpoints.

Requirements:
- 7.3: POST/PUT/DELETE/GET /api/v1/cart — cart CRUD operations
"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.cart import CartAddRequest, CartItemResponse, CartUpdateRequest
from app.schemas.common import ApiResponse
from app.services.cart_service import (
    add_to_cart,
    get_cart,
    remove_from_cart,
    update_cart_item,
)

router = APIRouter(prefix="/api/v1/cart", tags=["购物车"])


@router.post("", response_model=ApiResponse)
async def add_to_cart_endpoint(
    req: CartAddRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """Add a product to the cart (or increment if already exists)."""
    item = await add_to_cart(db, current_user.id, req.product_id, req.quantity)
    return ApiResponse(
        message="已添加到购物车",
        data={"id": str(item.id), "quantity": item.quantity},
    )


@router.put("/{item_id}", response_model=ApiResponse)
async def update_cart_item_endpoint(
    item_id: uuid.UUID,
    req: CartUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """Update the quantity of a cart item."""
    item = await update_cart_item(db, current_user.id, item_id, req.quantity)
    if item is None:
        return ApiResponse(code=404, message="购物车商品不存在")
    return ApiResponse(
        message="数量已更新",
        data={"id": str(item.id), "quantity": item.quantity},
    )


@router.delete("/{item_id}", response_model=ApiResponse)
async def remove_from_cart_endpoint(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """Remove an item from the cart."""
    deleted = await remove_from_cart(db, current_user.id, item_id)
    if not deleted:
        return ApiResponse(code=404, message="购物车商品不存在")
    return ApiResponse(message="已从购物车移除")


@router.get("", response_model=ApiResponse)
async def get_cart_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """List all cart items for the current user."""
    items = await get_cart(db, current_user.id)
    cart_items = [
        CartItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product.name,
            quantity=item.quantity,
            unit_price=item.product.price,
        ).model_dump(mode="json")
        for item in items
    ]
    return ApiResponse(data=cart_items)

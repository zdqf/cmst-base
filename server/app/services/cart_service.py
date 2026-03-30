"""Cart service layer — business logic for cart operations.

Requirements:
- 7.3: Add, update quantity, remove, and list cart items
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.cart import CartItem
from app.models.product import Product


async def add_to_cart(
    db: AsyncSession,
    user_id: uuid.UUID,
    product_id: uuid.UUID,
    quantity: int,
) -> CartItem:
    """Add a product to the cart, or increment quantity if already exists."""
    stmt = select(CartItem).where(
        CartItem.user_id == user_id,
        CartItem.product_id == product_id,
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing is not None:
        existing.quantity += quantity
        await db.flush()
        return existing

    item = CartItem(
        user_id=user_id,
        product_id=product_id,
        quantity=quantity,
    )
    db.add(item)
    await db.flush()
    return item


async def update_cart_item(
    db: AsyncSession,
    user_id: uuid.UUID,
    item_id: uuid.UUID,
    quantity: int,
) -> CartItem | None:
    """Update the quantity of a cart item. Returns None if not found."""
    stmt = select(CartItem).where(
        CartItem.id == item_id,
        CartItem.user_id == user_id,
    )
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()

    if item is None:
        return None

    item.quantity = quantity
    await db.flush()
    return item


async def remove_from_cart(
    db: AsyncSession,
    user_id: uuid.UUID,
    item_id: uuid.UUID,
) -> bool:
    """Remove a cart item. Returns True if deleted, False if not found."""
    stmt = select(CartItem).where(
        CartItem.id == item_id,
        CartItem.user_id == user_id,
    )
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()

    if item is None:
        return False

    await db.delete(item)
    await db.flush()
    return True


async def get_cart(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> list[CartItem]:
    """Get all cart items for a user with product info loaded."""
    stmt = (
        select(CartItem)
        .options(joinedload(CartItem.product))
        .where(CartItem.user_id == user_id)
        .order_by(CartItem.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().unique().all())

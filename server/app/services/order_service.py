"""Order service layer — business logic for order operations.

Requirements:
- 7.4: Validate stock and create order with unique order_no
- 7.5: Insufficient stock returns error and blocks order creation
- 7.6: Deduct stock after order creation
- 7.7: Order list paginated in time descending order
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.common import PaginatedResponse
from app.schemas.order import OrderItemRequest, OrderListItem


def _generate_order_no() -> str:
    """Generate a unique order number based on timestamp + random suffix."""
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%d%H%M%S%f")
    suffix = uuid.uuid4().hex[:6].upper()
    return f"ORD{ts}{suffix}"


async def create_order(
    db: AsyncSession,
    user_id: uuid.UUID,
    items: list[OrderItemRequest],
) -> Order:
    """Create an order after validating stock for all items.

    Raises:
        ValueError: If any product has insufficient stock or is not found.
    """
    # Collect product IDs and load products
    product_ids = [item.product_id for item in items]
    stmt = select(Product).where(Product.id.in_(product_ids))
    result = await db.execute(stmt)
    products = {p.id: p for p in result.scalars().all()}

    # Validate all items have valid products with sufficient stock
    for item in items:
        product = products.get(item.product_id)
        if product is None:
            raise ValueError(f"商品不存在: {item.product_id}")
        if product.stock < item.quantity:
            raise ValueError(f"商品「{product.name}」库存不足，当前库存: {product.stock}")

    # Calculate total amount
    total_amount = sum(
        products[item.product_id].price * item.quantity for item in items
    )

    # Create order
    order = Order(
        user_id=user_id,
        order_no=_generate_order_no(),
        total_amount=total_amount,
        status="pending",
    )
    db.add(order)
    await db.flush()

    # Create order items and deduct stock
    for item in items:
        product = products[item.product_id]
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=product.price,
        )
        db.add(order_item)
        product.stock -= item.quantity

    await db.flush()

    # Reload order with items for response
    reload_stmt = (
        select(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
        .where(Order.id == order.id)
    )
    reload_result = await db.execute(reload_stmt)
    return reload_result.unique().scalar_one()


async def list_orders(
    db: AsyncSession,
    user_id: uuid.UUID,
    page: int,
    page_size: int,
) -> PaginatedResponse[OrderListItem]:
    """Paginated order list for a user, sorted by time descending."""
    conditions = [Order.user_id == user_id]

    # Count total
    count_stmt = select(func.count()).select_from(Order).where(*conditions)
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    # Fetch page
    offset = (page - 1) * page_size
    query_stmt = (
        select(Order)
        .where(*conditions)
        .order_by(Order.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query_stmt)
    orders = result.scalars().all()

    items = [OrderListItem.model_validate(o) for o in orders]
    return PaginatedResponse.create(
        items=items, total=total, page=page, page_size=page_size
    )

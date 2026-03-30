"""Product service layer — business logic for product queries.

Requirements:
- 7.1: Product list with category filtering and pagination
- 7.2: Product detail query
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.schemas.common import PaginatedResponse
from app.schemas.product import ProductListItem, ProductSearchParams


async def list_products(
    db: AsyncSession, params: ProductSearchParams
) -> PaginatedResponse[ProductListItem]:
    """Paginated product list with optional category filter.

    Only returns active products.
    """
    conditions = [Product.status == "active"]

    if params.category:
        conditions.append(Product.category == params.category)

    # Count total
    count_stmt = select(func.count()).select_from(Product).where(*conditions)
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    # Fetch page
    offset = (params.page - 1) * params.page_size
    query_stmt = (
        select(Product)
        .where(*conditions)
        .order_by(Product.name)
        .offset(offset)
        .limit(params.page_size)
    )
    result = await db.execute(query_stmt)
    products = result.scalars().all()

    items = [ProductListItem.model_validate(p) for p in products]
    return PaginatedResponse.create(
        items=items, total=total, page=params.page, page_size=params.page_size
    )


async def get_product_detail(
    db: AsyncSession, product_id: uuid.UUID
) -> Product | None:
    """Get a single product by ID."""
    stmt = select(Product).where(Product.id == product_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

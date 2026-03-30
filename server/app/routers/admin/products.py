"""Admin product management router.

Requirements:
- 12.1: Create product with all fields
- 12.2: Update product info
- 12.3: Modify stock with change log
- 12.4: Toggle product status (active/inactive)
- 12.5: List products with category/status filter
"""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.product import Product
from app.models.stock_log import StockLog
from app.models.user import User
from app.routers.admin.users import get_admin_user
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.product import (
    AdminProductCreate,
    AdminProductStatusUpdate,
    AdminProductStockUpdate,
    AdminProductUpdate,
    ProductDetail,
)

router = APIRouter(prefix="/api/v1/admin/products", tags=["管理后台-商品管理"])


@router.get("", response_model=ApiResponse)
async def list_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=20),
    category: str | None = Query(default=None, description="按分类筛选"),
    status: str | None = Query(default=None, description="状态筛选: active/inactive"),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """List all products with pagination and optional filters.

    Requirement 12.5: Product list with category/status filter.
    """
    base_query = select(Product)
    count_query = select(func.count(Product.id))

    if category:
        base_query = base_query.where(Product.category == category)
        count_query = count_query.where(Product.category == category)
    if status:
        base_query = base_query.where(Product.status == status)
        count_query = count_query.where(Product.status == status)

    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    offset = (page - 1) * page_size
    query = base_query.order_by(Product.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    products = result.scalars().all()

    items = [ProductDetail.model_validate(p) for p in products]
    paginated = PaginatedResponse[ProductDetail].create(
        items=items, total=total, page=page, page_size=page_size
    )
    return ApiResponse(data=paginated.model_dump(mode="json"))


@router.post("", response_model=ApiResponse)
async def create_product(
    body: AdminProductCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """Create a new product.

    Requirement 12.1: Create product with all fields.
    Requirement 12.2: Validate required fields.
    """
    product = Product(
        name=body.name,
        category=body.category,
        price=body.price,
        specification=body.specification,
        description=body.description,
        image_url=body.image_url,
        stock=body.stock,
    )
    db.add(product)
    await db.flush()
    await db.refresh(product)

    detail = ProductDetail.model_validate(product)
    return ApiResponse(message="商品创建成功", data=detail.model_dump(mode="json"))


@router.put("/{product_id}", response_model=ApiResponse)
async def update_product(
    product_id: uuid.UUID,
    body: AdminProductUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """Update an existing product's information.

    Requirement 12.2: Update product info.
    """
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if product is None:
        return ApiResponse(code=404, message="商品不存在")

    update_data = body.model_dump(exclude_unset=True)
    if update_data:
        await db.execute(
            update(Product).where(Product.id == product_id).values(**update_data)
        )
        await db.flush()

    # Re-fetch updated product
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one()
    detail = ProductDetail.model_validate(product)
    return ApiResponse(message="商品信息已更新", data=detail.model_dump(mode="json"))


@router.put("/{product_id}/status", response_model=ApiResponse)
async def update_product_status(
    product_id: uuid.UUID,
    body: AdminProductStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """Toggle product status between active and inactive (上下架).

    Requirement 12.4: Product publish/unpublish.
    """
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if product is None:
        return ApiResponse(code=404, message="商品不存在")

    await db.execute(
        update(Product).where(Product.id == product_id).values(status=body.status)
    )

    status_label = "已上架" if body.status == "active" else "已下架"
    return ApiResponse(message=status_label)


@router.put("/{product_id}/stock", response_model=ApiResponse)
async def update_product_stock(
    product_id: uuid.UUID,
    body: AdminProductStockUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """Modify product stock and record change log.

    Requirement 12.3: Update stock and record to stock_logs.
    """
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if product is None:
        return ApiResponse(code=404, message="商品不存在")

    new_stock = product.stock + body.change_amount
    if new_stock < 0:
        return ApiResponse(code=400, message="库存不足，无法减少")

    # Update stock
    await db.execute(
        update(Product).where(Product.id == product_id).values(stock=new_stock)
    )

    # Record stock change log
    log = StockLog(
        product_id=product_id,
        change_amount=body.change_amount,
        reason=body.reason,
        operator_id=admin.id,
    )
    db.add(log)
    await db.flush()

    return ApiResponse(
        message="库存已更新",
        data={"stock": new_stock, "change_amount": body.change_amount},
    )

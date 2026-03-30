"""Product router — public product browsing endpoints.

Requirements:
- 7.1: GET /api/v1/products — product list with category filter
- 7.2: GET /api/v1/products/{product_id} — product detail
"""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.product import ProductDetail, ProductSearchParams
from app.services.product_service import get_product_detail, list_products

router = APIRouter(prefix="/api/v1/products", tags=["商品浏览"])


@router.get("", response_model=ApiResponse)
async def list_products_endpoint(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=20),
    category: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """List products with pagination and optional category filter."""
    params = ProductSearchParams(
        page=page, page_size=page_size, category=category
    )
    result = await list_products(db, params)
    return ApiResponse(data=result.model_dump())


@router.get("/{product_id}", response_model=ApiResponse)
async def product_detail_endpoint(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """Get product detail by ID."""
    product = await get_product_detail(db, product_id)
    if product is None:
        return ApiResponse(code=404, message="商品不存在")
    detail = ProductDetail.model_validate(product)
    return ApiResponse(data=detail.model_dump(mode="json"))

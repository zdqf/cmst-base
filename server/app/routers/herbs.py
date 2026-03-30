"""Herb router — public herb browsing endpoints.

Requirements:
- 2.2: GET /api/v1/herbs/daily — today's recommended herb
- 3.2: Category browsing
- 3.3: Keyword search
- 3.4: Paginated query, max 20 per page
- 3.5: Herb detail
"""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.herb import HerbDetail, HerbSearchParams
from app.services.herb_service import get_daily_herb, get_herb_detail, list_herbs

router = APIRouter(prefix="/api/v1/herbs", tags=["中药科普"])


@router.get("", response_model=ApiResponse)
async def list_herbs_endpoint(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=20),
    category: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """List herbs with pagination, optional category filter and keyword search."""
    params = HerbSearchParams(
        page=page, page_size=page_size, category=category, keyword=keyword
    )
    result = await list_herbs(db, params)
    return ApiResponse(data=result.model_dump())


@router.get("/daily", response_model=ApiResponse)
async def daily_herb_endpoint(
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """Get today's recommended herb."""
    herb = await get_daily_herb(db)
    if herb is None:
        return ApiResponse(code=404, message="暂无推荐草本")
    detail = HerbDetail.model_validate(herb)
    return ApiResponse(data=detail.model_dump(mode="json"))


@router.get("/{herb_id}", response_model=ApiResponse)
async def herb_detail_endpoint(
    herb_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    """Get herb detail by ID."""
    herb = await get_herb_detail(db, herb_id)
    if herb is None:
        return ApiResponse(code=404, message="中药信息不存在")
    detail = HerbDetail.model_validate(herb)
    return ApiResponse(data=detail.model_dump(mode="json"))

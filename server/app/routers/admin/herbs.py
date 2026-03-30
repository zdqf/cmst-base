"""Admin herb content management router.

Requirements:
- 11.1: Create herb with all standardized fields
- 11.2: Validate all required fields on create
- 11.3: Edit existing herb content
- 11.4: Toggle herb status (active/inactive for 上下架)
- 11.5: AI-generated herb content draft for admin review
"""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.herb import Herb
from app.models.user import User
from app.routers.admin.users import get_admin_user
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.herb import (
    AdminHerbCreate,
    AdminHerbStatusUpdate,
    AdminHerbUpdate,
    HerbDetail,
)
from app.services.ai_service import generate_herb_content

router = APIRouter(prefix="/api/v1/admin/herbs", tags=["管理后台-中药管理"])


@router.get("", response_model=ApiResponse)
async def list_herbs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=20),
    category: str | None = Query(default=None, description="按分类筛选"),
    keyword: str | None = Query(default=None, description="关键词搜索"),
    status: str | None = Query(default=None, description="状态筛选: active/inactive"),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """List all herbs with pagination (admin view — includes inactive).

    Requirement 11.4: Admin can see both active and inactive herbs.
    """
    base_query = select(Herb)
    count_query = select(func.count(Herb.id))

    if category:
        base_query = base_query.where(Herb.category == category)
        count_query = count_query.where(Herb.category == category)
    if keyword:
        base_query = base_query.where(Herb.name.ilike(f"%{keyword}%"))
        count_query = count_query.where(Herb.name.ilike(f"%{keyword}%"))
    if status:
        base_query = base_query.where(Herb.status == status)
        count_query = count_query.where(Herb.status == status)

    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    offset = (page - 1) * page_size
    query = base_query.order_by(Herb.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    herbs = result.scalars().all()

    items = [HerbDetail.model_validate(h) for h in herbs]
    paginated = PaginatedResponse[HerbDetail].create(
        items=items, total=total, page=page, page_size=page_size
    )
    return ApiResponse(data=paginated.model_dump(mode="json"))


@router.post("", response_model=ApiResponse)
async def create_herb(
    body: AdminHerbCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """Create a new herb entry.

    Requirement 11.1, 11.2: Create with all standardized fields, validate required.
    """
    # Check for duplicate name
    existing = await db.execute(select(Herb).where(Herb.name == body.name))
    if existing.scalar_one_or_none() is not None:
        return ApiResponse(code=400, message="该中药名称已存在")

    herb = Herb(
        name=body.name,
        category=body.category,
        origin_and_form=body.origin_and_form,
        flavor_meridian=body.flavor_meridian,
        common_pairings=body.common_pairings,
        unsuitable_groups=body.unsuitable_groups,
        precautions=body.precautions,
    )
    db.add(herb)
    await db.flush()
    await db.refresh(herb)

    detail = HerbDetail.model_validate(herb)
    return ApiResponse(message="中药创建成功", data=detail.model_dump(mode="json"))


@router.put("/{herb_id}", response_model=ApiResponse)
async def update_herb(
    herb_id: uuid.UUID,
    body: AdminHerbUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """Update an existing herb's information.

    Requirement 11.3: Edit existing herb content.
    """
    result = await db.execute(select(Herb).where(Herb.id == herb_id))
    herb = result.scalar_one_or_none()

    if herb is None:
        return ApiResponse(code=404, message="中药信息不存在")

    # Check name uniqueness if name is being changed
    update_data = body.model_dump(exclude_unset=True)
    if "name" in update_data and update_data["name"] != herb.name:
        dup = await db.execute(
            select(Herb).where(Herb.name == update_data["name"], Herb.id != herb_id)
        )
        if dup.scalar_one_or_none() is not None:
            return ApiResponse(code=400, message="该中药名称已存在")

    if update_data:
        await db.execute(
            update(Herb).where(Herb.id == herb_id).values(**update_data)
        )
        await db.flush()

    # Re-fetch updated herb
    result = await db.execute(select(Herb).where(Herb.id == herb_id))
    herb = result.scalar_one()
    detail = HerbDetail.model_validate(herb)
    return ApiResponse(message="中药信息已更新", data=detail.model_dump(mode="json"))


@router.put("/{herb_id}/status", response_model=ApiResponse)
async def update_herb_status(
    herb_id: uuid.UUID,
    body: AdminHerbStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """Toggle herb status between active and inactive (上下架).

    Requirement 11.4: Support herb publish/unpublish.
    """
    result = await db.execute(select(Herb).where(Herb.id == herb_id))
    herb = result.scalar_one_or_none()

    if herb is None:
        return ApiResponse(code=404, message="中药信息不存在")

    await db.execute(
        update(Herb).where(Herb.id == herb_id).values(status=body.status)
    )

    status_label = "已上架" if body.status == "active" else "已下架"
    return ApiResponse(message=status_label)


@router.post("/{herb_id}/generate-content", response_model=ApiResponse)
async def generate_herb_content_endpoint(
    herb_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """Call AI service to generate herb content draft for admin review.

    Requirement 11.5: AI-generated herb content using "科普内容生成" prompt.
    """
    result = await db.execute(select(Herb).where(Herb.id == herb_id))
    herb = result.scalar_one_or_none()

    if herb is None:
        return ApiResponse(code=404, message="中药信息不存在")

    try:
        content = await generate_herb_content(db, herb.name)
    except ValueError as exc:
        return ApiResponse(code=500, message=str(exc))

    return ApiResponse(data={"content": content})

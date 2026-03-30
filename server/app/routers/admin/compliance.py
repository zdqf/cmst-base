"""Admin compliance word management router.

Requirements:
- 15.5: Admin can add or modify forbidden words list
"""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.compliance_word import ComplianceWord
from app.models.user import User
from app.routers.admin.users import get_admin_user
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.compliance import (
    ComplianceWordCreate,
    ComplianceWordResponse,
    ComplianceWordUpdate,
)

router = APIRouter(prefix="/api/v1/admin/compliance", tags=["管理后台-合规配置"])


@router.get("", response_model=ApiResponse)
async def list_compliance_words(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """List all compliance words with pagination.

    Requirement 15.5: Manage forbidden words list.
    """
    count_result = await db.execute(select(func.count(ComplianceWord.id)))
    total = count_result.scalar_one()

    offset = (page - 1) * page_size
    query = (
        select(ComplianceWord)
        .order_by(ComplianceWord.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    words = result.scalars().all()

    items = [ComplianceWordResponse.model_validate(w) for w in words]
    paginated = PaginatedResponse[ComplianceWordResponse].create(
        items=items, total=total, page=page, page_size=page_size
    )
    return ApiResponse(data=paginated.model_dump(mode="json"))


@router.post("", response_model=ApiResponse)
async def create_compliance_word(
    body: ComplianceWordCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """Create a new compliance word.

    Requirement 15.5: Add forbidden words.
    """
    # Check for duplicate forbidden_word
    existing = await db.execute(
        select(ComplianceWord).where(
            ComplianceWord.forbidden_word == body.forbidden_word
        )
    )
    if existing.scalar_one_or_none() is not None:
        return ApiResponse(code=400, message="该违规词汇已存在")

    word = ComplianceWord(
        forbidden_word=body.forbidden_word,
        replacement=body.replacement,
    )
    db.add(word)
    await db.flush()
    await db.refresh(word)

    detail = ComplianceWordResponse.model_validate(word)
    return ApiResponse(message="违规词汇已添加", data=detail.model_dump(mode="json"))


@router.put("/{word_id}", response_model=ApiResponse)
async def update_compliance_word(
    word_id: uuid.UUID,
    body: ComplianceWordUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """Update an existing compliance word.

    Requirement 15.5: Modify forbidden words.
    """
    result = await db.execute(
        select(ComplianceWord).where(ComplianceWord.id == word_id)
    )
    word = result.scalar_one_or_none()

    if word is None:
        return ApiResponse(code=404, message="违规词汇不存在")

    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        return ApiResponse(message="无更新内容")

    # If updating forbidden_word, check for duplicates
    if "forbidden_word" in update_data:
        dup = await db.execute(
            select(ComplianceWord).where(
                ComplianceWord.forbidden_word == update_data["forbidden_word"],
                ComplianceWord.id != word_id,
            )
        )
        if dup.scalar_one_or_none() is not None:
            return ApiResponse(code=400, message="该违规词汇已存在")

    await db.execute(
        update(ComplianceWord)
        .where(ComplianceWord.id == word_id)
        .values(**update_data)
    )
    await db.flush()

    # Re-fetch updated word
    result = await db.execute(
        select(ComplianceWord).where(ComplianceWord.id == word_id)
    )
    updated_word = result.scalar_one()
    detail = ComplianceWordResponse.model_validate(updated_word)
    return ApiResponse(message="违规词汇已更新", data=detail.model_dump(mode="json"))


@router.delete("/{word_id}", response_model=ApiResponse)
async def delete_compliance_word(
    word_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """Delete a compliance word.

    Requirement 15.5: Remove forbidden words.
    """
    result = await db.execute(
        select(ComplianceWord).where(ComplianceWord.id == word_id)
    )
    word = result.scalar_one_or_none()

    if word is None:
        return ApiResponse(code=404, message="违规词汇不存在")

    await db.execute(
        delete(ComplianceWord).where(ComplianceWord.id == word_id)
    )
    return ApiResponse(message="违规词汇已删除")

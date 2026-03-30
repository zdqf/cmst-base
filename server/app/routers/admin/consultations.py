"""Admin consultation management router.

Requirements:
- 9.1: List consultations with status filter (pending/processing/completed)
- 9.2: View consultation details and processing history
- 9.3: Update consultation status or add admin notes, record operation time
- 6.4: Notify admin on new consultation
- 6.5: Record status change time and operator
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.consultation import Consultation
from app.models.user import User
from app.routers.admin.users import get_admin_user
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.consultation import (
    AdminConsultationItem,
    AdminConsultationNotesUpdate,
    AdminConsultationStatusUpdate,
)

router = APIRouter(prefix="/api/v1/admin/consultations", tags=["管理后台-咨询管理"])


@router.get("", response_model=ApiResponse)
async def list_consultations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=20),
    status: str | None = Query(default=None, description="状态筛选: pending/processing/completed"),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """List all consultations with pagination and optional status filter.

    Requirement 9.1: Consultation list with status filter.
    """
    base_query = select(Consultation)
    count_query = select(func.count(Consultation.id))

    if status:
        base_query = base_query.where(Consultation.status == status)
        count_query = count_query.where(Consultation.status == status)

    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    offset = (page - 1) * page_size
    query = base_query.order_by(Consultation.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    consultations = result.scalars().all()

    items = [AdminConsultationItem.model_validate(c) for c in consultations]
    paginated = PaginatedResponse[AdminConsultationItem].create(
        items=items, total=total, page=page, page_size=page_size
    )
    return ApiResponse(data=paginated.model_dump(mode="json"))


@router.put("/{consultation_id}/status", response_model=ApiResponse)
async def update_consultation_status(
    consultation_id: uuid.UUID,
    body: AdminConsultationStatusUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """Update consultation status and record operator info.

    Requirement 9.3, 6.5: Update status, record change time and operator.
    """
    result = await db.execute(
        select(Consultation).where(Consultation.id == consultation_id)
    )
    consultation = result.scalar_one_or_none()

    if consultation is None:
        return ApiResponse(code=404, message="咨询记录不存在")

    now = datetime.now(timezone.utc)
    await db.execute(
        update(Consultation)
        .where(Consultation.id == consultation_id)
        .values(
            status=body.status,
            handled_by=admin.id,
            handled_at=now,
        )
    )

    return ApiResponse(message="状态已更新")


@router.put("/{consultation_id}/notes", response_model=ApiResponse)
async def update_consultation_notes(
    consultation_id: uuid.UUID,
    body: AdminConsultationNotesUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """Add or update admin notes on a consultation.

    Requirement 9.3: Add processing notes, record operation time.
    """
    result = await db.execute(
        select(Consultation).where(Consultation.id == consultation_id)
    )
    consultation = result.scalar_one_or_none()

    if consultation is None:
        return ApiResponse(code=404, message="咨询记录不存在")

    now = datetime.now(timezone.utc)
    await db.execute(
        update(Consultation)
        .where(Consultation.id == consultation_id)
        .values(
            admin_notes=body.admin_notes,
            handled_by=admin.id,
            handled_at=now,
        )
    )

    return ApiResponse(message="备注已更新")

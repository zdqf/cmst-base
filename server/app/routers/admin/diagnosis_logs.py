"""Admin diagnosis log management router.

Requirements:
- 10.1: Paginated list of AI diagnosis logs with user info, time, summaries
- 10.2: View full diagnosis log detail (complete input_data and ai_output)
- 10.3: Filter diagnosis logs by time range and user
"""

import uuid
from datetime import date, datetime, time, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.ai_diagnosis_log import AIDiagnosisLog
from app.models.user import User
from app.routers.admin.users import get_admin_user
from app.schemas.ai import AdminDiagnosisLogDetail, AdminDiagnosisLogItem
from app.schemas.common import ApiResponse, PaginatedResponse

router = APIRouter(
    prefix="/api/v1/admin/diagnosis-logs",
    tags=["管理后台-问诊记录管理"],
)


@router.get("", response_model=ApiResponse)
async def list_diagnosis_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=20),
    user_id: uuid.UUID | None = Query(default=None, description="按用户 ID 筛选"),
    start_date: date | None = Query(default=None, description="开始日期 (YYYY-MM-DD)"),
    end_date: date | None = Query(default=None, description="结束日期 (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """List all AI diagnosis logs with pagination and optional filters.

    Requirement 10.1: Paginated diagnosis log list.
    Requirement 10.3: Filter by time range and user.
    """
    base_query = select(AIDiagnosisLog)
    count_query = select(func.count(AIDiagnosisLog.id))

    if user_id is not None:
        base_query = base_query.where(AIDiagnosisLog.user_id == user_id)
        count_query = count_query.where(AIDiagnosisLog.user_id == user_id)

    if start_date is not None:
        start_dt = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
        base_query = base_query.where(AIDiagnosisLog.created_at >= start_dt)
        count_query = count_query.where(AIDiagnosisLog.created_at >= start_dt)

    if end_date is not None:
        end_dt = datetime.combine(end_date, time.max, tzinfo=timezone.utc)
        base_query = base_query.where(AIDiagnosisLog.created_at <= end_dt)
        count_query = count_query.where(AIDiagnosisLog.created_at <= end_dt)

    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    offset = (page - 1) * page_size
    query = (
        base_query
        .order_by(AIDiagnosisLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    logs = result.scalars().all()

    items = [AdminDiagnosisLogItem.model_validate(log) for log in logs]
    paginated = PaginatedResponse[AdminDiagnosisLogItem].create(
        items=items, total=total, page=page, page_size=page_size
    )
    return ApiResponse(data=paginated.model_dump(mode="json"))


@router.get("/{log_id}", response_model=ApiResponse)
async def get_diagnosis_log_detail(
    log_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """Get full detail of a single diagnosis log.

    Requirement 10.2: View complete input_data and ai_output.
    """
    result = await db.execute(
        select(AIDiagnosisLog).where(AIDiagnosisLog.id == log_id)
    )
    log = result.scalar_one_or_none()

    if log is None:
        return ApiResponse(code=404, message="问诊记录不存在")

    detail = AdminDiagnosisLogDetail.model_validate(log)
    return ApiResponse(data=detail.model_dump(mode="json"))

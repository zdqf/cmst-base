"""AI router — diagnosis, history, and pairing suggestion endpoints.

Requirements:
- 4.1: Structured health form submission
- 4.2: Combine user input with Prompt_Template and send to AI_Service
- 4.3: Append disclaimer to results
- 4.6: Log every AI diagnosis input/output
- 4.8: History records in time-descending order, paginated
- 5.1: Call AI_Service to generate pairing suggestions when user selects herbs
- 5.2: Use "科普助手" role Prompt_Template for pairing suggestions
- 5.3: Display disclaimer in pairing suggestion results
- 5.4: Mark unsuitable groups and precautions in pairing output
- 5.5: Include basic info links for each herb in pairing suggestions
"""

import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.ai_diagnosis_log import AIDiagnosisLog
from app.models.herb import Herb
from app.models.user import User
from app.schemas.ai import (
    DiagnosisHistoryItem,
    DiagnosisRequest,
    DiagnosisResponse,
    PairingRequest,
    PairingResponse,
)
from app.schemas.common import ApiResponse, PaginatedResponse
from app.services.ai_service import diagnose, get_pairing_suggestion

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai", tags=["AI 问诊"])


@router.post("/diagnosis", response_model=ApiResponse)
async def create_diagnosis(
    req: DiagnosisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """Submit health info for AI diagnosis (Requirements 4.1, 4.2, 4.3, 4.6)."""
    input_data = req.model_dump()
    try:
        result = await diagnose(db, current_user.id, input_data)
    except ValueError as exc:
        return ApiResponse(code=500, message=str(exc))

    # Fetch the latest log entry for this user to build the response
    stmt = (
        select(AIDiagnosisLog)
        .where(AIDiagnosisLog.user_id == current_user.id)
        .order_by(AIDiagnosisLog.created_at.desc())
        .limit(1)
    )
    log_entry = (await db.execute(stmt)).scalar_one()

    resp = DiagnosisResponse(
        id=log_entry.id,
        result=log_entry.ai_output,
        created_at=log_entry.created_at,
    )
    return ApiResponse(data=resp.model_dump(mode="json"))


@router.get("/diagnosis/history", response_model=ApiResponse)
async def diagnosis_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """List diagnosis history for current user, time descending (Requirement 4.8)."""
    # Count total
    count_stmt = (
        select(func.count())
        .select_from(AIDiagnosisLog)
        .where(AIDiagnosisLog.user_id == current_user.id)
    )
    total = (await db.execute(count_stmt)).scalar_one()

    # Fetch page
    offset = (page - 1) * page_size
    items_stmt = (
        select(AIDiagnosisLog)
        .where(AIDiagnosisLog.user_id == current_user.id)
        .order_by(AIDiagnosisLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    rows = (await db.execute(items_stmt)).scalars().all()

    items = [DiagnosisHistoryItem.model_validate(row) for row in rows]
    paginated = PaginatedResponse.create(
        items=items, total=total, page=page, page_size=page_size
    )
    return ApiResponse(data=paginated.model_dump(mode="json"))


@router.post("/pairing", response_model=ApiResponse)
async def create_pairing_suggestion(
    req: PairingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """Generate herb pairing suggestions (Requirements 5.1, 5.2, 5.3, 5.4)."""
    # Look up herb names from IDs
    stmt = select(Herb).where(Herb.id.in_(req.herb_ids))
    result = await db.execute(stmt)
    herbs = result.scalars().all()

    found_ids = {herb.id for herb in herbs}
    missing_ids = [str(hid) for hid in req.herb_ids if hid not in found_ids]
    if missing_ids:
        return ApiResponse(
            code=400,
            message=f"未找到以下中药: {', '.join(missing_ids)}",
        )

    herb_names = [herb.name for herb in herbs]

    try:
        suggestion = await get_pairing_suggestion(db, herb_names)
    except ValueError as exc:
        return ApiResponse(code=500, message=str(exc))

    resp = PairingResponse(result=suggestion)
    return ApiResponse(data=resp.model_dump())

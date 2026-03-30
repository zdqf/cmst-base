"""Consultation router — submit and query consultation endpoints.

Requirements:
- 6.1: Form-based consultation submission (name, contact, subject, description)
- 6.2: Store consultation and return success confirmation
- 6.3: Display WeChat contact info after successful submission
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.consultation import (
    ConsultationCreateRequest,
    ConsultationResponse,
)
from app.services.consultation_service import WECHAT_CONTACT, create_consultation

router = APIRouter(prefix="/api/v1/consultations", tags=["私域咨询"])


@router.post("", response_model=ApiResponse)
async def submit_consultation(
    req: ConsultationCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """Submit a consultation request (Requirements 6.1, 6.2, 6.3).

    Creates a consultation record and returns it along with WeChat contact info.
    """
    consultation = await create_consultation(db, current_user.id, req)
    consultation_data = ConsultationResponse.model_validate(consultation)

    return ApiResponse(
        data={
            "consultation": consultation_data.model_dump(mode="json"),
            "contact": WECHAT_CONTACT.model_dump(),
        }
    )

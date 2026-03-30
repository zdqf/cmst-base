"""Consultation Pydantic schemas for API request/response models.

Requirements:
- 6.1: Form-based consultation submission (name, contact, subject, description)
- 6.2: Store consultation and return success confirmation
- 6.3: Display WeChat contact info after successful submission
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ConsultationCreateRequest(BaseModel):
    """Consultation submission form (Requirement 6.1)."""

    name: str = Field(..., min_length=1, max_length=100, description="姓名")
    contact: str = Field(..., min_length=1, max_length=100, description="联系方式")
    subject: str = Field(..., min_length=1, max_length=200, description="咨询主题")
    description: str = Field(..., min_length=1, description="详细描述")


class ConsultationResponse(BaseModel):
    """Consultation record response (Requirement 6.2)."""

    id: uuid.UUID
    name: str
    contact: str
    subject: str
    description: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ContactInfo(BaseModel):
    """WeChat contact info returned after consultation submission (Requirement 6.3)."""

    wechat_id: str = Field(..., description="微信号")
    qr_code_url: str = Field(..., description="二维码图片链接")


# ---------------------------------------------------------------------------
# Admin consultation schemas (Requirements 9.1, 9.2, 9.3, 6.4, 6.5)
# ---------------------------------------------------------------------------


class AdminConsultationItem(BaseModel):
    """Consultation list item for admin panel (Requirement 9.1)."""

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    contact: str
    subject: str
    description: str
    status: str
    admin_notes: str | None = None
    handled_by: uuid.UUID | None = None
    handled_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminConsultationStatusUpdate(BaseModel):
    """Request body for updating consultation status (Requirement 9.3, 6.5)."""

    status: str = Field(
        ...,
        pattern="^(pending|processing|completed)$",
        description="咨询状态: pending / processing / completed",
    )


class AdminConsultationNotesUpdate(BaseModel):
    """Request body for adding admin notes to a consultation (Requirement 9.3)."""

    admin_notes: str = Field(..., min_length=1, description="管理员备注")

"""Consultation service layer — business logic for consultation operations.

Requirements:
- 6.1: Form-based consultation submission
- 6.2: Store consultation record and return success confirmation
- 6.3: Return WeChat contact info after submission
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.consultation import Consultation
from app.schemas.consultation import ConsultationCreateRequest, ContactInfo

# Placeholder WeChat contact info (Requirement 6.3)
WECHAT_CONTACT = ContactInfo(
    wechat_id="caomushentang",
    qr_code_url="https://example.com/qrcode/caomushentang.png",
)


async def create_consultation(
    db: AsyncSession,
    user_id: uuid.UUID,
    data: ConsultationCreateRequest,
) -> Consultation:
    """Create and persist a new consultation record.

    Args:
        db: Database session.
        user_id: The authenticated user's ID.
        data: Consultation form data.

    Returns:
        The created Consultation ORM instance.
    """
    consultation = Consultation(
        user_id=user_id,
        name=data.name,
        contact=data.contact,
        subject=data.subject,
        description=data.description,
    )
    db.add(consultation)
    await db.flush()
    await db.refresh(consultation)
    return consultation

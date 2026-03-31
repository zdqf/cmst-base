"""Temporary SMS code storage model for Redis fallback.

When Redis is unavailable, SMS verification codes are stored in this table
with an expiry timestamp. When Redis recovers, the system automatically
switches back to Redis storage.

Requirements: 25.1, 25.2
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SmsCodeTemp(Base):
    """Temporary database storage for SMS verification codes.

    Used as a fallback when Redis is unavailable.
    """

    __tablename__ = "sms_code_temp"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    phone: Mapped[str] = mapped_column(
        String(20), unique=True, index=True, nullable=False
    )
    code: Mapped[str] = mapped_column(String(6), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

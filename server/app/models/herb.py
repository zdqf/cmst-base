"""Herb model."""

import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Herb(Base):
    __tablename__ = "herbs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    origin_and_form: Mapped[str | None] = mapped_column(Text, nullable=True)
    flavor_meridian: Mapped[str | None] = mapped_column(Text, nullable=True)
    common_pairings: Mapped[str | None] = mapped_column(Text, nullable=True)
    unsuitable_groups: Mapped[str | None] = mapped_column(Text, nullable=True)
    precautions: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="active"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

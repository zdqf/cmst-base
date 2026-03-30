"""Pydantic schemas for compliance word management.

Requirements:
- 15.5: Admin can add or modify forbidden words
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ComplianceWordCreate(BaseModel):
    """Request schema for creating a compliance word."""

    forbidden_word: str = Field(..., min_length=1, max_length=100, description="违规词汇")
    replacement: str | None = Field(default=None, max_length=200, description="替换词")


class ComplianceWordUpdate(BaseModel):
    """Request schema for updating a compliance word."""

    forbidden_word: str | None = Field(default=None, min_length=1, max_length=100, description="违规词汇")
    replacement: str | None = Field(default=None, max_length=200, description="替换词")


class ComplianceWordResponse(BaseModel):
    """Response schema for a compliance word."""

    id: uuid.UUID
    forbidden_word: str
    replacement: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

"""Herb Pydantic schemas for API request/response models.

Requirements:
- 3.1: Standardized herb content fields
- 3.2: Category browsing
- 3.3: Keyword search
- 3.4: Paginated query, max 20 per page
- 3.5: Full detail display
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import PaginationParams


class HerbListItem(BaseModel):
    """Herb summary for list view."""

    id: uuid.UUID
    name: str
    category: Optional[str] = None
    status: str

    model_config = {"from_attributes": True}


class HerbDetail(BaseModel):
    """Full herb detail with all standardized fields (Requirement 3.1, 3.5)."""

    id: uuid.UUID
    name: str
    category: Optional[str] = None
    origin_and_form: Optional[str] = None
    flavor_meridian: Optional[str] = None
    common_pairings: Optional[str] = None
    unsuitable_groups: Optional[str] = None
    precautions: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HerbSearchParams(PaginationParams):
    """Search parameters extending pagination (Requirement 3.2, 3.3)."""

    category: Optional[str] = Field(default=None, description="按分类筛选")
    keyword: Optional[str] = Field(default=None, description="关键词搜索（中药名称）")


# ---------------------------------------------------------------------------
# Admin herb schemas (Requirement 11.1, 11.2, 11.3, 11.4)
# ---------------------------------------------------------------------------


class AdminHerbCreate(BaseModel):
    """Create herb request — all standardized fields (Requirement 11.1, 11.2)."""

    name: str = Field(..., min_length=1, max_length=100, description="中药名称")
    category: Optional[str] = Field(default=None, max_length=50, description="分类")
    origin_and_form: Optional[str] = Field(default=None, description="来源与形态")
    flavor_meridian: Optional[str] = Field(default=None, description="性味归经白话解释")
    common_pairings: Optional[str] = Field(default=None, description="常见搭配方向")
    unsuitable_groups: Optional[str] = Field(default=None, description="不适合人群")
    precautions: Optional[str] = Field(default=None, description="注意事项")


class AdminHerbUpdate(BaseModel):
    """Update herb request — partial update allowed (Requirement 11.3)."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="中药名称")
    category: Optional[str] = Field(default=None, max_length=50, description="分类")
    origin_and_form: Optional[str] = Field(default=None, description="来源与形态")
    flavor_meridian: Optional[str] = Field(default=None, description="性味归经白话解释")
    common_pairings: Optional[str] = Field(default=None, description="常见搭配方向")
    unsuitable_groups: Optional[str] = Field(default=None, description="不适合人群")
    precautions: Optional[str] = Field(default=None, description="注意事项")


class AdminHerbStatusUpdate(BaseModel):
    """Toggle herb status (Requirement 11.4)."""

    status: str = Field(..., pattern=r"^(active|inactive)$", description="状态: active/inactive")

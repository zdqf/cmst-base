"""Product Pydantic schemas for API request/response models.

Requirements:
- 7.1: Product list with category filtering
- 7.2: Product detail with full information
- 12.1: Admin product create
- 12.2: Admin product update
- 12.3: Admin stock modification with logging
- 12.4: Admin product status toggle
- 12.5: Admin product list with category/status filter
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import PaginationParams


class ProductListItem(BaseModel):
    """Product summary for list view (Requirement 7.1)."""

    id: uuid.UUID
    name: str
    category: Optional[str] = None
    price: Decimal
    image_url: Optional[str] = None
    stock: int
    status: str

    model_config = {"from_attributes": True}


class ProductDetail(BaseModel):
    """Full product detail with all fields (Requirement 7.2)."""

    id: uuid.UUID
    name: str
    category: Optional[str] = None
    price: Decimal
    specification: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    stock: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductSearchParams(PaginationParams):
    """Search parameters extending pagination (Requirement 7.1)."""

    category: Optional[str] = Field(
        default=None, description="按分类筛选（原药材、简加工产品、调理组合包）"
    )


# ---------------------------------------------------------------------------
# Admin schemas (Requirements 12.1–12.5)
# ---------------------------------------------------------------------------


class AdminProductCreate(BaseModel):
    """Create product request (Requirement 12.1)."""

    name: str = Field(..., min_length=1, description="商品名称")
    category: Optional[str] = Field(default=None, description="分类")
    price: Decimal = Field(..., gt=0, description="价格")
    specification: Optional[str] = Field(default=None, description="规格")
    description: Optional[str] = Field(default=None, description="描述")
    image_url: Optional[str] = Field(default=None, description="产品图片 URL")
    stock: int = Field(default=0, ge=0, description="初始库存")

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("商品名称不能为空")
        return v.strip()


class AdminProductUpdate(BaseModel):
    """Update product request (Requirement 12.2). All fields optional."""

    name: Optional[str] = Field(default=None, min_length=1, description="商品名称")
    category: Optional[str] = None
    price: Optional[Decimal] = Field(default=None, gt=0)
    specification: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class AdminProductStatusUpdate(BaseModel):
    """Toggle product status (Requirement 12.4)."""

    status: Literal["active", "inactive"]


class AdminProductStockUpdate(BaseModel):
    """Modify product stock (Requirement 12.3)."""

    change_amount: int = Field(..., description="库存变更量（正数增加，负数减少）")
    reason: str = Field(..., min_length=1, description="变更原因")

    @field_validator("change_amount")
    @classmethod
    def change_amount_not_zero(cls, v: int) -> int:
        if v == 0:
            raise ValueError("库存变更量不能为 0")
        return v


class StockLogItem(BaseModel):
    """Stock log entry for response."""

    id: uuid.UUID
    product_id: uuid.UUID
    change_amount: int
    reason: Optional[str] = None
    operator_id: Optional[uuid.UUID] = None
    created_at: datetime

    model_config = {"from_attributes": True}

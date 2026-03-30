"""Unified API response format and common Pydantic models.

Requirements:
- 17.1: Use Pydantic models for all API request/response data structures
- 17.5: Invalid request data returns 422 with detailed field validation errors
- 18.5: Unified API response format with code, message, data fields
"""

from math import ceil
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel):
    """Unified API response format (Requirement 18.5).

    All API endpoints return this structure:
    - code: 0 for success, non-zero for errors
    - message: human-readable status message
    - data: response payload (None when no data)
    """

    code: int = 0
    message: str = "success"
    data: Any = None


class PaginationParams(BaseModel):
    """Pagination request parameters.

    Requirement 3.4: 每页返回不超过 20 条记录
    """

    page: int = Field(default=1, ge=1, description="页码，从 1 开始")
    page_size: int = Field(default=10, ge=1, le=20, description="每页条数，最大 20")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper.

    Contains the paginated items along with pagination metadata.
    """

    items: list[T] = Field(default_factory=list, description="当前页数据列表")
    total: int = Field(ge=0, description="总记录数")
    page: int = Field(ge=1, description="当前页码")
    page_size: int = Field(ge=1, description="每页条数")
    total_pages: int = Field(ge=0, description="总页数")

    @classmethod
    def create(
        cls, *, items: list[T], total: int, page: int, page_size: int
    ) -> "PaginatedResponse[T]":
        """Create a PaginatedResponse with auto-calculated total_pages."""
        total_pages = ceil(total / page_size) if page_size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

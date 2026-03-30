"""Prompt template Pydantic schemas for API request/response models.

Requirements:
- 14.1: Three types of Prompt_Template editing (健康顾问, 科普助手, 科普内容生成)
- 14.2: Save new version and retain history when modifying templates
- 14.3: Use latest version of Prompt_Template in AI_Service calls
- 14.4: Test functionality — input test data and view AI output
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

VALID_PROMPT_TYPES = ("health_advisor", "pairing_assistant", "content_generator")


class PromptTemplateResponse(BaseModel):
    """Prompt template detail response."""

    id: uuid.UUID
    type: str
    role_name: str
    content: str
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PromptTemplateUpdate(BaseModel):
    """Request body for updating a prompt template (creates a new version).

    Requirement 14.2: Save new version and retain history.
    """

    content: str = Field(..., min_length=1, description="模板内容")
    role_name: str | None = Field(default=None, description="角色名称（可选，不传则沿用上一版本）")


class PromptTestRequest(BaseModel):
    """Request body for testing a prompt template.

    Requirement 14.4: Test functionality with test input.
    """

    type: str = Field(
        ...,
        description="模板类型: health_advisor/pairing_assistant/content_generator",
        pattern=f"^({'|'.join(VALID_PROMPT_TYPES)})$",
    )
    test_input: str = Field(..., min_length=1, description="测试输入内容")


class PromptTestResponse(BaseModel):
    """Response for prompt template test."""

    type: str
    test_input: str
    ai_output: str

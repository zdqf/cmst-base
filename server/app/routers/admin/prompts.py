"""Admin prompt template management router.

Requirements:
- 14.1: Three types of Prompt_Template editing (健康顾问, 科普助手, 科普内容生成)
- 14.2: Save new version and retain history when modifying templates
- 14.3: Use latest version of Prompt_Template in AI_Service calls
- 14.4: Test functionality — input test data and view AI output
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import AIAdapterFactory
from app.database import get_db
from app.models.prompt_template import PromptTemplate
from app.models.user import User
from app.routers.admin.users import get_admin_user
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.prompt import (
    VALID_PROMPT_TYPES,
    PromptTemplateResponse,
    PromptTemplateUpdate,
    PromptTestRequest,
    PromptTestResponse,
)

router = APIRouter(prefix="/api/v1/admin/prompts", tags=["管理后台-Prompt模板管理"])

# Map internal type keys to Chinese role names
TYPE_ROLE_MAP = {
    "health_advisor": "健康顾问",
    "pairing_assistant": "科普助手",
    "content_generator": "科普内容生成",
}


@router.get("", response_model=ApiResponse)
async def list_prompts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=20),
    type: str | None = Query(default=None, description="模板类型筛选"),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """List prompt templates with pagination and optional type filter.

    Requirement 14.1: Provide editing interface for three types of templates.
    """
    base_query = select(PromptTemplate)
    count_query = select(func.count(PromptTemplate.id))

    if type:
        base_query = base_query.where(PromptTemplate.type == type)
        count_query = count_query.where(PromptTemplate.type == type)

    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    offset = (page - 1) * page_size
    query = (
        base_query
        .order_by(PromptTemplate.type, PromptTemplate.version.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    templates = result.scalars().all()

    items = [PromptTemplateResponse.model_validate(t) for t in templates]
    paginated = PaginatedResponse[PromptTemplateResponse].create(
        items=items, total=total, page=page, page_size=page_size,
    )
    return ApiResponse(data=paginated.model_dump(mode="json"))


@router.get("/{prompt_type}/active", response_model=ApiResponse)
async def get_active_prompt(
    prompt_type: str,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """Get the active template for a given type.

    Requirement 14.3: Use latest version of Prompt_Template.
    """
    if prompt_type not in VALID_PROMPT_TYPES:
        return ApiResponse(code=400, message=f"无效的模板类型: {prompt_type}")

    result = await db.execute(
        select(PromptTemplate)
        .where(
            PromptTemplate.type == prompt_type,
            PromptTemplate.is_active.is_(True),
        )
        .order_by(PromptTemplate.version.desc())
        .limit(1)
    )
    template = result.scalar_one_or_none()

    if template is None:
        return ApiResponse(code=404, message="未找到该类型的活跃模板")

    item = PromptTemplateResponse.model_validate(template)
    return ApiResponse(data=item.model_dump(mode="json"))


@router.put("/{prompt_type}", response_model=ApiResponse)
async def update_prompt(
    prompt_type: str,
    body: PromptTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """Update template content — creates a new version, sets it active, deactivates previous.

    Requirement 14.2: Save new version and retain history.
    """
    if prompt_type not in VALID_PROMPT_TYPES:
        return ApiResponse(code=400, message=f"无效的模板类型: {prompt_type}")

    # Find current active template to determine next version
    result = await db.execute(
        select(PromptTemplate)
        .where(
            PromptTemplate.type == prompt_type,
            PromptTemplate.is_active.is_(True),
        )
        .order_by(PromptTemplate.version.desc())
        .limit(1)
    )
    current = result.scalar_one_or_none()

    next_version = (current.version + 1) if current else 1
    role_name = body.role_name or (current.role_name if current else TYPE_ROLE_MAP.get(prompt_type, prompt_type))

    # Deactivate all existing active templates of this type
    await db.execute(
        update(PromptTemplate)
        .where(
            PromptTemplate.type == prompt_type,
            PromptTemplate.is_active.is_(True),
        )
        .values(is_active=False)
    )

    # Create new version
    new_template = PromptTemplate(
        type=prompt_type,
        role_name=role_name,
        content=body.content,
        version=next_version,
        is_active=True,
    )
    db.add(new_template)
    await db.flush()
    await db.refresh(new_template)

    item = PromptTemplateResponse.model_validate(new_template)
    return ApiResponse(message="模板已更新", data=item.model_dump(mode="json"))


@router.get("/{prompt_type}/history", response_model=ApiResponse)
async def get_prompt_history(
    prompt_type: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """Get version history for a template type.

    Requirement 14.2: Retain history versions.
    """
    if prompt_type not in VALID_PROMPT_TYPES:
        return ApiResponse(code=400, message=f"无效的模板类型: {prompt_type}")

    base_query = select(PromptTemplate).where(PromptTemplate.type == prompt_type)
    count_query = select(func.count(PromptTemplate.id)).where(PromptTemplate.type == prompt_type)

    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    offset = (page - 1) * page_size
    query = base_query.order_by(PromptTemplate.version.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    templates = result.scalars().all()

    items = [PromptTemplateResponse.model_validate(t) for t in templates]
    paginated = PaginatedResponse[PromptTemplateResponse].create(
        items=items, total=total, page=page, page_size=page_size,
    )
    return ApiResponse(data=paginated.model_dump(mode="json"))


@router.post("/test", response_model=ApiResponse)
async def test_prompt(
    body: PromptTestRequest,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_admin_user),
) -> ApiResponse:
    """Test a prompt: call AI service with the active template and test input.

    Requirement 14.4: Test functionality — input test data and view AI output.
    """
    # Get active template for the requested type
    result = await db.execute(
        select(PromptTemplate)
        .where(
            PromptTemplate.type == body.type,
            PromptTemplate.is_active.is_(True),
        )
        .order_by(PromptTemplate.version.desc())
        .limit(1)
    )
    template = result.scalar_one_or_none()

    if template is None:
        return ApiResponse(code=404, message="未找到该类型的活跃模板")

    full_prompt = f"{template.content}\n\n{body.test_input}"

    try:
        adapter = AIAdapterFactory.create()
        ai_output = await adapter.generate(full_prompt, context={"test_input": body.test_input})
    except Exception:
        return ApiResponse(code=500, message="AI 服务暂时不可用，请稍后再试")

    test_response = PromptTestResponse(
        type=body.type,
        test_input=body.test_input,
        ai_output=ai_output,
    )
    return ApiResponse(data=test_response.model_dump())

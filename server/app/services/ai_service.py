"""AI service layer — diagnosis, pairing suggestions, and herb content generation.

Requirements:
- 4.2: Combine user input with Prompt_Template and send to AI_Service
- 4.3: Append Disclaimer to AI diagnosis results
- 4.5: Use "健康顾问" role Prompt_Template, restrict from diagnosing/prescribing
- 4.6: Log every AI diagnosis input/output to ai_diagnosis_logs
- 4.7: On AI failure, return friendly error and log error
- 5.1: Call AI_Service to generate pairing suggestions when user selects herbs
- 5.2: Use "科普助手" role Prompt_Template for pairing suggestions
- 11.5: Use "科普内容生成" role Prompt_Template to generate herb content drafts
"""

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import AIAdapterFactory
from app.compliance.filter import ComplianceFilter
from app.models.ai_diagnosis_log import AIDiagnosisLog
from app.models.prompt_template import PromptTemplate

logger = logging.getLogger(__name__)

DISCLAIMER = (
    "以下内容仅为传统中药知识科普与调理方向参考，"
    "不构成医疗诊断或治疗建议，如有健康问题请咨询专业医师"
)

_compliance_filter = ComplianceFilter()


async def get_active_prompt(
    db: AsyncSession, prompt_type: str
) -> PromptTemplate | None:
    """Get the latest active prompt template by type.

    Args:
        db: Database session.
        prompt_type: The prompt template type (e.g. "健康顾问").

    Returns:
        The active PromptTemplate with the highest version, or None.
    """
    result = await db.execute(
        select(PromptTemplate)
        .where(PromptTemplate.type == prompt_type, PromptTemplate.is_active.is_(True))
        .order_by(PromptTemplate.version.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def diagnose(
    db: AsyncSession, user_id: uuid.UUID, input_data: dict
) -> str:
    """Run AI diagnosis: prompt → AI → compliance filter → disclaimer → log.

    Args:
        db: Database session.
        user_id: The requesting user's ID.
        input_data: Structured user health info (age, gender, symptoms, etc.).

    Returns:
        Filtered AI output with disclaimer appended.

    Raises:
        ValueError: When the AI call fails, with a user-friendly message.
    """
    template = await get_active_prompt(db, "健康顾问")
    prompt_content = template.content if template else ""
    prompt_version = str(template.version) if template else "unknown"

    # Build the full prompt from template + user input
    user_description = "\n".join(f"{k}: {v}" for k, v in input_data.items())
    full_prompt = f"{prompt_content}\n\n用户信息：\n{user_description}"

    try:
        adapter = AIAdapterFactory.create()
        raw_output = await adapter.generate(full_prompt, context=input_data)
    except Exception as exc:
        logger.error("AI diagnosis call failed for user %s: %s", user_id, exc)
        raise ValueError("AI 服务暂时不可用，请稍后再试") from exc

    # Compliance filter + disclaimer
    filtered_output = _compliance_filter.filter(raw_output)
    result = f"{filtered_output}\n\n{DISCLAIMER}"

    # Persist diagnosis log
    log_entry = AIDiagnosisLog(
        user_id=user_id,
        input_data=input_data,
        ai_output=result,
        prompt_version=prompt_version,
    )
    db.add(log_entry)
    await db.flush()

    return result


async def get_pairing_suggestion(
    db: AsyncSession, herb_names: list[str]
) -> str:
    """Generate herb pairing suggestions: prompt → AI → compliance filter → disclaimer.

    Args:
        db: Database session.
        herb_names: List of selected herb names.

    Returns:
        Filtered AI pairing suggestion with disclaimer appended.

    Raises:
        ValueError: When the AI call fails, with a user-friendly message.
    """
    template = await get_active_prompt(db, "科普助手")
    prompt_content = template.content if template else ""

    herbs_text = "、".join(herb_names)
    full_prompt = f"{prompt_content}\n\n用户选择的中药：{herbs_text}"

    try:
        adapter = AIAdapterFactory.create()
        raw_output = await adapter.generate(full_prompt, context={"herb_names": herb_names})
    except Exception as exc:
        logger.error("AI pairing suggestion failed for herbs %s: %s", herb_names, exc)
        raise ValueError("AI 服务暂时不可用，请稍后再试") from exc

    filtered_output = _compliance_filter.filter(raw_output)
    return f"{filtered_output}\n\n{DISCLAIMER}"


async def generate_herb_content(
    db: AsyncSession, herb_name: str
) -> str:
    """Generate herb encyclopedia content draft (admin review required).

    Args:
        db: Database session.
        herb_name: Name of the herb to generate content for.

    Returns:
        Raw AI output (no compliance filter — admin will review).

    Raises:
        ValueError: When the AI call fails, with a user-friendly message.
    """
    template = await get_active_prompt(db, "科普内容生成")
    prompt_content = template.content if template else ""

    full_prompt = f"{prompt_content}\n\n请为以下中药生成科普内容：{herb_name}"

    try:
        adapter = AIAdapterFactory.create()
        return await adapter.generate(full_prompt, context={"herb_name": herb_name})
    except Exception as exc:
        logger.error("AI herb content generation failed for %s: %s", herb_name, exc)
        raise ValueError("AI 服务暂时不可用，请稍后再试") from exc

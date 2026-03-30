"""Unit tests for AI service layer (Task 4.6).

Validates Requirements:
- 4.2: Combine user input with Prompt_Template and send to AI_Service
- 4.3: Append Disclaimer to AI diagnosis results
- 4.7: On AI failure, return friendly error and log error
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.ai_service import (
    DISCLAIMER,
    diagnose,
    generate_herb_content,
    get_active_prompt,
    get_pairing_suggestion,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_db_with_prompt(prompt_type: str, content: str, version: int = 1):
    """Return an AsyncMock db whose execute() yields a matching PromptTemplate."""
    template = MagicMock()
    template.type = prompt_type
    template.content = content
    template.version = version
    template.is_active = True

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = template

    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_result
    return mock_db, template


def _mock_db_no_prompt():
    """Return an AsyncMock db whose execute() yields None (no template)."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None

    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_result
    return mock_db


# ---------------------------------------------------------------------------
# 1. diagnose — success path
# ---------------------------------------------------------------------------


class TestDiagnoseSuccess:
    """Validates: Requirements 4.2, 4.3"""

    @pytest.mark.asyncio
    @patch("app.services.ai_service.AIAdapterFactory")
    async def test_diagnose_returns_filtered_output_with_disclaimer(self, mock_factory):
        mock_adapter = AsyncMock()
        # AI returns text containing a forbidden word "治愈"
        mock_adapter.generate.return_value = "建议使用枸杞治愈身体不适"
        mock_factory.create.return_value = mock_adapter

        mock_db, template = _mock_db_with_prompt("健康顾问", "你是健康顾问", version=2)
        user_id = uuid.uuid4()
        input_data = {"年龄": "30", "性别": "男", "不适描述": "头痛"}

        result = await diagnose(mock_db, user_id, input_data)

        # Compliance filter should replace "治愈" → "调理方向"
        assert "治愈" not in result
        assert "调理方向" in result
        # Disclaimer must be appended
        assert DISCLAIMER in result
        # AI adapter was called
        mock_adapter.generate.assert_awaited_once()
        # Log entry was persisted
        mock_db.add.assert_called_once()
        mock_db.flush.assert_awaited_once()


# ---------------------------------------------------------------------------
# 2. diagnose — AI failure
# ---------------------------------------------------------------------------


class TestDiagnoseFailure:
    """Validates: Requirement 4.7"""

    @pytest.mark.asyncio
    @patch("app.services.ai_service.AIAdapterFactory")
    async def test_diagnose_raises_value_error_on_ai_failure(self, mock_factory):
        mock_adapter = AsyncMock()
        mock_adapter.generate.side_effect = RuntimeError("API timeout")
        mock_factory.create.return_value = mock_adapter

        mock_db, _ = _mock_db_with_prompt("健康顾问", "你是健康顾问")
        user_id = uuid.uuid4()

        with pytest.raises(ValueError, match="AI 服务暂时不可用"):
            await diagnose(mock_db, user_id, {"症状": "头痛"})


# ---------------------------------------------------------------------------
# 3. diagnose — no prompt template
# ---------------------------------------------------------------------------


class TestDiagnoseNoPrompt:
    """Validates: Requirement 4.2 (graceful handling when no template exists)"""

    @pytest.mark.asyncio
    @patch("app.services.ai_service.AIAdapterFactory")
    async def test_diagnose_works_with_no_prompt_template(self, mock_factory):
        mock_adapter = AsyncMock()
        mock_adapter.generate.return_value = "一些健康建议"
        mock_factory.create.return_value = mock_adapter

        mock_db = _mock_db_no_prompt()
        user_id = uuid.uuid4()

        result = await diagnose(mock_db, user_id, {"症状": "疲劳"})

        assert "一些健康建议" in result
        assert DISCLAIMER in result
        mock_db.add.assert_called_once()


# ---------------------------------------------------------------------------
# 4. get_pairing_suggestion — success path
# ---------------------------------------------------------------------------


class TestPairingSuggestionSuccess:
    """Validates: Requirements 4.2, 4.3"""

    @pytest.mark.asyncio
    @patch("app.services.ai_service.AIAdapterFactory")
    async def test_pairing_returns_filtered_output_with_disclaimer(self, mock_factory):
        mock_adapter = AsyncMock()
        mock_adapter.generate.return_value = "枸杞搭配红枣可治疗气虚"
        mock_factory.create.return_value = mock_adapter

        mock_db, _ = _mock_db_with_prompt("科普助手", "你是科普助手")

        result = await get_pairing_suggestion(mock_db, ["枸杞", "红枣"])

        # Compliance filter: "治疗" → "健康参考" in the AI output portion
        ai_output_part = result.split(f"\n\n{DISCLAIMER}")[0]
        assert "治疗" not in ai_output_part
        assert "健康参考" in ai_output_part
        assert DISCLAIMER in result
        mock_adapter.generate.assert_awaited_once()


# ---------------------------------------------------------------------------
# 5. get_pairing_suggestion — AI failure
# ---------------------------------------------------------------------------


class TestPairingSuggestionFailure:
    """Validates: Requirement 4.7"""

    @pytest.mark.asyncio
    @patch("app.services.ai_service.AIAdapterFactory")
    async def test_pairing_raises_value_error_on_ai_failure(self, mock_factory):
        mock_adapter = AsyncMock()
        mock_adapter.generate.side_effect = ConnectionError("network error")
        mock_factory.create.return_value = mock_adapter

        mock_db, _ = _mock_db_with_prompt("科普助手", "你是科普助手")

        with pytest.raises(ValueError, match="AI 服务暂时不可用"):
            await get_pairing_suggestion(mock_db, ["当归"])


# ---------------------------------------------------------------------------
# 6. generate_herb_content — success path (no compliance filter)
# ---------------------------------------------------------------------------


class TestGenerateHerbContentSuccess:
    """Validates: Requirement 4.2"""

    @pytest.mark.asyncio
    @patch("app.services.ai_service.AIAdapterFactory")
    async def test_generate_returns_raw_output(self, mock_factory):
        raw_text = "枸杞，又名枸杞子，可治愈多种不适"
        mock_adapter = AsyncMock()
        mock_adapter.generate.return_value = raw_text
        mock_factory.create.return_value = mock_adapter

        mock_db, _ = _mock_db_with_prompt("科普内容生成", "生成科普内容")

        result = await generate_herb_content(mock_db, "枸杞")

        # Raw output returned — no compliance filter, no disclaimer
        assert result == raw_text
        assert DISCLAIMER not in result
        mock_adapter.generate.assert_awaited_once()


# ---------------------------------------------------------------------------
# 7. generate_herb_content — AI failure
# ---------------------------------------------------------------------------


class TestGenerateHerbContentFailure:
    """Validates: Requirement 4.7"""

    @pytest.mark.asyncio
    @patch("app.services.ai_service.AIAdapterFactory")
    async def test_generate_raises_value_error_on_ai_failure(self, mock_factory):
        mock_adapter = AsyncMock()
        mock_adapter.generate.side_effect = Exception("model unavailable")
        mock_factory.create.return_value = mock_adapter

        mock_db, _ = _mock_db_with_prompt("科普内容生成", "生成科普内容")

        with pytest.raises(ValueError, match="AI 服务暂时不可用"):
            await generate_herb_content(mock_db, "当归")


# ---------------------------------------------------------------------------
# 8. get_active_prompt — returns latest active template
# ---------------------------------------------------------------------------


class TestGetActivePrompt:
    @pytest.mark.asyncio
    async def test_returns_latest_active_template(self):
        template = MagicMock()
        template.type = "健康顾问"
        template.version = 3
        template.is_active = True
        template.content = "最新版本的 prompt"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = template

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        result = await get_active_prompt(mock_db, "健康顾问")

        assert result is template
        assert result.version == 3
        mock_db.execute.assert_awaited_once()


# ---------------------------------------------------------------------------
# 9. get_active_prompt — returns None when no template exists
# ---------------------------------------------------------------------------


class TestGetActivePromptNone:
    @pytest.mark.asyncio
    async def test_returns_none_when_no_template(self):
        mock_db = _mock_db_no_prompt()

        result = await get_active_prompt(mock_db, "不存在的类型")

        assert result is None

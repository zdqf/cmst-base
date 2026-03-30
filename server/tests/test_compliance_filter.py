"""Unit tests for ComplianceFilter (Task 4.3).

Validates: Requirements 15.2, 15.4
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.compliance.filter import ComplianceFilter, DEFAULT_WORD_MAP


# ---------------------------------------------------------------------------
# 1. Each default forbidden word is replaced correctly
# ---------------------------------------------------------------------------


class TestDefaultWordReplacement:
    @pytest.mark.parametrize(
        "forbidden,replacement",
        list(DEFAULT_WORD_MAP.items()),
        ids=list(DEFAULT_WORD_MAP.keys()),
    )
    def test_each_default_word_replaced(self, forbidden: str, replacement: str):
        cf = ComplianceFilter()
        result = cf.filter(f"这个产品可以{forbidden}")
        assert forbidden not in result
        assert replacement in result


# ---------------------------------------------------------------------------
# 2. Text without forbidden words remains unchanged
# ---------------------------------------------------------------------------


class TestCleanTextUnchanged:
    def test_clean_text_unchanged(self):
        cf = ComplianceFilter()
        text = "今天天气不错，适合喝茶"
        assert cf.filter(text) == text

    def test_plain_ascii_unchanged(self):
        cf = ComplianceFilter()
        text = "hello world 123"
        assert cf.filter(text) == text


# ---------------------------------------------------------------------------
# 3 & 4. Empty / None handling
# ---------------------------------------------------------------------------


class TestEmptyAndNoneHandling:
    def test_empty_string_returns_empty(self):
        cf = ComplianceFilter()
        assert cf.filter("") == ""

    def test_none_returns_empty(self):
        cf = ComplianceFilter()
        assert cf.filter(None) == ""


# ---------------------------------------------------------------------------
# 5. Multiple forbidden words in one text are all replaced
# ---------------------------------------------------------------------------


class TestMultipleForbiddenWords:
    def test_multiple_words_all_replaced(self):
        cf = ComplianceFilter()
        text = "本品可治愈感冒，治疗咳嗽，根治鼻炎"
        result = cf.filter(text)
        assert "治愈" not in result
        assert "治疗" not in result
        assert "根治" not in result
        assert "调理方向" in result
        assert "健康参考" in result
        assert "调理建议" in result


# ---------------------------------------------------------------------------
# 6. Longer phrases match before shorter ones
# ---------------------------------------------------------------------------


class TestLongerPhrasesPriority:
    def test_longer_phrase_matches_first(self):
        """'疗效承诺' (4 chars) should match before any partial overlap."""
        cf = ComplianceFilter()
        text = "本品有疗效承诺"
        result = cf.filter(text)
        assert "传统用法参考" in result
        assert "疗效承诺" not in result


# ---------------------------------------------------------------------------
# 7 & 8. reload_words merges DB words with defaults / DB overrides defaults
# ---------------------------------------------------------------------------


class TestReloadWords:
    @pytest.mark.asyncio
    async def test_reload_merges_db_with_defaults(self):
        """DB words are merged on top of defaults."""
        db_word = MagicMock()
        db_word.forbidden_word = "神药"
        db_word.replacement = "传统草本"

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [db_word]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        cf = ComplianceFilter()
        await cf.reload_words(mock_db)

        # New DB word is present
        assert cf.word_map["神药"] == "传统草本"
        # Defaults are still present
        for k, v in DEFAULT_WORD_MAP.items():
            assert cf.word_map[k] == v

    @pytest.mark.asyncio
    async def test_db_words_override_defaults(self):
        """DB entry for an existing default key overrides the default."""
        db_word = MagicMock()
        db_word.forbidden_word = "治愈"
        db_word.replacement = "自定义替换"

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [db_word]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        cf = ComplianceFilter()
        await cf.reload_words(mock_db)

        assert cf.word_map["治愈"] == "自定义替换"
        # Other defaults remain
        assert cf.word_map["治疗"] == DEFAULT_WORD_MAP["治疗"]

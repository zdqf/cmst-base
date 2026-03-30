"""Compliance filter — replaces forbidden words with compliant alternatives.

Validates: Requirements 15.2, 15.4
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.compliance_word import ComplianceWord

# Built-in defaults so the filter works without a database connection.
DEFAULT_WORD_MAP: dict[str, str] = {
    "治愈": "调理方向",
    "治疗": "健康参考",
    "疗效承诺": "传统用法参考",
    "根治": "调理建议",
    "药效": "传统功效",
    "处方": "搭配思路",
}


class ComplianceFilter:
    """Replace forbidden words in text with compliant alternatives.

    Can be used standalone (defaults only) or with a database session
    to load additional / overridden words via ``reload_words``.
    """

    def __init__(self) -> None:
        self._word_map: dict[str, str] = dict(DEFAULT_WORD_MAP)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def reload_words(self, db: AsyncSession) -> None:
        """Load all ComplianceWord records from the DB and merge with defaults.

        DB entries take precedence over built-in defaults for the same
        forbidden word.
        """
        result = await db.execute(select(ComplianceWord))
        db_words = result.scalars().all()

        merged = dict(DEFAULT_WORD_MAP)
        for word in db_words:
            if word.replacement:
                merged[word.forbidden_word] = word.replacement
        self._word_map = merged

    def filter(self, text: str | None) -> str:
        """Return *text* with all forbidden words replaced.

        Returns an empty string for ``None`` or empty input.
        """
        if not text:
            return ""

        # Sort by length descending so longer phrases match first
        # (e.g. "疗效承诺" before "疗效").
        for forbidden in sorted(self._word_map, key=len, reverse=True):
            text = text.replace(forbidden, self._word_map[forbidden])
        return text

    @property
    def word_map(self) -> dict[str, str]:
        """Read-only view of the current word map (useful for testing)."""
        return dict(self._word_map)

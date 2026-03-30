"""Property-based tests for ComplianceFilter — idempotency property.

**Validates: Requirements 15.2, 15.4**

Property 1 (Idempotency): Filtering already-filtered text produces the same result.
    filter(filter(text)) == filter(text)
"""

from hypothesis import given, settings
import hypothesis.strategies as st

from app.compliance.filter import ComplianceFilter, DEFAULT_WORD_MAP


class TestFilterIdempotency:
    """Property 1: filter(filter(text)) == filter(text) for all text."""

    @given(text=st.text())
    @settings(max_examples=200)
    def test_idempotent_on_arbitrary_text(self, text: str) -> None:
        """**Validates: Requirements 15.2, 15.4**

        For any arbitrary text, applying the compliance filter twice
        should yield the same result as applying it once.
        """
        cf = ComplianceFilter()
        filtered_once = cf.filter(text)
        filtered_twice = cf.filter(filtered_once)
        assert filtered_once == filtered_twice

    @given(
        prefix=st.text(max_size=30),
        forbidden=st.sampled_from(list(DEFAULT_WORD_MAP.keys())),
        suffix=st.text(max_size=30),
    )
    @settings(max_examples=200)
    def test_idempotent_with_forbidden_words(
        self, prefix: str, forbidden: str, suffix: str
    ) -> None:
        """**Validates: Requirements 15.2, 15.4**

        Text that contains a known forbidden word mixed with random
        surrounding text should still be idempotent after filtering.
        """
        text = prefix + forbidden + suffix
        cf = ComplianceFilter()
        filtered_once = cf.filter(text)
        filtered_twice = cf.filter(filtered_once)
        assert filtered_once == filtered_twice

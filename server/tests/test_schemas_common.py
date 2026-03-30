"""Tests for schemas/common.py — ApiResponse, PaginationParams, PaginatedResponse."""

import pytest
from pydantic import ValidationError

from app.schemas.common import ApiResponse, PaginatedResponse, PaginationParams


# --- ApiResponse ---


class TestApiResponse:
    def test_default_success(self):
        resp = ApiResponse()
        assert resp.code == 0
        assert resp.message == "success"
        assert resp.data is None

    def test_with_data(self):
        resp = ApiResponse(data={"id": 1, "name": "test"})
        assert resp.code == 0
        assert resp.data == {"id": 1, "name": "test"}

    def test_error_response(self):
        resp = ApiResponse(code=404, message="未找到", data=None)
        assert resp.code == 404
        assert resp.message == "未找到"

    def test_serialization_roundtrip(self):
        original = ApiResponse(code=0, message="ok", data={"key": "value"})
        json_str = original.model_dump_json()
        restored = ApiResponse.model_validate_json(json_str)
        assert original == restored


# --- PaginationParams ---


class TestPaginationParams:
    def test_defaults(self):
        params = PaginationParams()
        assert params.page == 1
        assert params.page_size == 10

    def test_custom_values(self):
        params = PaginationParams(page=3, page_size=20)
        assert params.page == 3
        assert params.page_size == 20

    def test_page_size_max_20(self):
        with pytest.raises(ValidationError):
            PaginationParams(page_size=21)

    def test_page_min_1(self):
        with pytest.raises(ValidationError):
            PaginationParams(page=0)

    def test_page_size_min_1(self):
        with pytest.raises(ValidationError):
            PaginationParams(page_size=0)


# --- PaginatedResponse ---


class TestPaginatedResponse:
    def test_create_helper(self):
        resp = PaginatedResponse.create(
            items=["a", "b", "c"], total=10, page=1, page_size=3
        )
        assert resp.items == ["a", "b", "c"]
        assert resp.total == 10
        assert resp.page == 1
        assert resp.page_size == 3
        assert resp.total_pages == 4  # ceil(10/3)

    def test_create_exact_division(self):
        resp = PaginatedResponse.create(
            items=[1, 2], total=6, page=3, page_size=2
        )
        assert resp.total_pages == 3

    def test_create_empty(self):
        resp = PaginatedResponse.create(
            items=[], total=0, page=1, page_size=10
        )
        assert resp.items == []
        assert resp.total == 0
        assert resp.total_pages == 0

    def test_serialization_roundtrip(self):
        original = PaginatedResponse.create(
            items=[{"id": 1}], total=1, page=1, page_size=10
        )
        json_str = original.model_dump_json()
        restored = PaginatedResponse.model_validate_json(json_str)
        assert original == restored

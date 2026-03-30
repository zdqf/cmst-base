"""Tests for Pydantic validation error responses (Task 23.2).

Validates: Requirements 17.5
- Invalid request data returns 422 status code with detailed field validation errors.
"""

import uuid
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.middleware.auth import get_current_user


def _mock_user():
    user = MagicMock()
    user.id = uuid.uuid4()
    user.status = "active"
    return user


@pytest.fixture(autouse=True)
def override_auth():
    """Override auth dependency for all tests so authenticated endpoints
    reach the body-validation stage instead of returning 401."""
    app.dependency_overrides[get_current_user] = lambda: _mock_user()
    yield
    app.dependency_overrides.clear()


client = TestClient(app)


# ---------------------------------------------------------------------------
# Auth endpoints — no authentication required
# ---------------------------------------------------------------------------


class TestRegisterValidation:
    """POST /api/v1/auth/register — requires phone, code."""

    def test_empty_body(self):
        resp = client.post("/api/v1/auth/register", json={})
        assert resp.status_code == 422
        detail = resp.json()["detail"]
        field_names = {e["loc"][-1] for e in detail}
        assert "phone" in field_names
        assert "code" in field_names

    def test_missing_phone(self):
        resp = client.post("/api/v1/auth/register", json={"code": "123456"})
        assert resp.status_code == 422
        detail = resp.json()["detail"]
        field_names = {e["loc"][-1] for e in detail}
        assert "phone" in field_names

    def test_missing_code(self):
        resp = client.post("/api/v1/auth/register", json={"phone": "13800138000"})
        assert resp.status_code == 422
        detail = resp.json()["detail"]
        field_names = {e["loc"][-1] for e in detail}
        assert "code" in field_names

    def test_invalid_phone_format(self):
        resp = client.post("/api/v1/auth/register", json={"phone": "abc", "code": "123456"})
        assert resp.status_code == 422

    def test_wrong_type_phone(self):
        resp = client.post("/api/v1/auth/register", json={"phone": 12345, "code": "123456"})
        assert resp.status_code == 422


class TestLoginValidation:
    """POST /api/v1/auth/login — requires phone, code."""

    def test_empty_body(self):
        resp = client.post("/api/v1/auth/login", json={})
        assert resp.status_code == 422
        detail = resp.json()["detail"]
        field_names = {e["loc"][-1] for e in detail}
        assert "phone" in field_names
        assert "code" in field_names

    def test_missing_phone(self):
        resp = client.post("/api/v1/auth/login", json={"code": "123456"})
        assert resp.status_code == 422

    def test_invalid_phone_format(self):
        resp = client.post("/api/v1/auth/login", json={"phone": "not-a-phone", "code": "123456"})
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# AI endpoints
# ---------------------------------------------------------------------------


class TestDiagnosisValidation:
    """POST /api/v1/ai/diagnosis — requires age, gender, symptoms."""

    def test_empty_body(self):
        resp = client.post("/api/v1/ai/diagnosis", json={})
        assert resp.status_code == 422
        detail = resp.json()["detail"]
        field_names = {e["loc"][-1] for e in detail}
        assert "age" in field_names
        assert "gender" in field_names
        assert "symptoms" in field_names

    def test_wrong_type_age(self):
        resp = client.post(
            "/api/v1/ai/diagnosis",
            json={"age": "not-a-number", "gender": "男", "symptoms": "头痛"},
        )
        assert resp.status_code == 422
        detail = resp.json()["detail"]
        field_names = {e["loc"][-1] for e in detail}
        assert "age" in field_names

    def test_negative_age(self):
        resp = client.post(
            "/api/v1/ai/diagnosis",
            json={"age": -1, "gender": "男", "symptoms": "头痛"},
        )
        assert resp.status_code == 422

    def test_age_exceeds_max(self):
        resp = client.post(
            "/api/v1/ai/diagnosis",
            json={"age": 300, "gender": "男", "symptoms": "头痛"},
        )
        assert resp.status_code == 422

    def test_empty_symptoms(self):
        resp = client.post(
            "/api/v1/ai/diagnosis",
            json={"age": 30, "gender": "男", "symptoms": ""},
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Consultation endpoint
# ---------------------------------------------------------------------------


class TestConsultationValidation:
    """POST /api/v1/consultations — requires name, contact, subject, description."""

    def test_empty_body(self):
        resp = client.post("/api/v1/consultations", json={})
        assert resp.status_code == 422
        detail = resp.json()["detail"]
        field_names = {e["loc"][-1] for e in detail}
        assert "name" in field_names
        assert "contact" in field_names
        assert "subject" in field_names
        assert "description" in field_names

    def test_empty_string_fields(self):
        resp = client.post(
            "/api/v1/consultations",
            json={"name": "", "contact": "", "subject": "", "description": ""},
        )
        assert resp.status_code == 422

    def test_missing_description(self):
        resp = client.post(
            "/api/v1/consultations",
            json={"name": "张三", "contact": "13800138000", "subject": "咨询"},
        )
        assert resp.status_code == 422
        detail = resp.json()["detail"]
        field_names = {e["loc"][-1] for e in detail}
        assert "description" in field_names


# ---------------------------------------------------------------------------
# Cart endpoint
# ---------------------------------------------------------------------------


class TestCartValidation:
    """POST /api/v1/cart — requires product_id, quantity."""

    def test_empty_body(self):
        resp = client.post("/api/v1/cart", json={})
        assert resp.status_code == 422
        detail = resp.json()["detail"]
        field_names = {e["loc"][-1] for e in detail}
        assert "product_id" in field_names

    def test_invalid_product_id(self):
        resp = client.post("/api/v1/cart", json={"product_id": "not-a-uuid", "quantity": 1})
        assert resp.status_code == 422

    def test_negative_quantity(self):
        resp = client.post(
            "/api/v1/cart",
            json={
                "product_id": "00000000-0000-0000-0000-000000000001",
                "quantity": -1,
            },
        )
        assert resp.status_code == 422

    def test_zero_quantity(self):
        resp = client.post(
            "/api/v1/cart",
            json={
                "product_id": "00000000-0000-0000-0000-000000000001",
                "quantity": 0,
            },
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Orders endpoint
# ---------------------------------------------------------------------------


class TestOrderValidation:
    """POST /api/v1/orders — requires items array."""

    def test_empty_body(self):
        resp = client.post("/api/v1/orders", json={})
        assert resp.status_code == 422
        detail = resp.json()["detail"]
        field_names = {e["loc"][-1] for e in detail}
        assert "items" in field_names

    def test_empty_items_array(self):
        resp = client.post("/api/v1/orders", json={"items": []})
        assert resp.status_code == 422

    def test_invalid_item_structure(self):
        resp = client.post("/api/v1/orders", json={"items": [{"bad": "data"}]})
        assert resp.status_code == 422

    def test_wrong_type_items(self):
        resp = client.post("/api/v1/orders", json={"items": "not-an-array"})
        assert resp.status_code == 422

    def test_item_negative_quantity(self):
        resp = client.post(
            "/api/v1/orders",
            json={
                "items": [
                    {
                        "product_id": "00000000-0000-0000-0000-000000000001",
                        "quantity": -1,
                    }
                ]
            },
        )
        assert resp.status_code == 422

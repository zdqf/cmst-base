"""Unit tests for consultation API — schemas, service, and router endpoint (Task 7.2).

Validates Requirements:
- 6.1: Form-based consultation submission (name, contact, subject, description)
- 6.2: Store consultation record and return success confirmation
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.consultation import (
    ConsultationCreateRequest,
    ConsultationResponse,
    ContactInfo,
)
from app.services.consultation_service import WECHAT_CONTACT


# ---------------------------------------------------------------------------
# 1. ConsultationCreateRequest schema validation
# ---------------------------------------------------------------------------


class TestConsultationCreateRequest:
    """Validates: Requirement 6.1 — form fields: name, contact, subject, description."""

    def test_valid_request(self):
        req = ConsultationCreateRequest(
            name="张三",
            contact="13800138000",
            subject="中药调理咨询",
            description="想了解枸杞的日常调理方向",
        )
        assert req.name == "张三"
        assert req.contact == "13800138000"
        assert req.subject == "中药调理咨询"
        assert req.description == "想了解枸杞的日常调理方向"

    def test_missing_name_raises(self):
        with pytest.raises(Exception):
            ConsultationCreateRequest(
                contact="13800138000",
                subject="咨询",
                description="描述",
            )

    def test_missing_contact_raises(self):
        with pytest.raises(Exception):
            ConsultationCreateRequest(
                name="张三",
                subject="咨询",
                description="描述",
            )

    def test_missing_subject_raises(self):
        with pytest.raises(Exception):
            ConsultationCreateRequest(
                name="张三",
                contact="13800138000",
                description="描述",
            )

    def test_missing_description_raises(self):
        with pytest.raises(Exception):
            ConsultationCreateRequest(
                name="张三",
                contact="13800138000",
                subject="咨询",
            )

    def test_empty_name_raises(self):
        with pytest.raises(Exception):
            ConsultationCreateRequest(
                name="",
                contact="13800138000",
                subject="咨询",
                description="描述",
            )


# ---------------------------------------------------------------------------
# 2. ConsultationResponse schema validation
# ---------------------------------------------------------------------------


class TestConsultationResponse:
    """Validates: Requirement 6.2 — consultation record response."""

    def test_valid_response(self):
        now = datetime.now(timezone.utc)
        resp = ConsultationResponse(
            id=uuid.uuid4(),
            name="张三",
            contact="13800138000",
            subject="中药调理咨询",
            description="详细描述",
            status="pending",
            created_at=now,
        )
        assert resp.name == "张三"
        assert resp.status == "pending"

    def test_from_attributes(self):
        obj = MagicMock()
        obj.id = uuid.uuid4()
        obj.name = "李四"
        obj.contact = "13900139000"
        obj.subject = "搭配咨询"
        obj.description = "想了解搭配方向"
        obj.status = "pending"
        obj.created_at = datetime.now(timezone.utc)
        resp = ConsultationResponse.model_validate(obj)
        assert resp.name == "李四"
        assert resp.subject == "搭配咨询"


# ---------------------------------------------------------------------------
# 3. ContactInfo schema
# ---------------------------------------------------------------------------


class TestContactInfo:
    """Validates: Requirement 6.3 — WeChat contact info."""

    def test_valid_contact_info(self):
        info = ContactInfo(
            wechat_id="caomushentang",
            qr_code_url="https://example.com/qrcode.png",
        )
        assert info.wechat_id == "caomushentang"
        assert info.qr_code_url == "https://example.com/qrcode.png"

    def test_wechat_contact_constant(self):
        assert WECHAT_CONTACT.wechat_id == "caomushentang"
        assert "qrcode" in WECHAT_CONTACT.qr_code_url


# ---------------------------------------------------------------------------
# 4. create_consultation service — mock DB, verify consultation created
# ---------------------------------------------------------------------------


def _mock_consultation(user_id, **overrides):
    """Create a mock Consultation ORM object."""
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=uuid.uuid4(),
        user_id=user_id,
        name="张三",
        contact="13800138000",
        subject="中药调理咨询",
        description="详细描述",
        status="pending",
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    obj = MagicMock()
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


class TestCreateConsultationService:
    """Validates: Requirement 6.2 — store consultation record."""

    @pytest.mark.asyncio
    async def test_creates_consultation(self):
        from app.services.consultation_service import create_consultation

        user_id = uuid.uuid4()
        data = ConsultationCreateRequest(
            name="张三",
            contact="13800138000",
            subject="中药调理咨询",
            description="想了解枸杞的日常调理方向",
        )

        mock_db = AsyncMock()
        # db.add is synchronous — use a plain MagicMock to capture the object
        added_objects = []
        mock_db.add = MagicMock(side_effect=lambda obj: added_objects.append(obj))

        result = await create_consultation(mock_db, user_id, data)

        mock_db.add.assert_called_once()
        mock_db.flush.assert_awaited_once()
        mock_db.refresh.assert_awaited_once()

        consultation = added_objects[0]
        assert consultation.name == "张三"
        assert consultation.contact == "13800138000"
        assert consultation.subject == "中药调理咨询"
        assert consultation.user_id == user_id


# ---------------------------------------------------------------------------
# 5. POST /api/v1/consultations endpoint tests
# ---------------------------------------------------------------------------


def _mock_user():
    user = MagicMock()
    user.id = uuid.uuid4()
    user.status = "active"
    return user


class TestSubmitConsultationEndpoint:
    """Validates: Requirements 6.1, 6.2, 6.3"""

    def test_submit_success_returns_consultation_and_contact(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.database import get_db
        from app.middleware.auth import get_current_user

        user = _mock_user()
        consultation = _mock_consultation(user.id)

        with patch(
            "app.routers.consultations.create_consultation",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = consultation

            app.dependency_overrides[get_db] = lambda: AsyncMock()
            app.dependency_overrides[get_current_user] = lambda: user
            try:
                client = TestClient(app)
                response = client.post(
                    "/api/v1/consultations",
                    json={
                        "name": "张三",
                        "contact": "13800138000",
                        "subject": "中药调理咨询",
                        "description": "想了解枸杞的日常调理方向",
                    },
                )
            finally:
                app.dependency_overrides.clear()

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["message"] == "success"

        # Verify consultation data is present
        assert "consultation" in body["data"]
        assert body["data"]["consultation"]["name"] == "张三"
        assert body["data"]["consultation"]["status"] == "pending"

        # Verify WeChat contact info is present (Requirement 6.3)
        assert "contact" in body["data"]
        assert body["data"]["contact"]["wechat_id"] == "caomushentang"
        assert "qr_code_url" in body["data"]["contact"]

    def test_submit_missing_fields_returns_422(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.middleware.auth import get_current_user

        user = _mock_user()
        app.dependency_overrides[get_current_user] = lambda: user
        try:
            client = TestClient(app)
            # Missing required fields (only name provided)
            response = client.post(
                "/api/v1/consultations",
                json={"name": "张三"},
            )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 422

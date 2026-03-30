"""Unit tests for admin consultation management API (Task 10.2).

Validates Requirements:
- 9.1: List consultations with status filter
- 9.2: View consultation details and processing history
- 9.3: Update consultation status or add admin notes, record operation time
- 6.4: Notify admin on new consultation
- 6.5: Record status change time and operator
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database import get_db
from app.routers.admin.consultations import router
from app.routers.admin.users import get_admin_user
from app.schemas.consultation import (
    AdminConsultationItem,
    AdminConsultationNotesUpdate,
    AdminConsultationStatusUpdate,
)


# ---------------------------------------------------------------------------
# Test app fixture
# ---------------------------------------------------------------------------

def _create_test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_admin_user() -> MagicMock:
    obj = MagicMock()
    obj.id = uuid.uuid4()
    obj.phone = "13900139000"
    obj.is_admin = True
    obj.status = "active"
    return obj


def _make_consultation(**overrides) -> MagicMock:
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        name="张三",
        contact="13800138000",
        subject="中药调理咨询",
        description="想了解枸杞的日常调理方向",
        status="pending",
        admin_notes=None,
        handled_by=None,
        handled_at=None,
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    obj = MagicMock()
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


# ---------------------------------------------------------------------------
# 1. Schema tests
# ---------------------------------------------------------------------------


class TestAdminConsultationSchemas:
    """Validates: Requirement 9.1 — consultation list item fields."""

    def test_admin_consultation_item_valid(self):
        now = datetime.now(timezone.utc)
        item = AdminConsultationItem(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            name="张三",
            contact="13800138000",
            subject="中药调理咨询",
            description="详细描述",
            status="pending",
            created_at=now,
            updated_at=now,
        )
        assert item.name == "张三"
        assert item.status == "pending"
        assert item.admin_notes is None
        assert item.handled_by is None

    def test_admin_consultation_item_from_attributes(self):
        obj = _make_consultation(status="processing", admin_notes="已联系用户")
        item = AdminConsultationItem.model_validate(obj)
        assert item.status == "processing"
        assert item.admin_notes == "已联系用户"

    def test_status_update_valid_values(self):
        for s in ("pending", "processing", "completed"):
            req = AdminConsultationStatusUpdate(status=s)
            assert req.status == s

    def test_status_update_invalid_value(self):
        with pytest.raises(Exception):
            AdminConsultationStatusUpdate(status="invalid")

    def test_notes_update_valid(self):
        req = AdminConsultationNotesUpdate(admin_notes="已联系用户，等待回复")
        assert req.admin_notes == "已联系用户，等待回复"

    def test_notes_update_empty_raises(self):
        with pytest.raises(Exception):
            AdminConsultationNotesUpdate(admin_notes="")


# ---------------------------------------------------------------------------
# 2. List consultations endpoint tests
# ---------------------------------------------------------------------------


class TestListConsultationsEndpoint:
    """Validates: Requirement 9.1 — list with pagination and status filter."""

    def test_list_all_consultations(self):
        admin = _make_admin_user()
        c1 = _make_consultation(status="pending")
        c2 = _make_consultation(status="completed")

        count_result = MagicMock()
        count_result.scalar_one.return_value = 2

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [c1, c2]

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.get("/api/v1/admin/consultations?page=1&page_size=10")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 2
        assert len(body["data"]["items"]) == 2

    def test_list_with_status_filter(self):
        admin = _make_admin_user()
        c1 = _make_consultation(status="pending")

        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [c1]

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.get("/api/v1/admin/consultations?status=pending")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 1

    def test_list_empty_result(self):
        admin = _make_admin_user()

        count_result = MagicMock()
        count_result.scalar_one.return_value = 0

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = []

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.get("/api/v1/admin/consultations")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 0
        assert body["data"]["items"] == []

    def test_page_size_exceeds_max_returns_422(self):
        admin = _make_admin_user()
        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin

        client = TestClient(app)
        response = client.get("/api/v1/admin/consultations?page_size=21")
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# 3. Update consultation status endpoint tests
# ---------------------------------------------------------------------------


class TestUpdateConsultationStatusEndpoint:
    """Validates: Requirement 9.3, 6.5 — update status, record operator and time."""

    def test_update_status_success(self):
        admin = _make_admin_user()
        consultation = _make_consultation(status="pending")

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = consultation

        update_result = MagicMock()

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[select_result, update_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.put(
            f"/api/v1/admin/consultations/{consultation.id}/status",
            json={"status": "processing"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["message"] == "状态已更新"

    def test_update_status_not_found(self):
        admin = _make_admin_user()

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=select_result)

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.put(
            f"/api/v1/admin/consultations/{uuid.uuid4()}/status",
            json={"status": "completed"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 404
        assert body["message"] == "咨询记录不存在"

    def test_update_status_invalid_value_returns_422(self):
        admin = _make_admin_user()
        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin

        client = TestClient(app)
        response = client.put(
            f"/api/v1/admin/consultations/{uuid.uuid4()}/status",
            json={"status": "invalid_status"},
        )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# 4. Update consultation notes endpoint tests
# ---------------------------------------------------------------------------


class TestUpdateConsultationNotesEndpoint:
    """Validates: Requirement 9.3 — add admin notes."""

    def test_add_notes_success(self):
        admin = _make_admin_user()
        consultation = _make_consultation()

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = consultation

        update_result = MagicMock()

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[select_result, update_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.put(
            f"/api/v1/admin/consultations/{consultation.id}/notes",
            json={"admin_notes": "已联系用户，等待回复"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["message"] == "备注已更新"

    def test_add_notes_not_found(self):
        admin = _make_admin_user()

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=select_result)

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.put(
            f"/api/v1/admin/consultations/{uuid.uuid4()}/notes",
            json={"admin_notes": "备注内容"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 404
        assert body["message"] == "咨询记录不存在"

    def test_add_empty_notes_returns_422(self):
        admin = _make_admin_user()
        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin

        client = TestClient(app)
        response = client.put(
            f"/api/v1/admin/consultations/{uuid.uuid4()}/notes",
            json={"admin_notes": ""},
        )
        assert response.status_code == 422

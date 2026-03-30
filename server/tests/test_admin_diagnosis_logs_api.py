"""Unit tests for admin diagnosis log management API (Task 10.3).

Validates Requirements:
- 10.1: Paginated list of AI diagnosis logs with user info, time, summaries
- 10.2: View full diagnosis log detail (complete input_data and ai_output)
- 10.3: Filter diagnosis logs by time range and user
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database import get_db
from app.routers.admin.diagnosis_logs import router
from app.routers.admin.users import get_admin_user
from app.schemas.ai import AdminDiagnosisLogDetail, AdminDiagnosisLogItem


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
    return obj


def _make_log_obj(**overrides) -> MagicMock:
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        input_data={"age": 30, "gender": "male", "symptoms": "头痛"},
        ai_output="建议多休息，注意饮食调理。",
        prompt_version="v1.0",
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


class TestAdminDiagnosisLogSchemas:
    """Validates: Requirement 10.1, 10.2 — schema field validation."""

    def test_item_schema_valid(self):
        now = datetime.now(timezone.utc)
        item = AdminDiagnosisLogItem(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            input_data={"age": 25, "symptoms": "失眠"},
            ai_output="建议调理作息。",
            prompt_version="v1.0",
            created_at=now,
            updated_at=now,
        )
        assert item.ai_output == "建议调理作息。"
        assert item.input_data["age"] == 25

    def test_item_schema_optional_prompt_version(self):
        now = datetime.now(timezone.utc)
        item = AdminDiagnosisLogItem(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            input_data={},
            ai_output="test",
            created_at=now,
            updated_at=now,
        )
        assert item.prompt_version is None

    def test_detail_schema_valid(self):
        now = datetime.now(timezone.utc)
        detail = AdminDiagnosisLogDetail(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            input_data={"age": 40, "gender": "female", "symptoms": "腰酸"},
            ai_output="建议适当运动，注意保暖。",
            prompt_version="v2.0",
            created_at=now,
            updated_at=now,
        )
        assert detail.ai_output == "建议适当运动，注意保暖。"


# ---------------------------------------------------------------------------
# 2. List endpoint tests
# ---------------------------------------------------------------------------


class TestListDiagnosisLogsEndpoint:
    """Validates: Requirement 10.1, 10.3"""

    def test_list_logs_success(self):
        admin = _make_admin_user()
        log1 = _make_log_obj()
        log2 = _make_log_obj()

        count_result = MagicMock()
        count_result.scalar_one.return_value = 2

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [log1, log2]

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        resp = client.get("/api/v1/admin/diagnosis-logs?page=1&page_size=10")

        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 2
        assert len(body["data"]["items"]) == 2

    def test_list_logs_with_user_id_filter(self):
        admin = _make_admin_user()
        uid = uuid.uuid4()
        log1 = _make_log_obj(user_id=uid)

        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [log1]

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        resp = client.get(f"/api/v1/admin/diagnosis-logs?user_id={uid}")

        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 1

    def test_list_logs_with_date_range_filter(self):
        admin = _make_admin_user()
        log1 = _make_log_obj()

        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [log1]

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        resp = client.get(
            "/api/v1/admin/diagnosis-logs?start_date=2024-01-01&end_date=2025-12-31"
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 1

    def test_list_logs_empty_result(self):
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
        resp = client.get("/api/v1/admin/diagnosis-logs")

        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 0
        assert body["data"]["items"] == []

    def test_page_size_exceeds_max_returns_422(self):
        admin = _make_admin_user()
        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin

        client = TestClient(app)
        resp = client.get("/api/v1/admin/diagnosis-logs?page_size=21")
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 3. Detail endpoint tests
# ---------------------------------------------------------------------------


class TestGetDiagnosisLogDetailEndpoint:
    """Validates: Requirement 10.2"""

    def test_get_detail_success(self):
        admin = _make_admin_user()
        log = _make_log_obj()

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = log

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=select_result)

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        resp = client.get(f"/api/v1/admin/diagnosis-logs/{log.id}")

        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["ai_output"] == log.ai_output
        assert body["data"]["input_data"] == log.input_data

    def test_get_detail_not_found(self):
        admin = _make_admin_user()

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=select_result)

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        resp = client.get(f"/api/v1/admin/diagnosis-logs/{uuid.uuid4()}")

        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 404
        assert body["message"] == "问诊记录不存在"

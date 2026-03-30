"""Unit tests for admin compliance word management API (Task 10.8).

Validates Requirements:
- 15.5: Admin can add, modify, and remove forbidden words
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database import get_db
from app.routers.admin.compliance import router
from app.routers.admin.users import get_admin_user
from app.schemas.compliance import (
    ComplianceWordCreate,
    ComplianceWordResponse,
    ComplianceWordUpdate,
)


# ---------------------------------------------------------------------------
# Fixtures & helpers
# ---------------------------------------------------------------------------

def _create_test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


def _make_admin_user() -> MagicMock:
    obj = MagicMock()
    obj.id = uuid.uuid4()
    obj.phone = "13900139000"
    obj.is_admin = True
    obj.status = "active"
    return obj


def _make_compliance_word(**overrides) -> MagicMock:
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=uuid.uuid4(),
        forbidden_word="治愈",
        replacement="调理方向",
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


class TestComplianceSchemas:
    """Validates: Requirement 15.5 — compliance word schema validation."""

    def test_create_valid(self):
        schema = ComplianceWordCreate(forbidden_word="治愈", replacement="调理方向")
        assert schema.forbidden_word == "治愈"
        assert schema.replacement == "调理方向"

    def test_create_without_replacement(self):
        schema = ComplianceWordCreate(forbidden_word="治疗")
        assert schema.forbidden_word == "治疗"
        assert schema.replacement is None

    def test_create_empty_forbidden_word_raises(self):
        with pytest.raises(Exception):
            ComplianceWordCreate(forbidden_word="")

    def test_create_missing_forbidden_word_raises(self):
        with pytest.raises(Exception):
            ComplianceWordCreate(replacement="调理方向")

    def test_update_partial_forbidden_word(self):
        schema = ComplianceWordUpdate(forbidden_word="疗效承诺")
        data = schema.model_dump(exclude_unset=True)
        assert data == {"forbidden_word": "疗效承诺"}

    def test_update_partial_replacement(self):
        schema = ComplianceWordUpdate(replacement="健康参考")
        data = schema.model_dump(exclude_unset=True)
        assert data == {"replacement": "健康参考"}

    def test_response_from_attributes(self):
        now = datetime.now(timezone.utc)
        resp = ComplianceWordResponse(
            id=uuid.uuid4(),
            forbidden_word="治愈",
            replacement="调理方向",
            created_at=now,
            updated_at=now,
        )
        assert resp.forbidden_word == "治愈"


# ---------------------------------------------------------------------------
# 2. List compliance words endpoint tests
# ---------------------------------------------------------------------------


class TestListComplianceWordsEndpoint:
    """Validates: Requirement 15.5 — list forbidden words with pagination."""

    def test_list_success(self):
        admin = _make_admin_user()
        w1 = _make_compliance_word(forbidden_word="治愈")
        w2 = _make_compliance_word(forbidden_word="治疗")

        count_result = MagicMock()
        count_result.scalar_one.return_value = 2

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [w1, w2]

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.get("/api/v1/admin/compliance?page=1&page_size=10")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 2
        assert len(body["data"]["items"]) == 2

    def test_list_empty(self):
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
        response = client.get("/api/v1/admin/compliance")

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
        response = client.get("/api/v1/admin/compliance?page_size=21")
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# 3. Create compliance word endpoint tests
# ---------------------------------------------------------------------------


class TestCreateComplianceWordEndpoint:
    """Validates: Requirement 15.5 — add forbidden words."""

    def test_create_success(self):
        admin = _make_admin_user()
        new_word = _make_compliance_word(forbidden_word="治愈", replacement="调理方向")

        # First execute: check duplicate (returns None)
        dup_result = MagicMock()
        dup_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=dup_result)
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()
        mock_db.refresh = AsyncMock(
            side_effect=lambda w: _apply_word_defaults(w, new_word)
        )

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.post(
            "/api/v1/admin/compliance",
            json={"forbidden_word": "治愈", "replacement": "调理方向"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["message"] == "违规词汇已添加"
        assert body["data"]["forbidden_word"] == "治愈"

    def test_create_duplicate_returns_error(self):
        admin = _make_admin_user()
        existing = _make_compliance_word(forbidden_word="治愈")

        dup_result = MagicMock()
        dup_result.scalar_one_or_none.return_value = existing

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=dup_result)

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.post(
            "/api/v1/admin/compliance",
            json={"forbidden_word": "治愈", "replacement": "调理方向"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 400
        assert body["message"] == "该违规词汇已存在"

    def test_create_missing_forbidden_word_returns_422(self):
        admin = _make_admin_user()
        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin

        client = TestClient(app)
        response = client.post(
            "/api/v1/admin/compliance",
            json={"replacement": "调理方向"},
        )
        assert response.status_code == 422

    def test_create_empty_forbidden_word_returns_422(self):
        admin = _make_admin_user()
        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin

        client = TestClient(app)
        response = client.post(
            "/api/v1/admin/compliance",
            json={"forbidden_word": ""},
        )
        assert response.status_code == 422

    def test_create_without_replacement(self):
        admin = _make_admin_user()
        new_word = _make_compliance_word(forbidden_word="治疗", replacement=None)

        dup_result = MagicMock()
        dup_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=dup_result)
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()
        mock_db.refresh = AsyncMock(
            side_effect=lambda w: _apply_word_defaults(w, new_word)
        )

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.post(
            "/api/v1/admin/compliance",
            json={"forbidden_word": "治疗"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["replacement"] is None


# ---------------------------------------------------------------------------
# 4. Update compliance word endpoint tests
# ---------------------------------------------------------------------------


class TestUpdateComplianceWordEndpoint:
    """Validates: Requirement 15.5 — modify forbidden words."""

    def test_update_success(self):
        admin = _make_admin_user()
        word = _make_compliance_word(forbidden_word="治愈")
        updated = _make_compliance_word(forbidden_word="治愈", replacement="健康参考")

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = word

        update_result = MagicMock()

        refetch_result = MagicMock()
        refetch_result.scalar_one.return_value = updated

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(
            side_effect=[select_result, update_result, refetch_result]
        )
        mock_db.flush = AsyncMock()

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.put(
            f"/api/v1/admin/compliance/{word.id}",
            json={"replacement": "健康参考"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["message"] == "违规词汇已更新"

    def test_update_forbidden_word_duplicate(self):
        admin = _make_admin_user()
        word = _make_compliance_word(forbidden_word="治愈")
        existing_dup = _make_compliance_word(forbidden_word="治疗")

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = word

        dup_result = MagicMock()
        dup_result.scalar_one_or_none.return_value = existing_dup

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[select_result, dup_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.put(
            f"/api/v1/admin/compliance/{word.id}",
            json={"forbidden_word": "治疗"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 400
        assert body["message"] == "该违规词汇已存在"

    def test_update_not_found(self):
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
            f"/api/v1/admin/compliance/{uuid.uuid4()}",
            json={"replacement": "健康参考"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 404
        assert body["message"] == "违规词汇不存在"

    def test_update_no_fields(self):
        admin = _make_admin_user()
        word = _make_compliance_word()

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = word

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=select_result)

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.put(
            f"/api/v1/admin/compliance/{word.id}",
            json={},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["message"] == "无更新内容"


# ---------------------------------------------------------------------------
# 5. Delete compliance word endpoint tests
# ---------------------------------------------------------------------------


class TestDeleteComplianceWordEndpoint:
    """Validates: Requirement 15.5 — remove forbidden words."""

    def test_delete_success(self):
        admin = _make_admin_user()
        word = _make_compliance_word()

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = word

        delete_result = MagicMock()

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[select_result, delete_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.delete(f"/api/v1/admin/compliance/{word.id}")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["message"] == "违规词汇已删除"

    def test_delete_not_found(self):
        admin = _make_admin_user()

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=select_result)

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.delete(f"/api/v1/admin/compliance/{uuid.uuid4()}")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 404
        assert body["message"] == "违规词汇不存在"


# ---------------------------------------------------------------------------
# Helper for mocking db.refresh
# ---------------------------------------------------------------------------

def _apply_word_defaults(target, source):
    """Copy attributes from source mock to target ComplianceWord ORM instance."""
    target.id = source.id
    target.forbidden_word = source.forbidden_word
    target.replacement = source.replacement
    target.created_at = source.created_at
    target.updated_at = source.updated_at

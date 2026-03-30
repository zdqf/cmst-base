"""Unit tests for admin herb content management API (Task 10.4).

Validates Requirements:
- 11.1: Create herb with all standardized fields
- 11.2: Validate all required fields on create
- 11.3: Edit existing herb content
- 11.4: Toggle herb status (active/inactive)
- 11.5: AI-generated herb content draft
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database import get_db
from app.routers.admin.herbs import router
from app.routers.admin.users import get_admin_user
from app.schemas.herb import (
    AdminHerbCreate,
    AdminHerbStatusUpdate,
    AdminHerbUpdate,
    HerbDetail,
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


def _make_herb(**overrides) -> MagicMock:
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=uuid.uuid4(),
        name="枸杞",
        category="补气",
        origin_and_form="茄科植物枸杞的干燥成熟果实",
        flavor_meridian="甘，平。归肝、肾经",
        common_pairings="菊花、红枣",
        unsuitable_groups="脾虚便溏者",
        precautions="不宜过量",
        status="active",
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


class TestAdminHerbSchemas:
    """Validates: Requirement 11.1, 11.2 — herb create/update schemas."""

    def test_create_valid(self):
        schema = AdminHerbCreate(name="枸杞", category="补气")
        assert schema.name == "枸杞"
        assert schema.category == "补气"
        assert schema.origin_and_form is None

    def test_create_missing_name_raises(self):
        with pytest.raises(Exception):
            AdminHerbCreate()

    def test_create_empty_name_raises(self):
        with pytest.raises(Exception):
            AdminHerbCreate(name="")

    def test_update_partial(self):
        schema = AdminHerbUpdate(category="清热")
        data = schema.model_dump(exclude_unset=True)
        assert data == {"category": "清热"}

    def test_status_update_active(self):
        schema = AdminHerbStatusUpdate(status="active")
        assert schema.status == "active"

    def test_status_update_inactive(self):
        schema = AdminHerbStatusUpdate(status="inactive")
        assert schema.status == "inactive"

    def test_status_update_invalid_raises(self):
        with pytest.raises(Exception):
            AdminHerbStatusUpdate(status="deleted")


# ---------------------------------------------------------------------------
# 2. List herbs endpoint tests
# ---------------------------------------------------------------------------


class TestListHerbsEndpoint:
    """Validates: Requirement 11.4 — admin herb list with filters."""

    def test_list_herbs_success(self):
        admin = _make_admin_user()
        h1 = _make_herb(name="枸杞")
        h2 = _make_herb(name="当归", status="inactive")

        count_result = MagicMock()
        count_result.scalar_one.return_value = 2

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [h1, h2]

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.get("/api/v1/admin/herbs?page=1&page_size=10")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 2
        assert len(body["data"]["items"]) == 2

    def test_list_with_status_filter(self):
        admin = _make_admin_user()
        h1 = _make_herb(name="枸杞", status="active")

        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [h1]

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.get("/api/v1/admin/herbs?status=active")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 1

    def test_page_size_exceeds_max_returns_422(self):
        admin = _make_admin_user()
        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin

        client = TestClient(app)
        response = client.get("/api/v1/admin/herbs?page_size=21")
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# 3. Create herb endpoint tests
# ---------------------------------------------------------------------------


class TestCreateHerbEndpoint:
    """Validates: Requirement 11.1, 11.2 — create herb with validation."""

    def test_create_herb_success(self):
        admin = _make_admin_user()
        new_herb = _make_herb(name="黄芪")

        # First execute: check duplicate name → not found
        dup_result = MagicMock()
        dup_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=dup_result)
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()
        mock_db.refresh = AsyncMock(side_effect=lambda h: _apply_herb_defaults(h, new_herb))

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.post(
            "/api/v1/admin/herbs",
            json={
                "name": "黄芪",
                "category": "补气",
                "origin_and_form": "豆科植物黄芪的干燥根",
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["message"] == "中药创建成功"

    def test_create_herb_duplicate_name(self):
        admin = _make_admin_user()
        existing = _make_herb(name="枸杞")

        dup_result = MagicMock()
        dup_result.scalar_one_or_none.return_value = existing

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=dup_result)

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.post(
            "/api/v1/admin/herbs",
            json={"name": "枸杞"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 400
        assert body["message"] == "该中药名称已存在"

    def test_create_herb_missing_name_returns_422(self):
        admin = _make_admin_user()
        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin

        client = TestClient(app)
        response = client.post("/api/v1/admin/herbs", json={})
        assert response.status_code == 422

    def test_create_herb_empty_name_returns_422(self):
        admin = _make_admin_user()
        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin

        client = TestClient(app)
        response = client.post("/api/v1/admin/herbs", json={"name": ""})
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# 4. Update herb endpoint tests
# ---------------------------------------------------------------------------


class TestUpdateHerbEndpoint:
    """Validates: Requirement 11.3 — edit existing herb content."""

    def test_update_herb_success(self):
        admin = _make_admin_user()
        herb = _make_herb(name="枸杞")
        updated_herb = _make_herb(name="枸杞", category="清热")

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = herb

        update_result = MagicMock()

        refetch_result = MagicMock()
        refetch_result.scalar_one.return_value = updated_herb

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
            f"/api/v1/admin/herbs/{herb.id}",
            json={"category": "清热"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["message"] == "中药信息已更新"

    def test_update_herb_not_found(self):
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
            f"/api/v1/admin/herbs/{uuid.uuid4()}",
            json={"category": "清热"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 404
        assert body["message"] == "中药信息不存在"

    def test_update_herb_duplicate_name(self):
        admin = _make_admin_user()
        herb = _make_herb(name="枸杞")
        existing = _make_herb(name="当归")

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = herb

        dup_result = MagicMock()
        dup_result.scalar_one_or_none.return_value = existing

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[select_result, dup_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.put(
            f"/api/v1/admin/herbs/{herb.id}",
            json={"name": "当归"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 400
        assert body["message"] == "该中药名称已存在"


# ---------------------------------------------------------------------------
# 5. Update herb status endpoint tests
# ---------------------------------------------------------------------------


class TestUpdateHerbStatusEndpoint:
    """Validates: Requirement 11.4 — toggle herb active/inactive."""

    def test_set_inactive(self):
        admin = _make_admin_user()
        herb = _make_herb(status="active")

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = herb

        update_result = MagicMock()

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[select_result, update_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.put(
            f"/api/v1/admin/herbs/{herb.id}/status",
            json={"status": "inactive"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["message"] == "已下架"

    def test_set_active(self):
        admin = _make_admin_user()
        herb = _make_herb(status="inactive")

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = herb

        update_result = MagicMock()

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[select_result, update_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.put(
            f"/api/v1/admin/herbs/{herb.id}/status",
            json={"status": "active"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["message"] == "已上架"

    def test_status_not_found(self):
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
            f"/api/v1/admin/herbs/{uuid.uuid4()}/status",
            json={"status": "active"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 404

    def test_invalid_status_returns_422(self):
        admin = _make_admin_user()
        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin

        client = TestClient(app)
        response = client.put(
            f"/api/v1/admin/herbs/{uuid.uuid4()}/status",
            json={"status": "deleted"},
        )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# 6. Generate content endpoint tests
# ---------------------------------------------------------------------------


class TestGenerateContentEndpoint:
    """Validates: Requirement 11.5 — AI-generated herb content draft."""

    def test_generate_content_success(self):
        admin = _make_admin_user()
        herb = _make_herb(name="枸杞")

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = herb

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=select_result)

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        with patch(
            "app.routers.admin.herbs.generate_herb_content",
            new_callable=AsyncMock,
        ) as mock_gen:
            mock_gen.return_value = "枸杞科普内容初稿..."

            client = TestClient(app)
            response = client.post(
                f"/api/v1/admin/herbs/{herb.id}/generate-content"
            )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["content"] == "枸杞科普内容初稿..."

    def test_generate_content_not_found(self):
        admin = _make_admin_user()

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=select_result)

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.post(
            f"/api/v1/admin/herbs/{uuid.uuid4()}/generate-content"
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 404

    def test_generate_content_ai_failure(self):
        admin = _make_admin_user()
        herb = _make_herb(name="枸杞")

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = herb

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=select_result)

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        with patch(
            "app.routers.admin.herbs.generate_herb_content",
            new_callable=AsyncMock,
        ) as mock_gen:
            mock_gen.side_effect = ValueError("AI 服务暂时不可用，请稍后再试")

            client = TestClient(app)
            response = client.post(
                f"/api/v1/admin/herbs/{herb.id}/generate-content"
            )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 500
        assert "AI 服务暂时不可用" in body["message"]


# ---------------------------------------------------------------------------
# Helper for mocking db.refresh
# ---------------------------------------------------------------------------

def _apply_herb_defaults(target, source):
    """Copy attributes from source mock to target Herb ORM instance for refresh simulation."""
    target.id = source.id
    target.name = source.name if hasattr(source, 'name') else target.name
    target.category = source.category
    target.origin_and_form = source.origin_and_form
    target.flavor_meridian = source.flavor_meridian
    target.common_pairings = source.common_pairings
    target.unsuitable_groups = source.unsuitable_groups
    target.precautions = source.precautions
    target.status = source.status
    target.created_at = source.created_at
    target.updated_at = source.updated_at

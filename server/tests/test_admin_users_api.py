"""Unit tests for admin user management API (Task 10.1).

Validates Requirements:
- 8.1: Paginated user list with phone, registration time, last login
- 8.2: Search users by phone number
- 8.3: Disable user account and invalidate auth tokens
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.models.user import User
from app.routers.admin.users import get_admin_user, router
from app.schemas.admin_user import AdminUserItem
from app.schemas.common import PaginatedResponse


# ---------------------------------------------------------------------------
# Test app fixture — admin router not yet in main.py
# ---------------------------------------------------------------------------

def _create_test_app() -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(router)
    return test_app


test_app = _create_test_app()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_user_obj(**overrides) -> MagicMock:
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=uuid.uuid4(),
        phone="13800138000",
        nickname="测试用户",
        status="active",
        is_admin=False,
        last_login_at=now,
        token_invalidated_at=None,
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    obj = MagicMock()
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


def _make_admin_user() -> MagicMock:
    return _make_user_obj(is_admin=True, phone="13900139000")


# ---------------------------------------------------------------------------
# 1. AdminUserItem schema tests
# ---------------------------------------------------------------------------


class TestAdminUserItemSchema:
    """Validates: Requirement 8.1 — user list item fields."""

    def test_valid_item(self):
        now = datetime.now(timezone.utc)
        item = AdminUserItem(
            id=uuid.uuid4(),
            phone="13800138000",
            nickname="测试用户",
            status="active",
            is_admin=False,
            last_login_at=now,
            created_at=now,
            updated_at=now,
        )
        assert item.phone == "13800138000"
        assert item.status == "active"
        assert item.is_admin is False

    def test_optional_fields(self):
        now = datetime.now(timezone.utc)
        item = AdminUserItem(
            id=uuid.uuid4(),
            phone="13800138001",
            status="active",
            created_at=now,
            updated_at=now,
        )
        assert item.nickname is None
        assert item.last_login_at is None


# ---------------------------------------------------------------------------
# 2. Admin permission dependency tests
# ---------------------------------------------------------------------------


class TestGetAdminUser:
    """Validates: Admin role check."""

    @pytest.mark.asyncio
    async def test_admin_user_passes(self):
        admin = _make_admin_user()
        result = await get_admin_user(current_user=admin)
        assert result is admin

    @pytest.mark.asyncio
    async def test_non_admin_raises_403(self):
        from fastapi import HTTPException

        user = _make_user_obj(is_admin=False)
        with pytest.raises(HTTPException) as exc_info:
            await get_admin_user(current_user=user)
        assert exc_info.value.status_code == 403


# ---------------------------------------------------------------------------
# 3. List users endpoint tests
# ---------------------------------------------------------------------------


class TestListUsersEndpoint:
    """Validates: Requirement 8.1, 8.2"""

    def test_list_users_success(self):
        admin = _make_admin_user()
        user1 = _make_user_obj(phone="13800138001")
        user2 = _make_user_obj(phone="13800138002")

        count_result = MagicMock()
        count_result.scalar_one.return_value = 2

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [user1, user2]

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        from app.database import get_db
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.get("/api/v1/admin/users?page=1&page_size=10")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 2
        assert len(body["data"]["items"]) == 2

    def test_list_users_with_phone_search(self):
        admin = _make_admin_user()
        user1 = _make_user_obj(phone="13800138001")

        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [user1]

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        from app.database import get_db
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.get("/api/v1/admin/users?phone=138")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 1

    def test_page_size_exceeds_max_returns_422(self):
        admin = _make_admin_user()
        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin

        client = TestClient(app)
        response = client.get("/api/v1/admin/users?page_size=21")
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# 4. Disable user endpoint tests
# ---------------------------------------------------------------------------


class TestDisableUserEndpoint:
    """Validates: Requirement 8.3"""

    def test_disable_user_success(self):
        admin = _make_admin_user()
        target_user = _make_user_obj(status="active")

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = target_user

        update_result = MagicMock()

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[select_result, update_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        from app.database import get_db
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.put(f"/api/v1/admin/users/{target_user.id}/disable")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["message"] == "用户已禁用"

    def test_disable_nonexistent_user(self):
        admin = _make_admin_user()

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=select_result)

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        from app.database import get_db
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.put(f"/api/v1/admin/users/{uuid.uuid4()}/disable")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 404
        assert body["message"] == "用户不存在"

    def test_disable_already_disabled_user(self):
        admin = _make_admin_user()
        target_user = _make_user_obj(status="disabled")

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = target_user

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=select_result)

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        from app.database import get_db
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.put(f"/api/v1/admin/users/{target_user.id}/disable")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 400
        assert body["message"] == "该用户已被禁用"

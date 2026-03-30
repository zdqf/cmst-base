"""Unit tests for admin order management API (Task 10.6).

Validates Requirements:
- 13.1: Paginated order list with order_no, user info, amount, status, time
- 13.2: Update order status and record operation time
- 13.3: Filter orders by status and date range
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database import get_db
from app.routers.admin.orders import router
from app.routers.admin.users import get_admin_user
from app.schemas.order import AdminOrderListItem, AdminOrderStatusUpdate


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


def _make_order(**overrides) -> MagicMock:
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        order_no="ORD20250101000000ABC123",
        total_amount=Decimal("99.80"),
        status="pending",
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


class TestAdminOrderSchemas:
    """Validates: Requirement 13.2 — order status update schema."""

    def test_status_update_pending(self):
        schema = AdminOrderStatusUpdate(status="pending")
        assert schema.status == "pending"

    def test_status_update_paid(self):
        schema = AdminOrderStatusUpdate(status="paid")
        assert schema.status == "paid"

    def test_status_update_shipped(self):
        schema = AdminOrderStatusUpdate(status="shipped")
        assert schema.status == "shipped"

    def test_status_update_completed(self):
        schema = AdminOrderStatusUpdate(status="completed")
        assert schema.status == "completed"

    def test_status_update_cancelled(self):
        schema = AdminOrderStatusUpdate(status="cancelled")
        assert schema.status == "cancelled"

    def test_status_update_invalid_raises(self):
        with pytest.raises(Exception):
            AdminOrderStatusUpdate(status="deleted")

    def test_status_update_empty_raises(self):
        with pytest.raises(Exception):
            AdminOrderStatusUpdate(status="")

    def test_admin_order_list_item(self):
        now = datetime.now(timezone.utc)
        item = AdminOrderListItem(
            id=uuid.uuid4(),
            order_no="ORD123",
            user_id=uuid.uuid4(),
            total_amount=Decimal("50.00"),
            status="pending",
            created_at=now,
            updated_at=now,
        )
        assert item.order_no == "ORD123"
        assert item.status == "pending"


# ---------------------------------------------------------------------------
# 2. List orders endpoint tests
# ---------------------------------------------------------------------------


class TestListOrdersEndpoint:
    """Validates: Requirement 13.1, 13.3 — admin order list with filters."""

    def test_list_orders_success(self):
        admin = _make_admin_user()
        o1 = _make_order(order_no="ORD001", status="pending")
        o2 = _make_order(order_no="ORD002", status="paid")

        count_result = MagicMock()
        count_result.scalar_one.return_value = 2

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [o1, o2]

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.get("/api/v1/admin/orders?page=1&page_size=10")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 2
        assert len(body["data"]["items"]) == 2

    def test_list_with_status_filter(self):
        admin = _make_admin_user()
        o1 = _make_order(status="shipped")

        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [o1]

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.get("/api/v1/admin/orders?status=shipped")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 1

    def test_list_with_date_range(self):
        admin = _make_admin_user()
        o1 = _make_order()

        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [o1]

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.get(
            "/api/v1/admin/orders?start_date=2025-01-01&end_date=2025-12-31"
        )

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
        response = client.get("/api/v1/admin/orders")

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
        response = client.get("/api/v1/admin/orders?page_size=21")
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# 3. Update order status endpoint tests
# ---------------------------------------------------------------------------


class TestUpdateOrderStatusEndpoint:
    """Validates: Requirement 13.2 — update order status and record time."""

    def test_update_status_success(self):
        admin = _make_admin_user()
        order = _make_order(status="pending")

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = order

        update_result = MagicMock()

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[select_result, update_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.put(
            f"/api/v1/admin/orders/{order.id}/status",
            json={"status": "shipped"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["message"] == "订单状态已更新"
        assert body["data"]["status"] == "shipped"
        assert "updated_at" in body["data"]

    def test_update_status_to_cancelled(self):
        admin = _make_admin_user()
        order = _make_order(status="pending")

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = order

        update_result = MagicMock()

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[select_result, update_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.put(
            f"/api/v1/admin/orders/{order.id}/status",
            json={"status": "cancelled"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["status"] == "cancelled"

    def test_update_status_order_not_found(self):
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
            f"/api/v1/admin/orders/{uuid.uuid4()}/status",
            json={"status": "shipped"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 404
        assert body["message"] == "订单不存在"

    def test_update_status_invalid_returns_422(self):
        admin = _make_admin_user()
        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin

        client = TestClient(app)
        response = client.put(
            f"/api/v1/admin/orders/{uuid.uuid4()}/status",
            json={"status": "deleted"},
        )
        assert response.status_code == 422

    def test_update_status_empty_returns_422(self):
        admin = _make_admin_user()
        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin

        client = TestClient(app)
        response = client.put(
            f"/api/v1/admin/orders/{uuid.uuid4()}/status",
            json={"status": ""},
        )
        assert response.status_code == 422

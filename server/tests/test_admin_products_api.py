"""Unit tests for admin product management API (Task 10.5).

Validates Requirements:
- 12.1: Create product with all fields
- 12.2: Update product info
- 12.3: Modify stock with change log
- 12.4: Toggle product status (active/inactive)
- 12.5: List products with category/status filter
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database import get_db
from app.routers.admin.products import router
from app.routers.admin.users import get_admin_user
from app.schemas.product import (
    AdminProductCreate,
    AdminProductStatusUpdate,
    AdminProductStockUpdate,
    AdminProductUpdate,
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


def _make_product(**overrides) -> MagicMock:
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=uuid.uuid4(),
        name="枸杞茶",
        category="简加工产品",
        price=Decimal("29.90"),
        specification="100g/袋",
        description="精选枸杞制成",
        image_url="https://example.com/img.jpg",
        stock=50,
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


class TestAdminProductSchemas:
    """Validates: Requirement 12.1, 12.2 — product create/update schemas."""

    def test_create_valid(self):
        schema = AdminProductCreate(name="枸杞茶", price=Decimal("29.90"))
        assert schema.name == "枸杞茶"
        assert schema.price == Decimal("29.90")
        assert schema.stock == 0

    def test_create_with_stock(self):
        schema = AdminProductCreate(name="枸杞茶", price=Decimal("29.90"), stock=100)
        assert schema.stock == 100

    def test_create_missing_name_raises(self):
        with pytest.raises(Exception):
            AdminProductCreate(price=Decimal("29.90"))

    def test_create_empty_name_raises(self):
        with pytest.raises(Exception):
            AdminProductCreate(name="", price=Decimal("29.90"))

    def test_create_missing_price_raises(self):
        with pytest.raises(Exception):
            AdminProductCreate(name="枸杞茶")

    def test_create_zero_price_raises(self):
        with pytest.raises(Exception):
            AdminProductCreate(name="枸杞茶", price=Decimal("0"))

    def test_update_partial(self):
        schema = AdminProductUpdate(category="原药材")
        data = schema.model_dump(exclude_unset=True)
        assert data == {"category": "原药材"}

    def test_status_update_valid(self):
        schema = AdminProductStatusUpdate(status="active")
        assert schema.status == "active"

    def test_status_update_invalid_raises(self):
        with pytest.raises(Exception):
            AdminProductStatusUpdate(status="deleted")

    def test_stock_update_valid(self):
        schema = AdminProductStockUpdate(change_amount=10, reason="进货补充")
        assert schema.change_amount == 10
        assert schema.reason == "进货补充"

    def test_stock_update_zero_raises(self):
        with pytest.raises(Exception):
            AdminProductStockUpdate(change_amount=0, reason="无变更")

    def test_stock_update_missing_reason_raises(self):
        with pytest.raises(Exception):
            AdminProductStockUpdate(change_amount=10)


# ---------------------------------------------------------------------------
# 2. List products endpoint tests
# ---------------------------------------------------------------------------


class TestListProductsEndpoint:
    """Validates: Requirement 12.5 — admin product list with filters."""

    def test_list_products_success(self):
        admin = _make_admin_user()
        p1 = _make_product(name="枸杞茶")
        p2 = _make_product(name="当归片", status="inactive")

        count_result = MagicMock()
        count_result.scalar_one.return_value = 2

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [p1, p2]

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.get("/api/v1/admin/products?page=1&page_size=10")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 2
        assert len(body["data"]["items"]) == 2

    def test_list_with_category_filter(self):
        admin = _make_admin_user()
        p1 = _make_product(name="枸杞茶", category="简加工产品")

        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [p1]

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.get("/api/v1/admin/products?category=简加工产品")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 1

    def test_list_with_status_filter(self):
        admin = _make_admin_user()
        p1 = _make_product(status="active")

        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [p1]

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.get("/api/v1/admin/products?status=active")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 1

    def test_page_size_exceeds_max_returns_422(self):
        admin = _make_admin_user()
        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin

        client = TestClient(app)
        response = client.get("/api/v1/admin/products?page_size=21")
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# 3. Create product endpoint tests
# ---------------------------------------------------------------------------


class TestCreateProductEndpoint:
    """Validates: Requirement 12.1 — create product with all fields."""

    def test_create_product_success(self):
        admin = _make_admin_user()
        new_product = _make_product(name="黄芪片")

        mock_db = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()
        mock_db.refresh = AsyncMock(
            side_effect=lambda p: _apply_product_defaults(p, new_product)
        )

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.post(
            "/api/v1/admin/products",
            json={
                "name": "黄芪片",
                "category": "原药材",
                "price": "19.90",
                "specification": "50g/袋",
                "stock": 100,
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["message"] == "商品创建成功"

    def test_create_product_missing_name_returns_422(self):
        admin = _make_admin_user()
        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin

        client = TestClient(app)
        response = client.post(
            "/api/v1/admin/products", json={"price": "19.90"}
        )
        assert response.status_code == 422

    def test_create_product_missing_price_returns_422(self):
        admin = _make_admin_user()
        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin

        client = TestClient(app)
        response = client.post(
            "/api/v1/admin/products", json={"name": "黄芪片"}
        )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# 4. Update product endpoint tests
# ---------------------------------------------------------------------------


class TestUpdateProductEndpoint:
    """Validates: Requirement 12.2 — update product info."""

    def test_update_product_success(self):
        admin = _make_admin_user()
        product = _make_product(name="枸杞茶")
        updated = _make_product(name="枸杞茶", category="原药材")

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = product

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
            f"/api/v1/admin/products/{product.id}",
            json={"category": "原药材"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["message"] == "商品信息已更新"

    def test_update_product_not_found(self):
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
            f"/api/v1/admin/products/{uuid.uuid4()}",
            json={"category": "原药材"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 404
        assert body["message"] == "商品不存在"


# ---------------------------------------------------------------------------
# 5. Update product status endpoint tests
# ---------------------------------------------------------------------------


class TestUpdateProductStatusEndpoint:
    """Validates: Requirement 12.4 — toggle product active/inactive."""

    def test_set_inactive(self):
        admin = _make_admin_user()
        product = _make_product(status="active")

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = product

        update_result = MagicMock()

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[select_result, update_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.put(
            f"/api/v1/admin/products/{product.id}/status",
            json={"status": "inactive"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["message"] == "已下架"

    def test_set_active(self):
        admin = _make_admin_user()
        product = _make_product(status="inactive")

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = product

        update_result = MagicMock()

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[select_result, update_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.put(
            f"/api/v1/admin/products/{product.id}/status",
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
            f"/api/v1/admin/products/{uuid.uuid4()}/status",
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
            f"/api/v1/admin/products/{uuid.uuid4()}/status",
            json={"status": "deleted"},
        )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# 6. Update product stock endpoint tests
# ---------------------------------------------------------------------------


class TestUpdateProductStockEndpoint:
    """Validates: Requirement 12.3 — modify stock with change log."""

    def test_increase_stock_success(self):
        admin = _make_admin_user()
        product = _make_product(stock=50)

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = product

        update_result = MagicMock()

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[select_result, update_result])
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.put(
            f"/api/v1/admin/products/{product.id}/stock",
            json={"change_amount": 20, "reason": "进货补充"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["message"] == "库存已更新"
        assert body["data"]["stock"] == 70
        assert body["data"]["change_amount"] == 20

    def test_decrease_stock_success(self):
        admin = _make_admin_user()
        product = _make_product(stock=50)

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = product

        update_result = MagicMock()

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[select_result, update_result])
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.put(
            f"/api/v1/admin/products/{product.id}/stock",
            json={"change_amount": -10, "reason": "盘点损耗"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["stock"] == 40

    def test_decrease_stock_insufficient(self):
        admin = _make_admin_user()
        product = _make_product(stock=5)

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = product

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=select_result)

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.put(
            f"/api/v1/admin/products/{product.id}/stock",
            json={"change_amount": -10, "reason": "盘点损耗"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 400
        assert body["message"] == "库存不足，无法减少"

    def test_stock_not_found(self):
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
            f"/api/v1/admin/products/{uuid.uuid4()}/stock",
            json={"change_amount": 10, "reason": "补货"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 404

    def test_stock_zero_change_returns_422(self):
        admin = _make_admin_user()
        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin

        client = TestClient(app)
        response = client.put(
            f"/api/v1/admin/products/{uuid.uuid4()}/stock",
            json={"change_amount": 0, "reason": "无变更"},
        )
        assert response.status_code == 422

    def test_stock_missing_reason_returns_422(self):
        admin = _make_admin_user()
        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin

        client = TestClient(app)
        response = client.put(
            f"/api/v1/admin/products/{uuid.uuid4()}/stock",
            json={"change_amount": 10},
        )
        assert response.status_code == 422

    def test_stock_log_records_operator(self):
        """Verify that the stock log is created with the admin's operator_id."""
        admin = _make_admin_user()
        product = _make_product(stock=50)

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = product

        update_result = MagicMock()

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[select_result, update_result])
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        client.put(
            f"/api/v1/admin/products/{product.id}/stock",
            json={"change_amount": 5, "reason": "补货"},
        )

        # Verify db.add was called with a StockLog
        mock_db.add.assert_called_once()
        log_arg = mock_db.add.call_args[0][0]
        assert log_arg.product_id == product.id
        assert log_arg.change_amount == 5
        assert log_arg.reason == "补货"
        assert log_arg.operator_id == admin.id


# ---------------------------------------------------------------------------
# Helper for mocking db.refresh
# ---------------------------------------------------------------------------

def _apply_product_defaults(target, source):
    """Copy attributes from source mock to target Product ORM instance."""
    target.id = source.id
    target.name = source.name if hasattr(source, "name") else target.name
    target.category = source.category
    target.price = source.price
    target.specification = source.specification
    target.description = source.description
    target.image_url = source.image_url
    target.stock = source.stock
    target.status = source.status
    target.created_at = source.created_at
    target.updated_at = source.updated_at

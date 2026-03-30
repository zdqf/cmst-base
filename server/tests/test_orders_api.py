"""Unit tests for order API — schemas, services, and router endpoints (Task 8.3).

Validates Requirements:
- 7.4: Create order with stock validation
- 7.5: Insufficient stock returns error
- 7.6: Deduct stock after order creation
- 7.7: Order list paginated, time descending
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.order import (
    CreateOrderRequest,
    OrderItemRequest,
    OrderItemResponse,
    OrderListItem,
    OrderResponse,
)


# ---------------------------------------------------------------------------
# 1. Schema validation tests
# ---------------------------------------------------------------------------


class TestOrderItemRequest:
    """Validates: Requirement 7.4 — order item request validation."""

    def test_valid(self):
        req = OrderItemRequest(product_id=uuid.uuid4(), quantity=3)
        assert req.quantity == 3

    def test_quantity_min_1(self):
        with pytest.raises(Exception):
            OrderItemRequest(product_id=uuid.uuid4(), quantity=0)


class TestCreateOrderRequest:
    """Validates: Requirement 7.4 — create order request validation."""

    def test_valid_single_item(self):
        req = CreateOrderRequest(
            items=[OrderItemRequest(product_id=uuid.uuid4(), quantity=1)]
        )
        assert len(req.items) == 1

    def test_valid_multiple_items(self):
        req = CreateOrderRequest(
            items=[
                OrderItemRequest(product_id=uuid.uuid4(), quantity=2),
                OrderItemRequest(product_id=uuid.uuid4(), quantity=1),
            ]
        )
        assert len(req.items) == 2

    def test_empty_items_rejected(self):
        with pytest.raises(Exception):
            CreateOrderRequest(items=[])


class TestOrderItemResponse:
    """Validates: Requirement 7.4 — order item response."""

    def test_valid(self):
        resp = OrderItemResponse(
            product_id=uuid.uuid4(),
            product_name="枸杞干果",
            quantity=2,
            unit_price=Decimal("29.90"),
        )
        assert resp.product_name == "枸杞干果"
        assert resp.unit_price == Decimal("29.90")


class TestOrderResponse:
    """Validates: Requirement 7.4 — full order response."""

    def test_valid(self):
        now = datetime.now(timezone.utc)
        resp = OrderResponse(
            id=uuid.uuid4(),
            order_no="ORD20240101120000000000ABCDEF",
            total_amount=Decimal("59.80"),
            status="pending",
            items=[
                OrderItemResponse(
                    product_id=uuid.uuid4(),
                    product_name="枸杞干果",
                    quantity=2,
                    unit_price=Decimal("29.90"),
                )
            ],
            created_at=now,
        )
        assert resp.status == "pending"
        assert len(resp.items) == 1


class TestOrderListItem:
    """Validates: Requirement 7.7 — order list item."""

    def test_valid(self):
        now = datetime.now(timezone.utc)
        item = OrderListItem(
            id=uuid.uuid4(),
            order_no="ORD20240101120000000000ABCDEF",
            total_amount=Decimal("100.00"),
            status="pending",
            created_at=now,
        )
        assert item.total_amount == Decimal("100.00")


# ---------------------------------------------------------------------------
# 2. Helpers for mock ORM objects
# ---------------------------------------------------------------------------


def _make_product(**overrides):
    defaults = dict(
        id=uuid.uuid4(),
        name="枸杞干果",
        price=Decimal("29.90"),
        stock=100,
        status="active",
    )
    defaults.update(overrides)
    obj = MagicMock()
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


def _make_order_item(order_id=None, product=None, **overrides):
    if product is None:
        product = _make_product()
    defaults = dict(
        id=uuid.uuid4(),
        order_id=order_id or uuid.uuid4(),
        product_id=product.id,
        quantity=1,
        unit_price=product.price,
        product=product,
    )
    defaults.update(overrides)
    obj = MagicMock()
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


def _make_order(user_id=None, items=None, **overrides):
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=uuid.uuid4(),
        user_id=user_id or uuid.uuid4(),
        order_no="ORD20240101120000000000ABCDEF",
        total_amount=Decimal("59.80"),
        status="pending",
        created_at=now,
        updated_at=now,
        items=items or [],
    )
    defaults.update(overrides)
    obj = MagicMock()
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


def _mock_user():
    user = MagicMock()
    user.id = uuid.uuid4()
    user.status = "active"
    return user


# ---------------------------------------------------------------------------
# 3. Service layer tests
# ---------------------------------------------------------------------------


class TestCreateOrderService:
    """Validates: Requirements 7.4, 7.5, 7.6 — create order with stock validation."""

    @pytest.mark.asyncio
    async def test_create_order_success(self):
        from app.services.order_service import create_order

        product = _make_product(stock=10)
        product.stock = 10  # real int for arithmetic

        # Mock db.execute for product lookup
        product_result = MagicMock()
        product_result.scalars.return_value.all.return_value = [product]

        # Mock db.execute for order reload
        order_id = uuid.uuid4()
        order_item = _make_order_item(order_id=order_id, product=product)
        reloaded_order = _make_order(items=[order_item])
        reloaded_order.id = order_id

        reload_result = MagicMock()
        reload_result.unique.return_value.scalar_one.return_value = reloaded_order

        mock_db = AsyncMock()
        mock_db.execute.side_effect = [product_result, reload_result]

        items = [OrderItemRequest(product_id=product.id, quantity=2)]
        user_id = uuid.uuid4()

        result = await create_order(mock_db, user_id, items)

        assert result.id == order_id
        mock_db.add.assert_called()
        mock_db.flush.assert_awaited()
        assert product.stock == 8  # deducted

    @pytest.mark.asyncio
    async def test_create_order_insufficient_stock(self):
        """Validates: Requirement 7.5 — insufficient stock blocks order."""
        from app.services.order_service import create_order

        product = _make_product(stock=1)
        product.stock = 1

        product_result = MagicMock()
        product_result.scalars.return_value.all.return_value = [product]

        mock_db = AsyncMock()
        mock_db.execute.return_value = product_result

        items = [OrderItemRequest(product_id=product.id, quantity=5)]

        with pytest.raises(ValueError, match="库存不足"):
            await create_order(mock_db, uuid.uuid4(), items)

    @pytest.mark.asyncio
    async def test_create_order_product_not_found(self):
        """Validates: Requirement 7.4 — non-existent product."""
        from app.services.order_service import create_order

        product_result = MagicMock()
        product_result.scalars.return_value.all.return_value = []

        mock_db = AsyncMock()
        mock_db.execute.return_value = product_result

        items = [OrderItemRequest(product_id=uuid.uuid4(), quantity=1)]

        with pytest.raises(ValueError, match="商品不存在"):
            await create_order(mock_db, uuid.uuid4(), items)


class TestListOrdersService:
    """Validates: Requirement 7.7 — paginated order list."""

    @pytest.mark.asyncio
    async def test_list_orders(self):
        from app.services.order_service import list_orders

        order1 = _make_order()
        order2 = _make_order()

        count_result = MagicMock()
        count_result.scalar_one.return_value = 2

        orders_result = MagicMock()
        orders_result.scalars.return_value.all.return_value = [order1, order2]

        mock_db = AsyncMock()
        mock_db.execute.side_effect = [count_result, orders_result]

        result = await list_orders(mock_db, uuid.uuid4(), page=1, page_size=10)

        assert result.total == 2
        assert len(result.items) == 2
        assert result.page == 1

    @pytest.mark.asyncio
    async def test_list_orders_empty(self):
        from app.services.order_service import list_orders

        count_result = MagicMock()
        count_result.scalar_one.return_value = 0

        orders_result = MagicMock()
        orders_result.scalars.return_value.all.return_value = []

        mock_db = AsyncMock()
        mock_db.execute.side_effect = [count_result, orders_result]

        result = await list_orders(mock_db, uuid.uuid4(), page=1, page_size=10)

        assert result.total == 0
        assert len(result.items) == 0


# ---------------------------------------------------------------------------
# 4. Router endpoint tests
# ---------------------------------------------------------------------------


class TestCreateOrderEndpoint:
    """Validates: Requirements 7.4, 7.5 — POST /api/v1/orders"""

    def test_create_success(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.middleware.auth import get_current_user

        user = _mock_user()
        product = _make_product()
        order_item = _make_order_item(product=product)
        order = _make_order(user_id=user.id, items=[order_item])

        app.dependency_overrides[get_current_user] = lambda: user
        try:
            with patch(
                "app.routers.orders.create_order", new_callable=AsyncMock
            ) as mock_create:
                mock_create.return_value = order
                client = TestClient(app)
                response = client.post(
                    "/api/v1/orders",
                    json={
                        "items": [
                            {"product_id": str(product.id), "quantity": 1}
                        ]
                    },
                )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["message"] == "订单创建成功"
        assert body["data"]["order_no"] == order.order_no

    def test_create_insufficient_stock(self):
        """Validates: Requirement 7.5 — stock error returns 400-level code."""
        from fastapi.testclient import TestClient
        from app.main import app
        from app.middleware.auth import get_current_user

        user = _mock_user()
        app.dependency_overrides[get_current_user] = lambda: user
        try:
            with patch(
                "app.routers.orders.create_order", new_callable=AsyncMock
            ) as mock_create:
                mock_create.side_effect = ValueError("商品「枸杞干果」库存不足，当前库存: 1")
                client = TestClient(app)
                response = client.post(
                    "/api/v1/orders",
                    json={
                        "items": [
                            {"product_id": str(uuid.uuid4()), "quantity": 5}
                        ]
                    },
                )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 400
        assert "库存不足" in body["message"]

    def test_create_empty_items_rejected(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.middleware.auth import get_current_user

        user = _mock_user()
        app.dependency_overrides[get_current_user] = lambda: user
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/orders",
                json={"items": []},
            )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 422


class TestListOrdersEndpoint:
    """Validates: Requirement 7.7 — GET /api/v1/orders"""

    def test_list_success(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.middleware.auth import get_current_user
        from app.schemas.common import PaginatedResponse

        user = _mock_user()
        now = datetime.now(timezone.utc)
        paginated = PaginatedResponse.create(
            items=[
                OrderListItem(
                    id=uuid.uuid4(),
                    order_no="ORD001",
                    total_amount=Decimal("59.80"),
                    status="pending",
                    created_at=now,
                )
            ],
            total=1,
            page=1,
            page_size=10,
        )

        app.dependency_overrides[get_current_user] = lambda: user
        try:
            with patch(
                "app.routers.orders.list_orders", new_callable=AsyncMock
            ) as mock_list:
                mock_list.return_value = paginated
                client = TestClient(app)
                response = client.get("/api/v1/orders")
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 1
        assert len(body["data"]["items"]) == 1

    def test_list_empty(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.middleware.auth import get_current_user
        from app.schemas.common import PaginatedResponse

        user = _mock_user()
        paginated = PaginatedResponse.create(
            items=[], total=0, page=1, page_size=10
        )

        app.dependency_overrides[get_current_user] = lambda: user
        try:
            with patch(
                "app.routers.orders.list_orders", new_callable=AsyncMock
            ) as mock_list:
                mock_list.return_value = paginated
                client = TestClient(app)
                response = client.get("/api/v1/orders")
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 0
        assert body["data"]["items"] == []

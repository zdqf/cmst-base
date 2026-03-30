"""Unit tests for cart API — schemas, services, and router endpoints (Task 8.2).

Validates Requirements:
- 7.3: Cart add, update, remove, and list operations
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.cart import CartAddRequest, CartItemResponse, CartUpdateRequest


# ---------------------------------------------------------------------------
# 1. Schema validation tests
# ---------------------------------------------------------------------------


class TestCartAddRequest:
    """Validates: Requirement 7.3 — add to cart request."""

    def test_defaults(self):
        req = CartAddRequest(product_id=uuid.uuid4())
        assert req.quantity == 1

    def test_custom_quantity(self):
        pid = uuid.uuid4()
        req = CartAddRequest(product_id=pid, quantity=5)
        assert req.product_id == pid
        assert req.quantity == 5

    def test_quantity_min_1(self):
        with pytest.raises(Exception):
            CartAddRequest(product_id=uuid.uuid4(), quantity=0)


class TestCartUpdateRequest:
    """Validates: Requirement 7.3 — update cart item request."""

    def test_valid(self):
        req = CartUpdateRequest(quantity=3)
        assert req.quantity == 3

    def test_quantity_min_1(self):
        with pytest.raises(Exception):
            CartUpdateRequest(quantity=0)


class TestCartItemResponse:
    """Validates: Requirement 7.3 — cart item response."""

    def test_valid(self):
        item = CartItemResponse(
            id=uuid.uuid4(),
            product_id=uuid.uuid4(),
            product_name="枸杞干果",
            quantity=2,
            unit_price=Decimal("29.90"),
        )
        assert item.product_name == "枸杞干果"
        assert item.quantity == 2
        assert item.unit_price == Decimal("29.90")


# ---------------------------------------------------------------------------
# 2. Helper to create mock CartItem / Product ORM objects
# ---------------------------------------------------------------------------


def _make_product(**overrides):
    defaults = dict(
        id=uuid.uuid4(),
        name="枸杞干果",
        price=Decimal("29.90"),
    )
    defaults.update(overrides)
    obj = MagicMock()
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


def _make_cart_item(**overrides):
    now = datetime.now(timezone.utc)
    product = overrides.pop("product", _make_product())
    defaults = dict(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        product_id=product.id,
        quantity=1,
        created_at=now,
        updated_at=now,
        product=product,
    )
    defaults.update(overrides)
    obj = MagicMock()
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


# ---------------------------------------------------------------------------
# 3. Service layer tests
# ---------------------------------------------------------------------------


class TestAddToCartService:
    """Validates: Requirement 7.3 — add to cart logic."""

    @pytest.mark.asyncio
    async def test_add_new_item(self):
        from app.services.cart_service import add_to_cart

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        user_id = uuid.uuid4()
        product_id = uuid.uuid4()
        result = await add_to_cart(mock_db, user_id, product_id, 2)

        mock_db.add.assert_called_once()
        mock_db.flush.assert_awaited_once()
        added_item = mock_db.add.call_args[0][0]
        assert added_item.user_id == user_id
        assert added_item.product_id == product_id
        assert added_item.quantity == 2

    @pytest.mark.asyncio
    async def test_increment_existing_item(self):
        from app.services.cart_service import add_to_cart

        existing = _make_cart_item(quantity=3)
        # Make quantity a real int so += works
        existing.quantity = 3

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        result = await add_to_cart(mock_db, existing.user_id, existing.product_id, 2)

        assert result.quantity == 5
        mock_db.flush.assert_awaited_once()


class TestUpdateCartItemService:
    """Validates: Requirement 7.3 — update cart item quantity."""

    @pytest.mark.asyncio
    async def test_update_found(self):
        from app.services.cart_service import update_cart_item

        item = _make_cart_item(quantity=1)
        item.quantity = 1

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = item

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        result = await update_cart_item(mock_db, item.user_id, item.id, 5)

        assert result is not None
        assert result.quantity == 5
        mock_db.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_not_found(self):
        from app.services.cart_service import update_cart_item

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        result = await update_cart_item(mock_db, uuid.uuid4(), uuid.uuid4(), 5)
        assert result is None


class TestRemoveFromCartService:
    """Validates: Requirement 7.3 — remove cart item."""

    @pytest.mark.asyncio
    async def test_remove_found(self):
        from app.services.cart_service import remove_from_cart

        item = _make_cart_item()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = item

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        result = await remove_from_cart(mock_db, item.user_id, item.id)

        assert result is True
        mock_db.delete.assert_awaited_once_with(item)
        mock_db.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_remove_not_found(self):
        from app.services.cart_service import remove_from_cart

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        result = await remove_from_cart(mock_db, uuid.uuid4(), uuid.uuid4())
        assert result is False


class TestGetCartService:
    """Validates: Requirement 7.3 — list cart items."""

    @pytest.mark.asyncio
    async def test_returns_items(self):
        from app.services.cart_service import get_cart

        item1 = _make_cart_item()
        item2 = _make_cart_item()

        mock_result = MagicMock()
        mock_result.scalars.return_value.unique.return_value.all.return_value = [item1, item2]

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        result = await get_cart(mock_db, uuid.uuid4())
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_empty_cart(self):
        from app.services.cart_service import get_cart

        mock_result = MagicMock()
        mock_result.scalars.return_value.unique.return_value.all.return_value = []

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        result = await get_cart(mock_db, uuid.uuid4())
        assert len(result) == 0


# ---------------------------------------------------------------------------
# 4. Router endpoint tests (using app.dependency_overrides)
# ---------------------------------------------------------------------------


def _mock_user():
    user = MagicMock()
    user.id = uuid.uuid4()
    user.status = "active"
    return user


class TestAddToCartEndpoint:
    """Validates: Requirement 7.3 — POST /api/v1/cart"""

    def test_add_success(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.middleware.auth import get_current_user

        user = _mock_user()
        product_id = uuid.uuid4()
        item_id = uuid.uuid4()

        mock_item = MagicMock()
        mock_item.id = item_id
        mock_item.quantity = 1

        app.dependency_overrides[get_current_user] = lambda: user
        try:
            with patch("app.routers.cart.add_to_cart", new_callable=AsyncMock) as mock_add:
                mock_add.return_value = mock_item
                client = TestClient(app)
                response = client.post(
                    "/api/v1/cart",
                    json={"product_id": str(product_id), "quantity": 2},
                )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["message"] == "已添加到购物车"
        assert body["data"]["id"] == str(item_id)

    def test_add_invalid_quantity(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.middleware.auth import get_current_user

        user = _mock_user()
        app.dependency_overrides[get_current_user] = lambda: user
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/cart",
                json={"product_id": str(uuid.uuid4()), "quantity": 0},
            )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 422


class TestUpdateCartItemEndpoint:
    """Validates: Requirement 7.3 — PUT /api/v1/cart/{item_id}"""

    def test_update_success(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.middleware.auth import get_current_user

        user = _mock_user()
        item_id = uuid.uuid4()

        mock_item = MagicMock()
        mock_item.id = item_id
        mock_item.quantity = 5

        app.dependency_overrides[get_current_user] = lambda: user
        try:
            with patch("app.routers.cart.update_cart_item", new_callable=AsyncMock) as mock_update:
                mock_update.return_value = mock_item
                client = TestClient(app)
                response = client.put(
                    f"/api/v1/cart/{item_id}",
                    json={"quantity": 5},
                )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["message"] == "数量已更新"
        assert body["data"]["quantity"] == 5

    def test_update_not_found(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.middleware.auth import get_current_user

        user = _mock_user()
        app.dependency_overrides[get_current_user] = lambda: user
        try:
            with patch("app.routers.cart.update_cart_item", new_callable=AsyncMock) as mock_update:
                mock_update.return_value = None
                client = TestClient(app)
                response = client.put(
                    f"/api/v1/cart/{uuid.uuid4()}",
                    json={"quantity": 3},
                )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 404
        assert body["message"] == "购物车商品不存在"


class TestRemoveFromCartEndpoint:
    """Validates: Requirement 7.3 — DELETE /api/v1/cart/{item_id}"""

    def test_remove_success(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.middleware.auth import get_current_user

        user = _mock_user()
        app.dependency_overrides[get_current_user] = lambda: user
        try:
            with patch("app.routers.cart.remove_from_cart", new_callable=AsyncMock) as mock_remove:
                mock_remove.return_value = True
                client = TestClient(app)
                response = client.delete(f"/api/v1/cart/{uuid.uuid4()}")
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["message"] == "已从购物车移除"

    def test_remove_not_found(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.middleware.auth import get_current_user

        user = _mock_user()
        app.dependency_overrides[get_current_user] = lambda: user
        try:
            with patch("app.routers.cart.remove_from_cart", new_callable=AsyncMock) as mock_remove:
                mock_remove.return_value = False
                client = TestClient(app)
                response = client.delete(f"/api/v1/cart/{uuid.uuid4()}")
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 404


class TestGetCartEndpoint:
    """Validates: Requirement 7.3 — GET /api/v1/cart"""

    def test_get_cart_success(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.middleware.auth import get_current_user

        user = _mock_user()
        product = _make_product(name="枸杞干果", price=Decimal("29.90"))
        item = _make_cart_item(user_id=user.id, product=product, quantity=2)
        item.quantity = 2

        app.dependency_overrides[get_current_user] = lambda: user
        try:
            with patch("app.routers.cart.get_cart", new_callable=AsyncMock) as mock_get:
                mock_get.return_value = [item]
                client = TestClient(app)
                response = client.get("/api/v1/cart")
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert len(body["data"]) == 1
        assert body["data"][0]["product_name"] == "枸杞干果"
        assert body["data"][0]["quantity"] == 2

    def test_get_empty_cart(self):
        from fastapi.testclient import TestClient
        from app.main import app
        from app.middleware.auth import get_current_user

        user = _mock_user()
        app.dependency_overrides[get_current_user] = lambda: user
        try:
            with patch("app.routers.cart.get_cart", new_callable=AsyncMock) as mock_get:
                mock_get.return_value = []
                client = TestClient(app)
                response = client.get("/api/v1/cart")
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"] == []

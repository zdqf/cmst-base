"""Unit tests for product API — schemas, services, and router endpoints (Task 8.1).

Validates Requirements:
- 7.1: Product list with category filtering and pagination
- 7.2: Product detail with full information
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.common import PaginatedResponse
from app.schemas.product import ProductDetail, ProductListItem, ProductSearchParams


# ---------------------------------------------------------------------------
# 1. ProductSearchParams defaults and validation
# ---------------------------------------------------------------------------


class TestProductSearchParams:
    """Validates: Requirement 7.1 — pagination and category filter."""

    def test_defaults(self):
        params = ProductSearchParams()
        assert params.page == 1
        assert params.page_size == 10
        assert params.category is None

    def test_custom_values(self):
        params = ProductSearchParams(page=2, page_size=15, category="原药材")
        assert params.page == 2
        assert params.page_size == 15
        assert params.category == "原药材"

    def test_page_size_max_20(self):
        with pytest.raises(Exception):
            ProductSearchParams(page_size=21)

    def test_page_size_min_1(self):
        with pytest.raises(Exception):
            ProductSearchParams(page_size=0)

    def test_page_min_1(self):
        with pytest.raises(Exception):
            ProductSearchParams(page=0)


# ---------------------------------------------------------------------------
# 2. ProductListItem and ProductDetail schema validation
# ---------------------------------------------------------------------------


class TestProductListItem:
    """Validates: Requirement 7.1"""

    def test_valid_item(self):
        item = ProductListItem(
            id=uuid.uuid4(),
            name="枸杞干果",
            category="原药材",
            price=Decimal("29.90"),
            image_url="https://example.com/img.jpg",
            stock=100,
            status="active",
        )
        assert item.name == "枸杞干果"
        assert item.price == Decimal("29.90")
        assert item.stock == 100

    def test_optional_fields(self):
        item = ProductListItem(
            id=uuid.uuid4(),
            name="当归片",
            price=Decimal("45.00"),
            stock=50,
            status="active",
        )
        assert item.category is None
        assert item.image_url is None


class TestProductDetail:
    """Validates: Requirement 7.2"""

    def test_full_detail(self):
        now = datetime.now(timezone.utc)
        detail = ProductDetail(
            id=uuid.uuid4(),
            name="枸杞干果",
            category="原药材",
            price=Decimal("29.90"),
            specification="500g/袋",
            description="精选宁夏枸杞",
            image_url="https://example.com/img.jpg",
            stock=100,
            status="active",
            created_at=now,
            updated_at=now,
        )
        assert detail.name == "枸杞干果"
        assert detail.specification == "500g/袋"
        assert detail.description == "精选宁夏枸杞"

    def test_optional_fields_default_none(self):
        now = datetime.now(timezone.utc)
        detail = ProductDetail(
            id=uuid.uuid4(),
            name="当归片",
            price=Decimal("45.00"),
            stock=50,
            status="active",
            created_at=now,
            updated_at=now,
        )
        assert detail.category is None
        assert detail.specification is None
        assert detail.description is None
        assert detail.image_url is None


# ---------------------------------------------------------------------------
# 3. Helper to create mock Product ORM objects
# ---------------------------------------------------------------------------


def _make_product_row(**overrides):
    """Create a mock Product ORM object."""
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=uuid.uuid4(),
        name="枸杞干果",
        category="原药材",
        price=Decimal("29.90"),
        specification="500g/袋",
        description="精选宁夏枸杞",
        image_url="https://example.com/img.jpg",
        stock=100,
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
# 4. list_products service tests
# ---------------------------------------------------------------------------


class TestListProductsService:
    """Validates: Requirement 7.1 — paginated product query."""

    @pytest.mark.asyncio
    async def test_returns_paginated_response(self):
        from app.services.product_service import list_products

        p1 = _make_product_row(name="枸杞干果")
        p2 = _make_product_row(name="当归片")

        count_result = MagicMock()
        count_result.scalar_one.return_value = 2

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [p1, p2]

        mock_db = AsyncMock()
        mock_db.execute.side_effect = [count_result, data_result]

        params = ProductSearchParams(page=1, page_size=10)
        result = await list_products(mock_db, params)

        assert result.total == 2
        assert result.page == 1
        assert len(result.items) == 2
        assert result.items[0].name == "枸杞干果"
        assert result.items[1].name == "当归片"

    @pytest.mark.asyncio
    async def test_empty_result(self):
        from app.services.product_service import list_products

        count_result = MagicMock()
        count_result.scalar_one.return_value = 0

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = []

        mock_db = AsyncMock()
        mock_db.execute.side_effect = [count_result, data_result]

        params = ProductSearchParams(page=1, page_size=10)
        result = await list_products(mock_db, params)

        assert result.total == 0
        assert len(result.items) == 0
        assert result.total_pages == 0


# ---------------------------------------------------------------------------
# 5. get_product_detail service tests
# ---------------------------------------------------------------------------


class TestGetProductDetailService:
    """Validates: Requirement 7.2"""

    @pytest.mark.asyncio
    async def test_found(self):
        from app.services.product_service import get_product_detail

        product = _make_product_row(name="枸杞干果")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = product

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        result = await get_product_detail(mock_db, product.id)
        assert result is product

    @pytest.mark.asyncio
    async def test_not_found(self):
        from app.services.product_service import get_product_detail

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        result = await get_product_detail(mock_db, uuid.uuid4())
        assert result is None


# ---------------------------------------------------------------------------
# 6. Router endpoint tests using TestClient with mocked services
# ---------------------------------------------------------------------------


class TestListProductsEndpoint:
    """Validates: Requirement 7.1"""

    def test_list_products_success(self):
        from fastapi.testclient import TestClient
        from app.main import app

        paginated = PaginatedResponse[ProductListItem].create(
            items=[
                ProductListItem(
                    id=uuid.uuid4(),
                    name="枸杞干果",
                    category="原药材",
                    price=Decimal("29.90"),
                    stock=100,
                    status="active",
                ),
            ],
            total=1,
            page=1,
            page_size=10,
        )

        with patch("app.routers.products.list_products", new_callable=AsyncMock) as mock_list:
            mock_list.return_value = paginated
            with patch("app.routers.products.get_db"):
                client = TestClient(app)
                response = client.get("/api/v1/products?page=1&page_size=10")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 1
        assert len(body["data"]["items"]) == 1
        assert body["data"]["items"][0]["name"] == "枸杞干果"

    def test_list_products_with_category_filter(self):
        from fastapi.testclient import TestClient
        from app.main import app

        paginated = PaginatedResponse[ProductListItem].create(
            items=[], total=0, page=1, page_size=10
        )

        with patch("app.routers.products.list_products", new_callable=AsyncMock) as mock_list:
            mock_list.return_value = paginated
            with patch("app.routers.products.get_db"):
                client = TestClient(app)
                response = client.get("/api/v1/products?category=原药材")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 0

    def test_page_size_exceeds_max_returns_422(self):
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.get("/api/v1/products?page_size=21")
        assert response.status_code == 422


class TestProductDetailEndpoint:
    """Validates: Requirement 7.2"""

    def test_product_detail_found(self):
        from fastapi.testclient import TestClient
        from app.main import app

        product = _make_product_row(name="枸杞干果")

        with patch("app.routers.products.get_product_detail", new_callable=AsyncMock) as mock_detail:
            mock_detail.return_value = product
            with patch("app.routers.products.get_db"):
                client = TestClient(app)
                response = client.get(f"/api/v1/products/{product.id}")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["name"] == "枸杞干果"

    def test_product_detail_not_found(self):
        from fastapi.testclient import TestClient
        from app.main import app

        with patch("app.routers.products.get_product_detail", new_callable=AsyncMock) as mock_detail:
            mock_detail.return_value = None
            with patch("app.routers.products.get_db"):
                client = TestClient(app)
                response = client.get(f"/api/v1/products/{uuid.uuid4()}")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 404
        assert body["message"] == "商品不存在"

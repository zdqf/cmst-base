"""Unit tests for herb API — schemas, services, and router endpoints (Task 5.2).

Validates Requirements:
- 3.4: Paginated query, max 20 per page
- 3.5: Full herb detail display
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.common import PaginatedResponse
from app.schemas.herb import HerbDetail, HerbListItem, HerbSearchParams


# ---------------------------------------------------------------------------
# 1. HerbSearchParams defaults and validation
# ---------------------------------------------------------------------------


class TestHerbSearchParams:
    """Validates: Requirement 3.4 — page_size max 20."""

    def test_defaults(self):
        params = HerbSearchParams()
        assert params.page == 1
        assert params.page_size == 10
        assert params.category is None
        assert params.keyword is None

    def test_custom_values(self):
        params = HerbSearchParams(page=3, page_size=15, category="补气", keyword="枸杞")
        assert params.page == 3
        assert params.page_size == 15
        assert params.category == "补气"
        assert params.keyword == "枸杞"

    def test_page_size_max_20(self):
        with pytest.raises(Exception):
            HerbSearchParams(page_size=21)

    def test_page_size_min_1(self):
        with pytest.raises(Exception):
            HerbSearchParams(page_size=0)

    def test_page_min_1(self):
        with pytest.raises(Exception):
            HerbSearchParams(page=0)


# ---------------------------------------------------------------------------
# 2. HerbListItem and HerbDetail schema validation
# ---------------------------------------------------------------------------


class TestHerbListItem:
    """Validates: Requirement 3.5"""

    def test_valid_item(self):
        item = HerbListItem(
            id=uuid.uuid4(), name="枸杞", category="补气", status="active"
        )
        assert item.name == "枸杞"
        assert item.category == "补气"

    def test_optional_category(self):
        item = HerbListItem(id=uuid.uuid4(), name="当归", status="active")
        assert item.category is None


class TestHerbDetail:
    """Validates: Requirement 3.1, 3.5"""

    def test_full_detail(self):
        now = datetime.now(timezone.utc)
        detail = HerbDetail(
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
        assert detail.name == "枸杞"
        assert detail.origin_and_form == "茄科植物枸杞的干燥成熟果实"

    def test_optional_fields_default_none(self):
        now = datetime.now(timezone.utc)
        detail = HerbDetail(
            id=uuid.uuid4(),
            name="当归",
            status="active",
            created_at=now,
            updated_at=now,
        )
        assert detail.origin_and_form is None
        assert detail.flavor_meridian is None
        assert detail.common_pairings is None
        assert detail.unsuitable_groups is None
        assert detail.precautions is None


# ---------------------------------------------------------------------------
# 3. list_herbs service — mock DB, test pagination response structure
# ---------------------------------------------------------------------------


def _make_herb_row(**overrides):
    """Create a mock Herb ORM object."""
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=uuid.uuid4(),
        name="枸杞",
        category="补气",
        origin_and_form="来源描述",
        flavor_meridian="甘，平",
        common_pairings="菊花",
        unsuitable_groups="脾虚者",
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


class TestListHerbsService:
    """Validates: Requirement 3.4 — paginated query."""

    @pytest.mark.asyncio
    async def test_returns_paginated_response(self):
        from app.services.herb_service import list_herbs

        herb1 = _make_herb_row(name="枸杞")
        herb2 = _make_herb_row(name="当归")

        # Mock count query result
        count_result = MagicMock()
        count_result.scalar_one.return_value = 2

        # Mock data query result
        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [herb1, herb2]

        mock_db = AsyncMock()
        mock_db.execute.side_effect = [count_result, data_result]

        params = HerbSearchParams(page=1, page_size=10)
        result = await list_herbs(mock_db, params)

        assert result.total == 2
        assert result.page == 1
        assert len(result.items) == 2
        assert result.items[0].name == "枸杞"
        assert result.items[1].name == "当归"

    @pytest.mark.asyncio
    async def test_empty_result(self):
        from app.services.herb_service import list_herbs

        count_result = MagicMock()
        count_result.scalar_one.return_value = 0

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = []

        mock_db = AsyncMock()
        mock_db.execute.side_effect = [count_result, data_result]

        params = HerbSearchParams(page=1, page_size=10)
        result = await list_herbs(mock_db, params)

        assert result.total == 0
        assert len(result.items) == 0
        assert result.total_pages == 0


# ---------------------------------------------------------------------------
# 4. get_herb_detail service — found and not found
# ---------------------------------------------------------------------------


class TestGetHerbDetailService:
    """Validates: Requirement 3.5"""

    @pytest.mark.asyncio
    async def test_found(self):
        from app.services.herb_service import get_herb_detail

        herb = _make_herb_row(name="枸杞")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = herb

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        result = await get_herb_detail(mock_db, herb.id)
        assert result is herb

    @pytest.mark.asyncio
    async def test_not_found(self):
        from app.services.herb_service import get_herb_detail

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute.return_value = mock_result

        result = await get_herb_detail(mock_db, uuid.uuid4())
        assert result is None


# ---------------------------------------------------------------------------
# 5. get_daily_herb service — returns herb and returns None when empty
# ---------------------------------------------------------------------------


class TestGetDailyHerbService:
    """Validates: Requirement 2.2"""

    @pytest.mark.asyncio
    async def test_returns_herb(self):
        from app.services.herb_service import get_daily_herb

        herb = _make_herb_row(name="今日推荐")

        count_result = MagicMock()
        count_result.scalar_one.return_value = 5

        data_result = MagicMock()
        data_result.scalar_one_or_none.return_value = herb

        mock_db = AsyncMock()
        mock_db.execute.side_effect = [count_result, data_result]

        result = await get_daily_herb(mock_db)
        assert result is herb

    @pytest.mark.asyncio
    async def test_returns_none_when_empty(self):
        from app.services.herb_service import get_daily_herb

        count_result = MagicMock()
        count_result.scalar_one.return_value = 0

        mock_db = AsyncMock()
        mock_db.execute.return_value = count_result

        result = await get_daily_herb(mock_db)
        assert result is None


# ---------------------------------------------------------------------------
# 6. Router endpoint tests using TestClient with mocked services
# ---------------------------------------------------------------------------


class TestListHerbsEndpoint:
    """Validates: Requirement 3.4"""

    def test_list_herbs_success(self):
        from fastapi.testclient import TestClient
        from app.main import app

        paginated = PaginatedResponse[HerbListItem].create(
            items=[
                HerbListItem(id=uuid.uuid4(), name="枸杞", category="补气", status="active"),
            ],
            total=1,
            page=1,
            page_size=10,
        )

        with patch("app.routers.herbs.list_herbs", new_callable=AsyncMock) as mock_list:
            mock_list.return_value = paginated
            with patch("app.routers.herbs.get_db"):
                client = TestClient(app)
                response = client.get("/api/v1/herbs?page=1&page_size=10")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 1
        assert len(body["data"]["items"]) == 1
        assert body["data"]["items"][0]["name"] == "枸杞"

    def test_list_herbs_with_category_filter(self):
        from fastapi.testclient import TestClient
        from app.main import app

        paginated = PaginatedResponse[HerbListItem].create(
            items=[], total=0, page=1, page_size=10
        )

        with patch("app.routers.herbs.list_herbs", new_callable=AsyncMock) as mock_list:
            mock_list.return_value = paginated
            with patch("app.routers.herbs.get_db"):
                client = TestClient(app)
                response = client.get("/api/v1/herbs?category=补气")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 0

    def test_page_size_exceeds_max_returns_422(self):
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.get("/api/v1/herbs?page_size=21")
        assert response.status_code == 422


class TestHerbDetailEndpoint:
    """Validates: Requirement 3.5"""

    def test_herb_detail_found(self):
        from fastapi.testclient import TestClient
        from app.main import app

        herb = _make_herb_row(name="枸杞")

        with patch("app.routers.herbs.get_herb_detail", new_callable=AsyncMock) as mock_detail:
            mock_detail.return_value = herb
            with patch("app.routers.herbs.get_db"):
                client = TestClient(app)
                response = client.get(f"/api/v1/herbs/{herb.id}")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["name"] == "枸杞"

    def test_herb_detail_not_found(self):
        from fastapi.testclient import TestClient
        from app.main import app

        with patch("app.routers.herbs.get_herb_detail", new_callable=AsyncMock) as mock_detail:
            mock_detail.return_value = None
            with patch("app.routers.herbs.get_db"):
                client = TestClient(app)
                response = client.get(f"/api/v1/herbs/{uuid.uuid4()}")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 404
        assert body["message"] == "中药信息不存在"


class TestDailyHerbEndpoint:
    """Validates: Requirement 2.2"""

    def test_daily_herb_found(self):
        from fastapi.testclient import TestClient
        from app.main import app

        herb = _make_herb_row(name="今日推荐")

        with patch("app.routers.herbs.get_daily_herb", new_callable=AsyncMock) as mock_daily:
            mock_daily.return_value = herb
            with patch("app.routers.herbs.get_db"):
                client = TestClient(app)
                response = client.get("/api/v1/herbs/daily")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["name"] == "今日推荐"

    def test_daily_herb_empty(self):
        from fastapi.testclient import TestClient
        from app.main import app

        with patch("app.routers.herbs.get_daily_herb", new_callable=AsyncMock) as mock_daily:
            mock_daily.return_value = None
            with patch("app.routers.herbs.get_db"):
                client = TestClient(app)
                response = client.get("/api/v1/herbs/daily")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 404
        assert body["message"] == "暂无推荐草本"

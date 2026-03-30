"""Unit tests for admin prompt template management API (Task 10.7).

Validates Requirements:
- 14.1: Three types of Prompt_Template editing (健康顾问, 科普助手, 科普内容生成)
- 14.2: Save new version and retain history when modifying templates
- 14.3: Use latest version of Prompt_Template in AI_Service calls
- 14.4: Test functionality — input test data and view AI output
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database import get_db
from app.routers.admin.prompts import router
from app.routers.admin.users import get_admin_user
from app.schemas.prompt import (
    VALID_PROMPT_TYPES,
    PromptTemplateResponse,
    PromptTemplateUpdate,
    PromptTestRequest,
    PromptTestResponse,
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


def _make_template(**overrides) -> MagicMock:
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=uuid.uuid4(),
        type="health_advisor",
        role_name="健康顾问",
        content="你是一个健康顾问",
        version=1,
        is_active=True,
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


class TestPromptSchemas:
    """Validates: Requirement 14.1, 14.2, 14.4 — schema validation."""

    def test_template_response_valid(self):
        now = datetime.now(timezone.utc)
        resp = PromptTemplateResponse(
            id=uuid.uuid4(),
            type="health_advisor",
            role_name="健康顾问",
            content="你是健康顾问",
            version=1,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        assert resp.type == "health_advisor"
        assert resp.is_active is True

    def test_template_update_valid(self):
        body = PromptTemplateUpdate(content="新的模板内容")
        assert body.content == "新的模板内容"
        assert body.role_name is None

    def test_template_update_with_role_name(self):
        body = PromptTemplateUpdate(content="内容", role_name="新角色")
        assert body.role_name == "新角色"

    def test_template_update_empty_content_raises(self):
        with pytest.raises(Exception):
            PromptTemplateUpdate(content="")

    def test_test_request_valid(self):
        req = PromptTestRequest(type="health_advisor", test_input="测试输入")
        assert req.type == "health_advisor"

    def test_test_request_invalid_type_raises(self):
        with pytest.raises(Exception):
            PromptTestRequest(type="invalid_type", test_input="测试")

    def test_test_request_empty_input_raises(self):
        with pytest.raises(Exception):
            PromptTestRequest(type="health_advisor", test_input="")

    def test_test_response_valid(self):
        resp = PromptTestResponse(
            type="health_advisor",
            test_input="测试",
            ai_output="AI 输出结果",
        )
        assert resp.ai_output == "AI 输出结果"

    def test_valid_prompt_types(self):
        assert "health_advisor" in VALID_PROMPT_TYPES
        assert "pairing_assistant" in VALID_PROMPT_TYPES
        assert "content_generator" in VALID_PROMPT_TYPES


# ---------------------------------------------------------------------------
# 2. List prompts endpoint tests
# ---------------------------------------------------------------------------


class TestListPromptsEndpoint:
    """Validates: Requirement 14.1 — list prompt templates with optional type filter."""

    def test_list_prompts_success(self):
        admin = _make_admin_user()
        t1 = _make_template(type="health_advisor", version=1)
        t2 = _make_template(type="pairing_assistant", version=1)

        count_result = MagicMock()
        count_result.scalar_one.return_value = 2

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [t1, t2]

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.get("/api/v1/admin/prompts")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 2
        assert len(body["data"]["items"]) == 2

    def test_list_prompts_with_type_filter(self):
        admin = _make_admin_user()
        t1 = _make_template(type="health_advisor")

        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [t1]

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.get("/api/v1/admin/prompts?type=health_advisor")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 1

    def test_list_prompts_empty(self):
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
        response = client.get("/api/v1/admin/prompts")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 0
        assert body["data"]["items"] == []

    def test_list_prompts_page_size_exceeds_max_returns_422(self):
        admin = _make_admin_user()
        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin

        client = TestClient(app)
        response = client.get("/api/v1/admin/prompts?page_size=21")
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# 3. Get active prompt endpoint tests
# ---------------------------------------------------------------------------


class TestGetActivePromptEndpoint:
    """Validates: Requirement 14.3 — get the active template for a given type."""

    def test_get_active_prompt_success(self):
        admin = _make_admin_user()
        template = _make_template(type="health_advisor", is_active=True, version=3)

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = template

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=select_result)

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.get("/api/v1/admin/prompts/health_advisor/active")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["type"] == "health_advisor"
        assert body["data"]["version"] == 3

    def test_get_active_prompt_not_found(self):
        admin = _make_admin_user()

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = None

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=select_result)

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.get("/api/v1/admin/prompts/health_advisor/active")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 404
        assert "未找到" in body["message"]

    def test_get_active_prompt_invalid_type(self):
        admin = _make_admin_user()
        mock_db = AsyncMock()

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.get("/api/v1/admin/prompts/invalid_type/active")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 400
        assert "无效" in body["message"]


# ---------------------------------------------------------------------------
# 4. Update prompt endpoint tests
# ---------------------------------------------------------------------------


class TestUpdatePromptEndpoint:
    """Validates: Requirement 14.2 — update creates new version, deactivates previous."""

    def test_update_prompt_creates_new_version(self):
        admin = _make_admin_user()
        current = _make_template(type="health_advisor", version=2, is_active=True)

        # First call: find current active template
        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = current

        # Second call: deactivate old templates (update)
        update_result = MagicMock()

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[select_result, update_result])
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()
        mock_db.refresh = AsyncMock()

        # After refresh, the new template should have the new values
        async def mock_refresh(obj):
            obj.id = uuid.uuid4()
            obj.created_at = datetime.now(timezone.utc)
            obj.updated_at = datetime.now(timezone.utc)

        mock_db.refresh = AsyncMock(side_effect=mock_refresh)

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.put(
            "/api/v1/admin/prompts/health_advisor",
            json={"content": "新版本模板内容"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["message"] == "模板已更新"
        assert body["data"]["version"] == 3
        assert body["data"]["is_active"] is True
        assert body["data"]["content"] == "新版本模板内容"
        # Verify db.add was called (new template created)
        mock_db.add.assert_called_once()

    def test_update_prompt_first_version(self):
        admin = _make_admin_user()

        # No existing template
        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = None

        update_result = MagicMock()

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[select_result, update_result])
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()

        async def mock_refresh(obj):
            obj.id = uuid.uuid4()
            obj.created_at = datetime.now(timezone.utc)
            obj.updated_at = datetime.now(timezone.utc)

        mock_db.refresh = AsyncMock(side_effect=mock_refresh)

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.put(
            "/api/v1/admin/prompts/health_advisor",
            json={"content": "第一版模板", "role_name": "健康顾问"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["version"] == 1
        assert body["data"]["role_name"] == "健康顾问"

    def test_update_prompt_invalid_type(self):
        admin = _make_admin_user()
        mock_db = AsyncMock()

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.put(
            "/api/v1/admin/prompts/invalid_type",
            json={"content": "内容"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 400

    def test_update_prompt_empty_content_returns_422(self):
        admin = _make_admin_user()
        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin

        client = TestClient(app)
        response = client.put(
            "/api/v1/admin/prompts/health_advisor",
            json={"content": ""},
        )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# 5. Get prompt history endpoint tests
# ---------------------------------------------------------------------------


class TestGetPromptHistoryEndpoint:
    """Validates: Requirement 14.2 — version history for a template type."""

    def test_get_history_success(self):
        admin = _make_admin_user()
        t1 = _make_template(type="health_advisor", version=2, is_active=True)
        t2 = _make_template(type="health_advisor", version=1, is_active=False)

        count_result = MagicMock()
        count_result.scalar_one.return_value = 2

        data_result = MagicMock()
        data_result.scalars.return_value.all.return_value = [t1, t2]

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(side_effect=[count_result, data_result])

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.get("/api/v1/admin/prompts/health_advisor/history")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 2
        assert len(body["data"]["items"]) == 2

    def test_get_history_empty(self):
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
        response = client.get("/api/v1/admin/prompts/health_advisor/history")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 0

    def test_get_history_invalid_type(self):
        admin = _make_admin_user()
        mock_db = AsyncMock()

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.get("/api/v1/admin/prompts/bad_type/history")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 400


# ---------------------------------------------------------------------------
# 6. Test prompt endpoint tests
# ---------------------------------------------------------------------------


class TestTestPromptEndpoint:
    """Validates: Requirement 14.4 — test prompt with test input and view AI output."""

    @patch("app.routers.admin.prompts.AIAdapterFactory")
    def test_test_prompt_success(self, mock_factory):
        admin = _make_admin_user()
        template = _make_template(type="health_advisor", content="你是健康顾问")

        mock_adapter = AsyncMock()
        mock_adapter.generate.return_value = "AI 测试输出结果"
        mock_factory.create.return_value = mock_adapter

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = template

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=select_result)

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.post(
            "/api/v1/admin/prompts/test",
            json={"type": "health_advisor", "test_input": "我头痛怎么办"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["type"] == "health_advisor"
        assert body["data"]["test_input"] == "我头痛怎么办"
        assert body["data"]["ai_output"] == "AI 测试输出结果"
        mock_adapter.generate.assert_awaited_once()

    def test_test_prompt_no_active_template(self):
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
            "/api/v1/admin/prompts/test",
            json={"type": "health_advisor", "test_input": "测试"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 404
        assert "未找到" in body["message"]

    @patch("app.routers.admin.prompts.AIAdapterFactory")
    def test_test_prompt_ai_failure(self, mock_factory):
        admin = _make_admin_user()
        template = _make_template(type="health_advisor", content="你是健康顾问")

        mock_adapter = AsyncMock()
        mock_adapter.generate.side_effect = RuntimeError("AI service down")
        mock_factory.create.return_value = mock_adapter

        select_result = MagicMock()
        select_result.scalar_one_or_none.return_value = template

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=select_result)

        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin
        app.dependency_overrides[get_db] = lambda: mock_db

        client = TestClient(app)
        response = client.post(
            "/api/v1/admin/prompts/test",
            json={"type": "health_advisor", "test_input": "测试"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 500
        assert "AI 服务" in body["message"]

    def test_test_prompt_invalid_type_returns_422(self):
        admin = _make_admin_user()
        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin

        client = TestClient(app)
        response = client.post(
            "/api/v1/admin/prompts/test",
            json={"type": "invalid_type", "test_input": "测试"},
        )
        assert response.status_code == 422

    def test_test_prompt_empty_input_returns_422(self):
        admin = _make_admin_user()
        app = _create_test_app()
        app.dependency_overrides[get_admin_user] = lambda: admin

        client = TestClient(app)
        response = client.post(
            "/api/v1/admin/prompts/test",
            json={"type": "health_advisor", "test_input": ""},
        )
        assert response.status_code == 422

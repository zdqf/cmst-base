"""Tests for FastAPI project structure and configuration (Task 1.1)."""

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import ApiResponse, app, create_app


class TestSettings:
    """Test Pydantic Settings configuration."""

    def test_default_settings(self):
        s = Settings(
            database_url="postgresql+asyncpg://localhost/test",
            jwt_secret_key="test-secret",
        )
        assert s.app_name == "草木沈塘"
        assert s.jwt_algorithm == "HS256"
        assert s.jwt_expire_days == 7
        assert s.ai_provider == "openai"
        assert s.cors_origins == ["*"]

    def test_settings_fields_exist(self):
        s = Settings(
            database_url="postgresql+asyncpg://localhost/test",
            jwt_secret_key="test-secret",
        )
        # Verify all required config fields are present
        assert hasattr(s, "database_url")
        assert hasattr(s, "jwt_secret_key")
        assert hasattr(s, "jwt_algorithm")
        assert hasattr(s, "jwt_expire_days")
        assert hasattr(s, "ai_provider")
        assert hasattr(s, "openai_api_key")
        assert hasattr(s, "openai_model")
        assert hasattr(s, "private_model_endpoint")
        assert hasattr(s, "private_model_api_key")


class TestApiResponse:
    """Test unified API response format (Requirement 18.5)."""

    def test_default_response(self):
        resp = ApiResponse()
        assert resp.code == 0
        assert resp.message == "success"
        assert resp.data is None

    def test_success_response_with_data(self):
        resp = ApiResponse(data={"id": "123"})
        assert resp.code == 0
        assert resp.data == {"id": "123"}

    def test_error_response(self):
        resp = ApiResponse(code=400, message="请求参数错误")
        assert resp.code == 400
        assert resp.message == "请求参数错误"
        assert resp.data is None

    def test_response_serialization(self):
        resp = ApiResponse(code=0, message="success", data={"key": "value"})
        d = resp.model_dump()
        assert d == {"code": 0, "message": "success", "data": {"key": "value"}}


class TestFastAPIApp:
    """Test FastAPI application setup."""

    def test_app_creation(self):
        test_app = create_app()
        assert test_app.title == "草木沈塘"

    def test_cors_middleware_registered(self):
        test_app = create_app()
        middleware_classes = [m.cls.__name__ for m in test_app.user_middleware]
        assert "CORSMiddleware" in middleware_classes

    def test_health_endpoint(self):
        client = TestClient(app)
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["message"] == "success"
        assert body["data"]["status"] == "ok"

    def test_user_facing_routers_registered(self):
        """Verify all user-facing routers are registered with correct prefixes."""
        test_app = create_app()
        routes = [route.path for route in test_app.routes]
        user_prefixes = [
            "/api/v1/auth/",
            "/api/v1/herbs",
            "/api/v1/ai/",
            "/api/v1/consultations",
            "/api/v1/products",
            "/api/v1/cart",
            "/api/v1/orders",
        ]
        for prefix in user_prefixes:
            assert any(prefix in r for r in routes), f"No route found with prefix {prefix}"

    def test_admin_routers_registered(self):
        """Verify all admin routers are registered with correct prefixes."""
        test_app = create_app()
        routes = [route.path for route in test_app.routes]
        admin_prefixes = [
            "/api/v1/admin/users",
            "/api/v1/admin/consultations",
            "/api/v1/admin/diagnosis-logs",
            "/api/v1/admin/herbs",
            "/api/v1/admin/products",
            "/api/v1/admin/orders",
            "/api/v1/admin/prompts",
            "/api/v1/admin/compliance",
        ]
        for prefix in admin_prefixes:
            assert any(prefix in r for r in routes), f"No route found with prefix {prefix}"


class TestDatabaseModule:
    """Test database module structure."""

    def test_base_class_exists(self):
        from app.database import Base
        assert Base is not None

    def test_engine_exists(self):
        from app.database import engine
        assert engine is not None

    def test_session_factory_exists(self):
        from app.database import async_session_factory
        assert async_session_factory is not None

    def test_get_db_is_async_generator(self):
        import inspect
        from app.database import get_db
        assert inspect.isasyncgenfunction(get_db)

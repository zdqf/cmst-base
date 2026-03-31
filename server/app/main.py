"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.exceptions import AppException
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.redis import close_redis, init_redis
from app.routers.admin.compliance import router as admin_compliance_router
from app.routers.admin.consultations import router as admin_consultations_router
from app.routers.admin.diagnosis_logs import router as admin_diagnosis_logs_router
from app.routers.admin.herbs import router as admin_herbs_router
from app.routers.admin.orders import router as admin_orders_router
from app.routers.admin.products import router as admin_products_router
from app.routers.admin.prompts import router as admin_prompts_router
from app.routers.admin.users import router as admin_users_router
from app.routers.ai import router as ai_router
from app.routers.auth import router as auth_router
from app.routers.cart import router as cart_router
from app.routers.consultations import router as consultations_router
from app.routers.herbs import router as herbs_router
from app.routers.orders import router as orders_router
from app.routers.products import router as products_router
from app.routers.payments import router as payments_router
from app.schemas.common import ApiResponse


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    @asynccontextmanager
    async def lifespan(application: FastAPI):  # noqa: ARG001
        await init_redis()
        yield
        await close_redis()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request logging middleware
    app.add_middleware(RequestLoggingMiddleware)

    # API rate limiting middleware
    app.add_middleware(RateLimitMiddleware)

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.code,
            content=ApiResponse(code=exc.code, message=exc.message).model_dump(),
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=ApiResponse(code=500, message="服务器内部错误").model_dump(),
        )

    @app.get("/api/v1/health")
    async def health_check() -> ApiResponse:
        return ApiResponse(data={"status": "ok"})

    # Register user-facing routers
    app.include_router(auth_router)
    app.include_router(herbs_router)
    app.include_router(ai_router)
    app.include_router(consultations_router)
    app.include_router(products_router)
    app.include_router(cart_router)
    app.include_router(orders_router)
    app.include_router(payments_router)

    # Register admin routers
    app.include_router(admin_users_router)
    app.include_router(admin_consultations_router)
    app.include_router(admin_diagnosis_logs_router)
    app.include_router(admin_herbs_router)
    app.include_router(admin_products_router)
    app.include_router(admin_orders_router)
    app.include_router(admin_prompts_router)
    app.include_router(admin_compliance_router)

    return app


app = create_app()

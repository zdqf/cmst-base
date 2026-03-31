"""Authentication router — register and login endpoints.

Requirements:
- 1.1: POST /api/v1/auth/register — create user, return token
- 1.2: POST /api/v1/auth/login — verify credentials, return token
- 1.3: Invalid verification code → error response
- 1.4: Duplicate phone → "该手机号已注册"
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import AdminLoginRequest, LoginRequest, RegisterRequest, SendSMSRequest, TokenResponse
from app.schemas.common import ApiResponse
from app.services.auth_service import admin_login, login_user, register_user
from app.services.sms_service import send_sms_code

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


@router.post("/register", response_model=ApiResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)) -> ApiResponse:
    """Register a new user with phone and SMS verification code."""
    user, token = await register_user(db, req.phone, req.code)
    return ApiResponse(
        data=TokenResponse(access_token=token).model_dump(),
    )


@router.post("/login", response_model=ApiResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)) -> ApiResponse:
    """Login with phone and SMS verification code."""
    user, token = await login_user(db, req.phone, req.code)
    return ApiResponse(
        data=TokenResponse(access_token=token).model_dump(),
    )


@router.post("/sms/send", response_model=ApiResponse)
async def send_sms(req: SendSMSRequest) -> ApiResponse:
    """发送短信验证码 — 无需认证。

    Requirements:
    - 3.1: Generate and send 6-digit code to valid phone
    - 3.8: Phone format validation ^1[3-9]\\d{9}$

    Errors (AppException, RateLimitError) are caught by the global exception handler.
    """
    await send_sms_code(req.phone)
    return ApiResponse(message="验证码已发送")


@router.post("/admin/login", response_model=ApiResponse)
async def admin_login_endpoint(
    req: AdminLoginRequest, db: AsyncSession = Depends(get_db)
) -> ApiResponse:
    """Admin password login — no authentication required.

    Requirements:
    - 1.1: Validate password and return JWT with user_id, role="admin"
    - 1.2: Wrong password returns "手机号或密码错误"
    - 1.3: Non-admin users rejected
    - 1.7: Phone format validation
    """
    user, token = await admin_login(db, req.phone, req.password)
    return ApiResponse(
        data=TokenResponse(access_token=token).model_dump(),
    )

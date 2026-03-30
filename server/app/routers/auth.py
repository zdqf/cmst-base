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
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.common import ApiResponse
from app.services.auth_service import login_user, register_user

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


@router.post("/register", response_model=ApiResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)) -> ApiResponse:
    """Register a new user with phone and SMS verification code."""
    try:
        user, token = await register_user(db, req.phone, req.code)
        return ApiResponse(
            data=TokenResponse(access_token=token).model_dump(),
        )
    except ValueError as e:
        return ApiResponse(code=400, message=str(e))


@router.post("/login", response_model=ApiResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)) -> ApiResponse:
    """Login with phone and SMS verification code."""
    try:
        user, token = await login_user(db, req.phone, req.code)
        return ApiResponse(
            data=TokenResponse(access_token=token).model_dump(),
        )
    except ValueError as e:
        return ApiResponse(code=400, message=str(e))

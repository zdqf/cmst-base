"""Authentication request/response Pydantic models.

Requirements:
- 1.1: Register with phone + verification code, return auth token
- 1.2: Login with valid credentials, return auth token
- 1.3: Invalid verification code returns error
- 1.4: Duplicate phone returns "该手机号已注册"
"""

import re

from pydantic import BaseModel, Field, field_validator


def _validate_phone(v: str) -> str:
    """Validate Chinese mobile phone number format."""
    if not re.match(r"^1[3-9]\d{9}$", v):
        raise ValueError("手机号格式不正确")
    return v


class RegisterRequest(BaseModel):
    """Registration request: phone number + SMS verification code."""

    phone: str = Field(..., description="手机号")
    code: str = Field(..., description="短信验证码")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return _validate_phone(v)


class LoginRequest(BaseModel):
    """Login request: phone number + SMS verification code."""

    phone: str = Field(..., description="手机号")
    code: str = Field(..., description="短信验证码")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return _validate_phone(v)


class TokenResponse(BaseModel):
    """Authentication token response."""

    access_token: str = Field(..., description="JWT 访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")

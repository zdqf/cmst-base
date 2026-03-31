"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "草木沈塘"
    app_version: str = "0.1.0"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/caomushentang"

    # JWT
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_days: int = 7

    # AI Configuration
    ai_provider: str = "openai"  # "openai" or "private"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    private_model_endpoint: str = ""
    private_model_api_key: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # CORS
    cors_origins: list[str] = ["*"]

    # SMS Provider
    sms_provider: str = "mock"  # "aliyun" or "mock"
    aliyun_access_key_id: str = ""
    aliyun_access_key_secret: str = ""
    aliyun_sms_sign_name: str = "草木沈塘"
    aliyun_sms_template_code: str = ""

    # SMS Limits
    sms_code_ttl: int = 300       # verification code TTL (seconds)
    sms_rate_limit: int = 60      # send interval (seconds)
    sms_daily_limit: int = 10     # daily limit per phone number

    # Payment Provider
    payment_provider: str = "mock"  # "alipay" / "wechat" / "mock"

    # Alipay
    alipay_app_id: str = ""
    alipay_private_key: str = ""       # app private key (RSA2)
    alipay_public_key: str = ""        # alipay public key
    alipay_notify_url: str = ""        # async callback URL
    alipay_return_url: str = ""        # frontend redirect URL
    alipay_sandbox: bool = True        # sandbox mode

    # WeChat Pay
    wechat_app_id: str = ""
    wechat_mch_id: str = ""            # merchant ID
    wechat_api_key: str = ""           # API v3 key
    wechat_cert_serial_no: str = ""    # certificate serial number
    wechat_private_key: str = ""       # merchant private key
    wechat_notify_url: str = ""        # async callback URL


settings = Settings()

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

    # CORS
    cors_origins: list[str] = ["*"]

    # SMS (placeholder)
    sms_api_key: str = ""


settings = Settings()

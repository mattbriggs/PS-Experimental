"""Pydantic settings model for the Content Resource API.

All configuration is injected from environment variables.
Sensitive values use SecretStr and never appear in repr or validation output.
"""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Application
    environment: str = Field(default="development", description="Runtime environment name.")
    app_log_level: str = Field(default="info", description="Structured log level.")
    registry_path: str = Field(default="config/registry.yaml", description="Path to registry YAML.")
    filename_max_length: int = Field(
        default=200, gt=0, description="Maximum public filename length."
    )
    correlation_id_max_length: int = Field(
        default=128, gt=0, description="Maximum correlation ID length."
    )

    # WebDAV upstream
    webdav_base_url: str = Field(default="http://localhost:8180")
    webdav_username: str = Field(default="")
    webdav_password: SecretStr = Field(default=SecretStr(""))
    webdav_connect_timeout_seconds: float = Field(default=5.0, gt=0)
    webdav_read_timeout_seconds: float = Field(default=30.0, gt=0)
    webdav_max_retries: int = Field(default=3, ge=0)
    webdav_max_concurrency: int = Field(default=20, gt=0)

    # Authentication
    auth_api_key_enabled: bool = Field(default=True)

    # Operations
    readiness_requires_webdav: bool = Field(default=True)
    metrics_enabled: bool = Field(default=True)

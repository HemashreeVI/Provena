"""Typed application settings, loaded from environment variables and `.env`."""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache

from pydantic import Field, HttpUrl, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class LogFormat(StrEnum):
    CONSOLE = "console"
    JSON = "json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PROVENA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    env: Environment = Environment.DEVELOPMENT
    log_level: str = Field(default="INFO", pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    log_format: LogFormat = LogFormat.CONSOLE

    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)

    qdrant_url: HttpUrl = HttpUrl("http://localhost:6333")
    qdrant_api_key: SecretStr | None = None
    probe_timeout_s: float = Field(default=2.0, gt=0, le=30)

    @model_validator(mode="after")
    def _production_rules(self) -> Settings:
        if self.env is Environment.PRODUCTION and self.log_format is not LogFormat.JSON:
            raise ValueError("PROVENA_LOG_FORMAT must be 'json' in production")
        return self

    @property
    def is_production(self) -> bool:
        return self.env is Environment.PRODUCTION


@lru_cache
def get_settings() -> Settings:
    return Settings()

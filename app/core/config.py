from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "llm-gateway"
    environment: Literal["local", "dev", "test", "prod"] = "local"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    openai_api_key: str = Field(..., min_length=1)
    openai_model_chat: str = "gpt-4.1-mini"
    openai_model_summarize: str = "gpt-4.1-mini"

    openai_timeout_total_seconds: float = Field(30.0, gt=0)
    openai_timeout_connect_seconds: float = Field(2.0, gt=0)
    openai_timeout_read_seconds: float = Field(20.0, gt=0)
    openai_timeout_write_seconds: float = Field(10.0, gt=0)

    openai_max_retries: int = Field(2, ge=0, le=10)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="LLM_GATEWAY_",
        extra="ignore",
        case_sensitive=False
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
"""Application configuration using pydantic-settings."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[4]  # core/config.py -> sdwc_api -> src -> sdwc-api -> SDwC


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = ["*"]
    SDWC_RESOURCE_DIR: Path = _REPO_ROOT / ".sdwc"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

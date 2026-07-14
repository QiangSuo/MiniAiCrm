from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PROJECT_ROOT.parent


class Settings(BaseSettings):
    service_name: str = "xerp-demo"
    app_mode: str = "offline-demo"
    database_path: Path = Field(default=PROJECT_ROOT / "data" / "demo.db")
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    openai_model: str | None = None

    model_config = SettingsConfigDict(
        env_file=(REPOSITORY_ROOT / ".env", PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

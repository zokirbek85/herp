"""Ilova konfiguratsiyasi. Muhit o'zgaruvchilari yoki .env fayl orqali boshqariladi (prefix: HAZORASP_)."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.utils.paths import get_app_data_dir


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="HAZORASP_", env_file=".env", extra="ignore")

    app_name: str = "Hazorasp Sales Management"
    app_version: str = "0.1.0"

    database_path: Path = get_app_data_dir() / "sales.duckdb"
    echo_sql: bool = False

    theme: str = "light"
    language: str = "uz"

    @property
    def database_url(self) -> str:
        return f"duckdb:///{self.database_path}"


@lru_cache
def get_settings() -> Settings:
    """Settings'ni jarayon davomida bitta marta yaratadi (cache)."""
    return Settings()

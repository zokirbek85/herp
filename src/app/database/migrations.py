"""Alembic uchun DuckDB dialect support va dastur ishga tushganda avtomatik migration.

`duckdb_engine` Alembic uchun DDL implementation taqdim etmaydi, shuning uchun DuckDB SQL
sintaksisi PostgreSQL'ga juda yaqin bo'lgani uchun shu asosda minimal impl ro'yxatdan o'tkaziladi.
Bu modul Alembic chaqirilishidan oldin (CLI yoki runtime'da) albatta import qilinishi kerak.
"""

from alembic.ddl.impl import DefaultImpl


class DuckDBImpl(DefaultImpl):
    __dialect__ = "duckdb"


def run_upgrade_to_head() -> None:
    """Dastur ishga tushganda lokal DuckDB faylini eng so'nggi migration darajasiga olib chiqadi."""
    from pathlib import Path

    from alembic import command
    from alembic.config import Config

    from app.config.settings import get_settings

    project_root = Path(__file__).resolve().parents[3]
    alembic_cfg = Config(str(project_root / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(project_root / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", get_settings().database_url)
    command.upgrade(alembic_cfg, "head")

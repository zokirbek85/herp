"""Test session boshlanishidan oldin alohida vaqtinchalik DuckDB fayliga yo'naltiradi."""

import os
import uuid
from pathlib import Path

_TEST_DB_DIR = Path(__file__).resolve().parent / "_tmp_test_db"
_TEST_DB_DIR.mkdir(exist_ok=True)
os.environ["HAZORASP_DATABASE_PATH"] = str(_TEST_DB_DIR / f"test_{uuid.uuid4().hex}.duckdb")
# Backup/sync/device-id kabi fayllar haqiqiy foydalanuvchi papkasini ifloslantirmasligi uchun.
os.environ["HAZORASP_APP_DATA_DIR"] = str(_TEST_DB_DIR / "app_data")

import pytest  # noqa: E402

from app.database.migrations import run_upgrade_to_head  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _migrated_test_database():
    run_upgrade_to_head()
    yield

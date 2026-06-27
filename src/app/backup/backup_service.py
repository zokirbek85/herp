"""Database backup va restore. Sinxronlashdan oldin avtomatik, shuningdek foydalanuvchi
tomonidan "Backup" bo'limidan qo'lda chaqiriladi."""

import shutil
from datetime import datetime, timezone
from pathlib import Path

from app.config.settings import get_settings
from app.database.engine import get_engine
from app.utils.paths import get_backup_dir

_BACKUP_FILE_PREFIX = "sales_"
_BACKUP_FILE_SUFFIX = ".duckdb"


def create_backup(*, label: str | None = None) -> Path:
    """Joriy DuckDB faylining nusxasini backup papkasiga oladi.

    Nusxalashdan oldin `CHECKPOINT` chaqirilib, barcha yozilmagan o'zgarishlar diskka
    tushiriladi — aks holda backup faylida oxirgi tranzaksiyalar yetishmasligi mumkin.
    """
    settings = get_settings()
    with get_engine().connect() as connection:
        connection.exec_driver_sql("CHECKPOINT")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    suffix = f"_{label}" if label else ""
    backup_path = get_backup_dir() / f"{_BACKUP_FILE_PREFIX}{timestamp}{suffix}{_BACKUP_FILE_SUFFIX}"
    shutil.copy2(settings.database_path, backup_path)
    return backup_path


def list_backups() -> list[Path]:
    pattern = f"{_BACKUP_FILE_PREFIX}*{_BACKUP_FILE_SUFFIX}"
    return sorted(get_backup_dir().glob(pattern), reverse=True)


def restore_backup(backup_path: Path) -> None:
    """Diqqat: bu operatsiya joriy database faylini to'liq almashtiradi — qaytarib bo'lmaydi
    (restore'dan oldin avtomatik backup olinmaydi, chunki aynan shu fayl tiklanmoqchi bo'lgan
    holatni buzib qo'yishi mumkin). Chaqiruvchi UI qatlami foydalanuvchidan tasdiq olishi shart.
    """
    settings = get_settings()
    get_engine().dispose()
    shutil.copy2(backup_path, settings.database_path)

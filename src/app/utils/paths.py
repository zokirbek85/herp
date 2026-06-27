"""Platformaga bog'liq fayl yo'llari (Windows/macOS) bilan ishlash uchun yordamchi funksiyalar."""

import os
import sys
from pathlib import Path

APP_DIR_NAME = "HazoraspSalesManagement"
_APP_DATA_DIR_ENV_VAR = "HAZORASP_APP_DATA_DIR"


def get_app_data_dir() -> Path:
    """Foydalanuvchi darajasidagi ilova ma'lumotlar papkasini qaytaradi (DB, backup, log, config uchun).

    `HAZORASP_APP_DATA_DIR` muhit o'zgaruvchisi orqali boshqacha papkaga yo'naltirish mumkin —
    bu testlarda haqiqiy foydalanuvchi papkasini ifloslantirmaslik uchun ishlatiladi.
    """
    override = os.environ.get(_APP_DATA_DIR_ENV_VAR)
    if override:
        app_dir = Path(override)
        app_dir.mkdir(parents=True, exist_ok=True)
        return app_dir

    if sys.platform == "win32":
        base = Path.home() / "AppData" / "Local"
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".local" / "share"

    app_dir = base / APP_DIR_NAME
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_backup_dir() -> Path:
    backup_dir = get_app_data_dir() / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def get_log_dir() -> Path:
    log_dir = get_app_data_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir

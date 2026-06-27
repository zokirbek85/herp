"""Foydalanuvchi runtime sozlamalari (masalan, tema) — `.env`dagi statik Settings'dan farqli
ravishda, UI orqali o'zgartirilib, qurilma darajasida saqlanadi."""

import json
from pathlib import Path

from app.utils.paths import get_app_data_dir

_PREFERENCES_FILE_NAME = "preferences.json"


def _preferences_path() -> Path:
    return get_app_data_dir() / _PREFERENCES_FILE_NAME


def _read_all() -> dict:
    path = _preferences_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_theme(default: str) -> str:
    return _read_all().get("theme", default)


def save_theme(theme: str) -> None:
    data = _read_all()
    data["theme"] = theme
    _preferences_path().write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

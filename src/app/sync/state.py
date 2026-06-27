"""Oxirgi muvaffaqiyatli eksport vaqtini saqlaydi — keyingi eksport faqat shu vaqtdan
keyingi o'zgarishlarni oladi ("incremental export")."""

import json
from datetime import datetime
from pathlib import Path

from app.utils.paths import get_app_data_dir

_STATE_FILE_NAME = "sync_state.json"


def _state_file_path() -> Path:
    return get_app_data_dir() / _STATE_FILE_NAME


def get_last_export_at() -> datetime | None:
    path = _state_file_path()
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    value = data.get("last_export_at")
    return datetime.fromisoformat(value) if value else None


def set_last_export_at(value: datetime) -> None:
    _state_file_path().write_text(json.dumps({"last_export_at": value.isoformat()}), encoding="utf-8")

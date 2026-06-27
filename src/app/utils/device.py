"""Har bir kompyuter uchun barqaror, noyob qurilma identifikatori (sinxronlashda ishlatiladi)."""

import uuid

from app.utils.paths import get_app_data_dir

_DEVICE_ID_FILE_NAME = "device_id.txt"


def get_device_id() -> str:
    device_file = get_app_data_dir() / _DEVICE_ID_FILE_NAME
    if device_file.exists():
        return device_file.read_text(encoding="utf-8").strip()

    device_id = uuid.uuid4().hex
    device_file.write_text(device_id, encoding="utf-8")
    return device_id

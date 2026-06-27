"""Sync UI/ViewModel uchun yuqori darajadagi kirish nuqtasi: backup, export, import."""

from datetime import datetime, timezone
from pathlib import Path

from app.backup.backup_service import create_backup
from app.sync.exporter import export_changes
from app.sync.importer import ImportResult, SyncConflict, import_changes, resolve_conflict
from app.sync.state import get_last_export_at, set_last_export_at
from app.utils.device import get_device_id

__all__ = ["ImportResult", "SyncConflict", "SyncService", "resolve_conflict"]


class SyncService:
    def export_changes(self, output_path: Path, *, full_export: bool = False) -> Path:
        """`full_export=True` — barcha ma'lumotlarni (yangi qurilma uchun), aks holda faqat
        oxirgi eksportdan keyingi o'zgarishlarni eksport qiladi."""
        since = None if full_export else get_last_export_at()
        export_started_at = datetime.now(timezone.utc)

        path = export_changes(output_path, device_id=get_device_id(), since=since)
        set_last_export_at(export_started_at)
        return path

    def import_changes(self, package_path: Path) -> ImportResult:
        """Import'dan oldin avtomatik backup oladi — agar merge kutilmagan natija bersa,
        foydalanuvchi oldingi holatga qaytishi mumkin."""
        create_backup(label="pre_sync")
        return import_changes(package_path, device_id=get_device_id())

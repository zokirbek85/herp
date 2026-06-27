"""Sinxronlash sahifasi uchun ViewModel: eksport, import va conflictlarni hal qilish."""

from pathlib import Path

from PySide6.QtCore import Signal

from app.sync.importer import ImportResult, SyncConflict, resolve_conflict
from app.sync.state import get_last_export_at
from app.sync.sync_service import SyncService
from app.viewmodels.base_viewmodel import BaseViewModel


class SyncViewModel(BaseViewModel):
    export_completed = Signal(Path)
    import_completed = Signal(object)

    def __init__(self, service: SyncService | None = None) -> None:
        super().__init__()
        self._service = service or SyncService()
        self.last_export_at = get_last_export_at()
        self.last_result: ImportResult | None = None

    def export_changes(self, output_path: Path, *, full_export: bool) -> bool:
        try:
            path = self._service.export_changes(output_path, full_export=full_export)
            self.last_export_at = get_last_export_at()
            self.export_completed.emit(path)
            return True
        except OSError as exc:
            self.error_occurred.emit(f"Eksport qilishda xatolik: {exc}")
            return False

    def import_changes(self, package_path: Path) -> bool:
        try:
            result = self._service.import_changes(package_path)
            self.last_result = result
            self.import_completed.emit(result)
            return True
        except (OSError, ValueError) as exc:
            self.error_occurred.emit(f"Import qilishda xatolik: {exc}")
            return False

    def resolve_conflict(self, conflict: SyncConflict, *, keep: str) -> bool:
        try:
            resolve_conflict(conflict, keep=keep)
            if self.last_result is not None:
                remaining = [c for c in self.last_result.conflicts if c is not conflict]
                self.last_result = ImportResult(
                    inserted=self.last_result.inserted,
                    updated=self.last_result.updated,
                    skipped=self.last_result.skipped,
                    conflicts=remaining,
                )
            return True
        except OSError as exc:
            self.error_occurred.emit(f"Conflictni hal qilishda xatolik: {exc}")
            return False

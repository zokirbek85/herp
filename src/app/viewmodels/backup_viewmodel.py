"""Backup sahifasi uchun ViewModel."""

from pathlib import Path

from PySide6.QtCore import Signal

from app.backup.backup_service import create_backup, list_backups, restore_backup
from app.viewmodels.base_viewmodel import BaseViewModel


class BackupViewModel(BaseViewModel):
    backups_changed = Signal(list)

    def __init__(self) -> None:
        super().__init__()
        self.backups: list[Path] = []

    def load(self) -> None:
        def action() -> None:
            self.backups = list_backups()
            self.backups_changed.emit(list(self.backups))

        self.run_safely(action)

    def create(self) -> bool:
        try:
            create_backup(label="manual")
            self.load()
            return True
        except OSError as exc:
            self.error_occurred.emit(f"Backup olishda xatolik: {exc}")
            return False

    def restore(self, backup_path: Path) -> bool:
        try:
            restore_backup(backup_path)
            return True
        except OSError as exc:
            self.error_occurred.emit(f"Tiklashda xatolik: {exc}")
            return False

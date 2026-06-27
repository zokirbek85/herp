"""Sozlamalar: ilova haqida ma'lumot, fayl yo'llari va ma'lumotlar papkasiga tezkor kirish."""

import os
import sys
from pathlib import Path

from PySide6.QtWidgets import QFormLayout, QFrame, QLabel, QPushButton, QVBoxLayout, QWidget

import qtawesome as qta

from app.config.settings import get_settings
from app.utils.device import get_device_id
from app.utils.paths import get_app_data_dir, get_backup_dir, get_log_dir


def _open_folder(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    if sys.platform == "win32":
        os.startfile(path)


class SettingsPage(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        settings = get_settings()

        card = QFrame()
        card.setObjectName("Card")
        form = QFormLayout(card)
        form.addRow("Dastur nomi", QLabel(settings.app_name))
        form.addRow("Versiya", QLabel(settings.app_version))
        form.addRow("Til", QLabel("O'zbek"))
        form.addRow("Qurilma identifikatori", QLabel(get_device_id()))

        for label, path in (
            ("Ma'lumotlar papkasi", get_app_data_dir()),
            ("Backup papkasi", get_backup_dir()),
            ("Log papkasi", get_log_dir()),
        ):
            open_button = QPushButton(" Papkani ochish")
            open_button.setIcon(qta.icon("fa5s.folder-open"))
            open_button.clicked.connect(lambda _checked=False, p=path: _open_folder(p))
            form.addRow(f"{label} ({path})", open_button)

        layout = QVBoxLayout(self)
        layout.addWidget(card)
        layout.addStretch()

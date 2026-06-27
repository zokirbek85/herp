"""Backup: zaxira nusxa olish va tiklash."""

from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

import qtawesome as qta

from app.viewmodels.backup_viewmodel import BackupViewModel


class BackupPage(QWidget):
    def __init__(self, view_model: BackupViewModel | None = None, parent=None) -> None:
        super().__init__(parent)
        self._view_model = view_model or BackupViewModel()
        self._view_model.backups_changed.connect(self._render_rows)
        self._view_model.error_occurred.connect(self._show_error)

        create_button = QPushButton(" Backup olish")
        create_button.setObjectName("PrimaryButton")
        create_button.setIcon(qta.icon("fa5s.save", color="#FFFFFF"))
        create_button.clicked.connect(self._on_create_clicked)

        restore_button = QPushButton(" Tanlangan nusxani tiklash")
        restore_button.setIcon(qta.icon("fa5s.undo"))
        restore_button.clicked.connect(self._on_restore_clicked)

        toolbar = QHBoxLayout()
        toolbar.addStretch()
        toolbar.addWidget(restore_button)
        toolbar.addWidget(create_button)

        self._table = QTableWidget(0, 1)
        self._table.setHorizontalHeaderLabels(("Backup fayli",))
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        layout = QVBoxLayout(self)
        layout.addLayout(toolbar)
        layout.addWidget(self._table)

        self._view_model.load()

    def _on_create_clicked(self) -> None:
        if self._view_model.create():
            QMessageBox.information(self, "Tayyor", "Backup muvaffaqiyatli yaratildi")

    def _on_restore_clicked(self) -> None:
        row = self._table.currentRow()
        if row < 0 or row >= len(self._view_model.backups):
            return
        backup_path = self._view_model.backups[row]
        confirm = QMessageBox.warning(
            self,
            "Diqqat",
            f"'{backup_path.name}' tiklansa, joriy ma'lumotlar ustidan yoziladi. "
            "Tiklashdan keyin dasturni qayta ishga tushirish kerak bo'ladi. Davom etasizmi?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes and self._view_model.restore(backup_path):
            QMessageBox.information(
                self, "Tayyor", "Ma'lumotlar tiklandi. Iltimos, dasturni qayta ishga tushiring."
            )

    def _render_rows(self, backups: list) -> None:
        self._table.setRowCount(len(backups))
        for row, backup_path in enumerate(backups):
            self._table.setItem(row, 0, QTableWidgetItem(backup_path.name))

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Xatolik", message)

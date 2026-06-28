"""Sinxronlash: o'zgarishlarni eksport/import qilish va conflictlarni hal qilish."""

from pathlib import Path

from PySide6.QtWidgets import (
    QButtonGroup,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

import qtawesome as qta

from app.sync.importer import SyncConflict
from app.viewmodels.sync_viewmodel import SyncViewModel

_CONFLICT_COLUMNS = ("Jadval", "UUID", "Lokal qiymat", "Kelgan qiymat", "Tanlov", "")


class SyncPage(QWidget):
    def __init__(self, view_model: SyncViewModel | None = None, parent=None) -> None:
        super().__init__(parent)
        self._view_model = view_model or SyncViewModel()
        self._view_model.export_completed.connect(self._on_export_completed)
        self._view_model.import_completed.connect(self._on_import_completed)
        self._view_model.error_occurred.connect(self._show_error)

        self._status_label = QLabel()
        self._update_status_label()

        export_changes_button = QPushButton(" O'zgarishlarni eksport qilish")
        export_changes_button.setObjectName("PrimaryButton")
        export_changes_button.setIcon(qta.icon("fa5s.upload", color="#FFFFFF"))
        export_changes_button.clicked.connect(lambda: self._on_export_clicked(full_export=False))

        export_full_button = QPushButton(" To'liq eksport (yangi qurilma uchun)")
        export_full_button.setIcon(qta.icon("fa5s.upload"))
        export_full_button.clicked.connect(lambda: self._on_export_clicked(full_export=True))

        import_button = QPushButton(" Import qilish")
        import_button.setIcon(qta.icon("fa5s.download"))
        import_button.clicked.connect(self._on_import_clicked)

        actions_row = QHBoxLayout()
        actions_row.addWidget(export_changes_button)
        actions_row.addWidget(export_full_button)
        actions_row.addWidget(import_button)
        actions_row.addStretch()

        self._result_label = QLabel()

        self._conflicts_table = QTableWidget(0, len(_CONFLICT_COLUMNS))
        self._conflicts_table.setHorizontalHeaderLabels(_CONFLICT_COLUMNS)
        self._conflicts_table.verticalHeader().setVisible(False)
        self._conflicts_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._conflicts_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self._conflicts_table.horizontalHeader().setStretchLastSection(True)
        self._conflicts_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._conflicts_table.verticalHeader().setDefaultSectionSize(40)

        layout = QVBoxLayout(self)
        layout.addWidget(self._status_label)
        layout.addLayout(actions_row)
        layout.addWidget(self._result_label)
        layout.addWidget(QLabel("Hal qilinmagan conflict'lar:"))
        layout.addWidget(self._conflicts_table)

    def _update_status_label(self) -> None:
        last = self._view_model.last_export_at
        text = f"Oxirgi eksport: {last.strftime('%d.%m.%Y %H:%M')}" if last else "Hali eksport qilinmagan"
        self._status_label.setText(text)

    def _on_export_clicked(self, *, full_export: bool) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Sync paketini saqlash", "export.sync", "*.sync")
        if not path:
            return
        self._view_model.export_changes(Path(path), full_export=full_export)

    def _on_export_completed(self, path: Path) -> None:
        self._update_status_label()
        QMessageBox.information(self, "Tayyor", f"Eksport qilindi: {path}")

    def _on_import_clicked(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Sync paketini tanlash", "", "*.sync")
        if not path:
            return
        self._view_model.import_changes(Path(path))

    def _on_import_completed(self, result) -> None:
        self._result_label.setText(
            f"Qo'shildi: {result.inserted}, Yangilandi: {result.updated}, "
            f"O'tkazildi: {result.skipped}, Conflict: {len(result.conflicts)}"
        )
        self._render_conflicts(result.conflicts)

    def _render_conflicts(self, conflicts: list[SyncConflict]) -> None:
        self._incoming_radios: list[QRadioButton] = []
        self._conflicts_table.setRowCount(len(conflicts))
        for row, conflict in enumerate(conflicts):
            self._conflicts_table.setItem(row, 0, QTableWidgetItem(conflict.table_name))
            self._conflicts_table.setItem(row, 1, QTableWidgetItem(conflict.record_uuid[:8]))
            self._conflicts_table.setItem(row, 2, QTableWidgetItem(str(conflict.local_data)))
            self._conflicts_table.setItem(row, 3, QTableWidgetItem(str(conflict.incoming_data)))

            choice_widget = QWidget()
            choice_layout = QHBoxLayout(choice_widget)
            choice_layout.setContentsMargins(0, 0, 0, 0)
            local_radio = QRadioButton("Lokal")
            incoming_radio = QRadioButton("Kelgan")
            local_radio.setChecked(True)
            group = QButtonGroup(choice_widget)
            group.addButton(local_radio)
            group.addButton(incoming_radio)
            choice_layout.addWidget(local_radio)
            choice_layout.addWidget(incoming_radio)
            self._incoming_radios.append(incoming_radio)
            self._conflicts_table.setCellWidget(row, 4, choice_widget)

            resolve_button = QPushButton("Hal qilish")
            resolve_button.clicked.connect(
                lambda _checked=False, c=conflict, r=incoming_radio: self._on_resolve_clicked(c, r)
            )
            self._conflicts_table.setCellWidget(row, 5, resolve_button)

    def _on_resolve_clicked(self, conflict: SyncConflict, incoming_radio: QRadioButton) -> None:
        keep = "incoming" if incoming_radio.isChecked() else "local"
        if self._view_model.resolve_conflict(conflict, keep=keep):
            result = self._view_model.last_result
            if result is not None:
                self._render_conflicts(result.conflicts)
                self._result_label.setText(
                    f"Qo'shildi: {result.inserted}, Yangilandi: {result.updated}, "
                    f"O'tkazildi: {result.skipped}, Conflict: {len(result.conflicts)}"
                )

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Xatolik", message)

"""Shartnomalar ro'yxati: yaratish va qatorni ikki marta bosib kartochkasini ochish."""

from PySide6.QtCore import Qt
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

from app.viewmodels.contract_list_viewmodel import ContractListViewModel, ContractRow
from app.views.dialogs.contract_detail_dialog import ContractDetailDialog
from app.views.dialogs.contract_form_dialog import ContractFormDialog

_COLUMNS = ("Shartnoma №", "Kontragent", "Valyuta", "Summa", "Status", "Qarz")
_AMOUNT_FORMAT = "{:,.2f}".format


class ContractsPage(QWidget):
    def __init__(self, view_model: ContractListViewModel | None = None, parent=None) -> None:
        super().__init__(parent)
        self._view_model = view_model or ContractListViewModel()
        self._view_model.rows_changed.connect(self._render_rows)
        self._view_model.error_occurred.connect(self._show_error)

        add_button = QPushButton(" Yangi shartnoma")
        add_button.setObjectName("PrimaryButton")
        add_button.setIcon(qta.icon("fa5s.plus", color="#FFFFFF"))
        add_button.clicked.connect(self._on_add_clicked)

        refresh_button = QPushButton(" Yangilash")
        refresh_button.setIcon(qta.icon("fa5s.sync"))
        refresh_button.clicked.connect(self._view_model.load)

        toolbar = QHBoxLayout()
        toolbar.addStretch()
        toolbar.addWidget(refresh_button)
        toolbar.addWidget(add_button)

        self._table = QTableWidget(0, len(_COLUMNS))
        self._table.setHorizontalHeaderLabels(_COLUMNS)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.doubleClicked.connect(self._on_row_double_clicked)

        layout = QVBoxLayout(self)
        layout.addLayout(toolbar)
        layout.addWidget(self._table)

        self._view_model.load()

    def _on_add_clicked(self) -> None:
        dialog = ContractFormDialog(parent=self)
        if dialog.exec():
            self._view_model.create(**dialog.values)

    def _on_row_double_clicked(self) -> None:
        row = self._selected_row()
        if row is None:
            return
        dialog = ContractDetailDialog(row.contract.id, parent=self)
        dialog.exec()
        self._view_model.load()

    def _selected_row(self) -> ContractRow | None:
        row = self._table.currentRow()
        if row < 0 or row >= len(self._view_model.rows):
            return None
        return self._view_model.rows[row]

    def _render_rows(self, rows: list[ContractRow]) -> None:
        self._table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            values = (
                row.contract.contract_number,
                row.contragent_name,
                row.contract.currency.value,
                _AMOUNT_FORMAT(row.contract.amount),
                row.contract.status.value,
                _AMOUNT_FORMAT(row.debt),
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column in (2, 4):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._table.setItem(row_index, column, item)

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Xatolik", message)

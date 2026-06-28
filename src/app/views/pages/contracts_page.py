"""Shartnomalar ro'yxati: yaratish va qatorni ikki marta bosib kartochkasini ochish."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

import qtawesome as qta

from app.core.enums import ContractStatus
from app.viewmodels.contract_list_viewmodel import ContractListViewModel, ContractRow
from app.views.dialogs.contract_detail_dialog import ContractDetailDialog
from app.views.dialogs.contract_form_dialog import ContractFormDialog
from app.widgets.status_badge import StatusBadge

_COLUMNS = ("Shartnoma №", "Kontragent", "Valyuta", "Summa", "Status", "Qarz", "")
_AMOUNT_FORMAT = "{:,.0f}".format
_DIMMED_COLOR = QColor("#9AA0A6")
_DEBT_COLOR = QColor("#E34948")


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

        page_title = QLabel("Shartnomalar")
        page_title.setObjectName("PageTitle")

        toolbar = QHBoxLayout()
        toolbar.addWidget(page_title)
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
        self._table.setColumnWidth(0, 130)
        self._table.setColumnWidth(2, 60)
        self._table.setColumnWidth(3, 130)
        self._table.setColumnWidth(4, 110)
        self._table.setColumnWidth(5, 130)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        self._table.verticalHeader().setDefaultSectionSize(38)
        self._table.setShowGrid(False)
        self._table.setFrameShape(QFrame.Shape.NoFrame)
        self._table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._table.horizontalHeader().setHighlightSections(False)
        self._table.setMouseTracking(True)
        self._table.doubleClicked.connect(self._on_row_double_clicked)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        content = QWidget()
        content.setObjectName("ContentArea")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 16, 20, 16)
        content_layout.setSpacing(12)
        content_layout.addLayout(toolbar)
        content_layout.addWidget(self._table)

        outer_layout.addWidget(content)

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
            contract = row.contract

            num_item = QTableWidgetItem(contract.contract_number)
            self._table.setItem(row_index, 0, num_item)

            self._table.setItem(row_index, 1, QTableWidgetItem(row.contragent_name))

            currency_item = QTableWidgetItem(contract.currency.value)
            currency_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row_index, 2, currency_item)

            amount_item = QTableWidgetItem(_AMOUNT_FORMAT(contract.amount))
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(row_index, 3, amount_item)

            badge = StatusBadge(contract.status)
            badge_wrapper = QWidget()
            badge_layout = QHBoxLayout(badge_wrapper)
            badge_layout.setContentsMargins(4, 2, 4, 2)
            badge_layout.addWidget(badge)
            badge_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setCellWidget(row_index, 4, badge_wrapper)

            if row.debt <= 0:
                debt_item = QTableWidgetItem("—")
                debt_item.setForeground(_DIMMED_COLOR)
            else:
                debt_item = QTableWidgetItem(_AMOUNT_FORMAT(row.debt))
                debt_item.setForeground(_DEBT_COLOR)
            debt_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(row_index, 5, debt_item)

            if contract.status == ContractStatus.CANCELLED:
                for column in range(self._table.columnCount()):
                    item = self._table.item(row_index, column)
                    if item:
                        item.setForeground(_DIMMED_COLOR)

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Xatolik", message)

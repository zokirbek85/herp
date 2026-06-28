"""Barcha shartnomalar bo'yicha Ortishlar ro'yxati."""

from PySide6.QtCore import Qt
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

from app.viewmodels.shipment_list_viewmodel import ShipmentListViewModel, ShipmentRow
from app.views.dialogs.shipment_form_dialog import ShipmentFormDialog

_COLUMNS = ("Ortish №", "Shartnoma №", "Sana", "Invoice", "TTN", "Summa")
_AMOUNT_FORMAT = "{:,.2f}".format


class ShipmentsPage(QWidget):
    def __init__(self, view_model: ShipmentListViewModel | None = None, parent=None) -> None:
        super().__init__(parent)
        self._view_model = view_model or ShipmentListViewModel()
        self._view_model.rows_changed.connect(self._render_rows)
        self._view_model.error_occurred.connect(self._show_error)

        add_button = QPushButton(" Yangi ortish")
        add_button.setObjectName("PrimaryButton")
        add_button.setIcon(qta.icon("fa5s.plus", color="#FFFFFF"))
        add_button.clicked.connect(self._on_add_clicked)

        refresh_button = QPushButton(" Yangilash")
        refresh_button.setIcon(qta.icon("fa5s.sync"))
        refresh_button.clicked.connect(self._view_model.load)

        page_title = QLabel("Ortishlar")
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
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setDefaultSectionSize(38)
        self._table.setShowGrid(False)
        self._table.setFrameShape(QFrame.Shape.NoFrame)
        self._table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._table.horizontalHeader().setHighlightSections(False)
        self._table.setMouseTracking(True)

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
        choices = self._view_model.contract_choices()
        if not choices:
            QMessageBox.information(self, "Diqqat", "Avval kamida bitta shartnoma yaratish kerak")
            return
        dialog = ShipmentFormDialog(parent=self, contract_choices=choices)
        if dialog.exec():
            self._view_model.create(**dialog.values)

    def _render_rows(self, rows: list[ShipmentRow]) -> None:
        self._table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            values = (
                row.shipment.shipment_number,
                row.contract_number,
                row.shipment.shipment_date.strftime("%d.%m.%Y"),
                row.shipment.invoice_number or "",
                row.shipment.ttn_number or "",
                _AMOUNT_FORMAT(row.total_amount),
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 2:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._table.setItem(row_index, column, item)

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Xatolik", message)

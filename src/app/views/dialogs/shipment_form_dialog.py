"""Yangi ortish (header + tarkib) yaratish uchun modal forma."""

from datetime import date
from decimal import Decimal

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
)

import qtawesome as qta

from app.config.theme import style_calendar_popup
from app.services.dto import ShipmentItemInput
from app.services.product_service import ProductService

_ITEM_COLUMNS = ("Mahsulot", "Lot", "Kg", "Narx")


class ShipmentFormDialog(QDialog):
    def __init__(self, parent=None, contract_choices: list[tuple[int, str]] | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Yangi ortish")
        self.setMinimumWidth(640)

        self._products = ProductService().list_all()

        self.contract_combo: QComboBox | None = None
        self.shipment_number_input = QLineEdit()
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        style_calendar_popup(self.date_input)
        self.invoice_input = QLineEdit()
        self.ttn_input = QLineEdit()

        header_form = QFormLayout()
        if contract_choices is not None:
            self.contract_combo = QComboBox()
            for contract_id, label in contract_choices:
                self.contract_combo.addItem(label, contract_id)
            header_form.addRow("Shartnoma*", self.contract_combo)
        header_form.addRow("Ortish raqami*", self.shipment_number_input)
        header_form.addRow("Sana*", self.date_input)
        header_form.addRow("Invoice", self.invoice_input)
        header_form.addRow("TTN", self.ttn_input)

        self.items_table = QTableWidget(0, len(_ITEM_COLUMNS))
        self.items_table.setHorizontalHeaderLabels(_ITEM_COLUMNS)
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.items_table.horizontalHeader().setStretchLastSection(True)
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.verticalHeader().setDefaultSectionSize(40)

        add_row_button = QPushButton(" Qator qo'shish")
        add_row_button.setIcon(qta.icon("fa5s.plus"))
        add_row_button.clicked.connect(self._add_item_row)

        remove_row_button = QPushButton(" Qatorni o'chirish")
        remove_row_button.setIcon(qta.icon("fa5s.minus"))
        remove_row_button.clicked.connect(self._remove_selected_row)

        items_toolbar = QHBoxLayout()
        items_toolbar.addWidget(QLabel("Mahsulotlar"))
        items_toolbar.addStretch()
        items_toolbar.addWidget(add_row_button)
        items_toolbar.addWidget(remove_row_button)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(header_form)
        layout.addLayout(items_toolbar)
        layout.addWidget(self.items_table)
        layout.addWidget(buttons)

        self._add_item_row()

    def _add_item_row(self) -> None:
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)

        product_combo = QComboBox()
        for product in self._products:
            product_combo.addItem(f"{product.name} ({product.unit})", product.id)
        self.items_table.setCellWidget(row, 0, product_combo)

        self.items_table.setCellWidget(row, 1, QLineEdit())

        kg_input = QDoubleSpinBox()
        kg_input.setRange(0.001, 10_000_000)
        kg_input.setDecimals(3)
        self.items_table.setCellWidget(row, 2, kg_input)

        price_input = QDoubleSpinBox()
        price_input.setRange(0.0001, 1_000_000)
        price_input.setDecimals(4)
        self.items_table.setCellWidget(row, 3, price_input)

    def _remove_selected_row(self) -> None:
        row = self.items_table.currentRow()
        if row >= 0:
            self.items_table.removeRow(row)

    def _on_accept(self) -> None:
        if not self.shipment_number_input.text().strip():
            return
        if self.contract_combo is not None and self.contract_combo.count() == 0:
            return
        if not self.items:
            return
        self.accept()

    @property
    def items(self) -> list[ShipmentItemInput]:
        items: list[ShipmentItemInput] = []
        for row in range(self.items_table.rowCount()):
            product_combo: QComboBox = self.items_table.cellWidget(row, 0)
            lot_input: QLineEdit = self.items_table.cellWidget(row, 1)
            kg_input: QDoubleSpinBox = self.items_table.cellWidget(row, 2)
            price_input: QDoubleSpinBox = self.items_table.cellWidget(row, 3)
            if kg_input.value() <= 0 or price_input.value() <= 0:
                continue
            items.append(
                ShipmentItemInput(
                    product_id=product_combo.currentData(),
                    kg=Decimal(str(kg_input.value())),
                    price=Decimal(str(price_input.value())),
                    lot_number=lot_input.text().strip() or None,
                )
            )
        return items

    @property
    def values(self) -> dict[str, object]:
        qdate = self.date_input.date()
        values: dict[str, object] = {
            "shipment_number": self.shipment_number_input.text().strip(),
            "shipment_date": date(qdate.year(), qdate.month(), qdate.day()),
            "invoice_number": self.invoice_input.text().strip() or None,
            "ttn_number": self.ttn_input.text().strip() or None,
            "items": self.items,
        }
        if self.contract_combo is not None:
            values["contract_id"] = self.contract_combo.currentData()
        return values

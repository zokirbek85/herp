"""Yangi to'lov qo'shish uchun modal forma."""

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
    QVBoxLayout,
)

from app.core.enums import PaymentType

_PAYMENT_TYPE_LABELS = {
    PaymentType.ADVANCE: "Avans",
    PaymentType.REGULAR: "Oddiy to'lov",
    PaymentType.OVERPAYMENT: "Ortiqcha to'lov",
}


class PaymentFormDialog(QDialog):
    def __init__(self, parent=None, contract_choices: list[tuple[int, str]] | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Yangi to'lov")
        self.setMinimumWidth(380)

        self.contract_combo: QComboBox | None = None
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 1_000_000_000)
        self.amount_input.setDecimals(2)
        self.amount_input.setValue(100.0)

        self.payment_type_combo = QComboBox()
        for payment_type, label in _PAYMENT_TYPE_LABELS.items():
            self.payment_type_combo.addItem(label, payment_type)

        form = QFormLayout()
        if contract_choices is not None:
            self.contract_combo = QComboBox()
            for contract_id, label in contract_choices:
                self.contract_combo.addItem(label, contract_id)
            form.addRow("Shartnoma*", self.contract_combo)
        form.addRow("Sana*", self.date_input)
        form.addRow("Summa*", self.amount_input)
        form.addRow("Turi*", self.payment_type_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    @property
    def values(self) -> dict[str, object]:
        qdate = self.date_input.date()
        values: dict[str, object] = {
            "payment_date": date(qdate.year(), qdate.month(), qdate.day()),
            "amount": Decimal(str(self.amount_input.value())),
            "payment_type": self.payment_type_combo.currentData(),
        }
        if self.contract_combo is not None:
            values["contract_id"] = self.contract_combo.currentData()
        return values

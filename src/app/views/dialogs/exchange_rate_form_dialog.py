"""Valyuta kursini kiritish/tahrirlash uchun modal forma."""

from datetime import date
from decimal import Decimal

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QVBoxLayout,
)

from app.config.theme import style_calendar_popup


class ExchangeRateFormDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Valyuta kursi")
        self.setMinimumWidth(360)

        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        style_calendar_popup(self.date_input)

        self.rate_input = QDoubleSpinBox()
        self.rate_input.setRange(0.0001, 1_000_000)
        self.rate_input.setDecimals(4)
        self.rate_input.setValue(12700.0)

        form = QFormLayout()
        form.addRow("Sana*", self.date_input)
        form.addRow("1 USD = ... UZS*", self.rate_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    @property
    def values(self) -> dict[str, object]:
        qdate = self.date_input.date()
        return {
            "rate_date": date(qdate.year(), qdate.month(), qdate.day()),
            "usd_to_uzs": Decimal(str(self.rate_input.value())),
        }

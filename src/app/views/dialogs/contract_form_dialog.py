"""Yangi shartnoma yaratish uchun modal forma."""

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
    QLineEdit,
    QVBoxLayout,
)

from app.config.theme import style_calendar_popup
from app.core.enums import Currency
from app.models.contract import Contract
from app.services.contragent_service import ContragentService


class ContractFormDialog(QDialog):
    def __init__(self, contract: Contract | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Shartnomani tahrirlash" if contract else "Yangi shartnoma")
        self.setMinimumWidth(420)

        self._contragents = ContragentService().list_all()

        self.contract_number_input = QLineEdit(contract.contract_number if contract else "")
        self.contragent_combo = QComboBox()
        for contragent in self._contragents:
            self.contragent_combo.addItem(contragent.name, contragent.id)
        if contract is not None:
            index = self.contragent_combo.findData(contract.contragent_id)
            if index >= 0:
                self.contragent_combo.setCurrentIndex(index)

        self.currency_combo = QComboBox()
        for currency in Currency:
            self.currency_combo.addItem(currency.value, currency)
        if contract is not None:
            index = self.currency_combo.findData(contract.currency)
            if index >= 0:
                self.currency_combo.setCurrentIndex(index)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 1_000_000_000_000)
        self.amount_input.setDecimals(2)
        self.amount_input.setValue(float(contract.amount) if contract else 1000.0)

        self.date_input = QDateEdit(
            QDate(contract.contract_date.year, contract.contract_date.month, contract.contract_date.day)
            if contract
            else QDate.currentDate()
        )
        self.date_input.setCalendarPopup(True)
        style_calendar_popup(self.date_input)

        self.notes_input = QLineEdit(contract.notes or "" if contract else "")

        form = QFormLayout()
        form.addRow("Shartnoma raqami*", self.contract_number_input)
        form.addRow("Kontragent*", self.contragent_combo)
        form.addRow("Valyuta*", self.currency_combo)
        form.addRow("Summa*", self.amount_input)
        form.addRow("Sana*", self.date_input)
        form.addRow("Izoh", self.notes_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        if not self.contract_number_input.text().strip() or self.contragent_combo.count() == 0:
            return
        self.accept()

    @property
    def values(self) -> dict[str, object]:
        qdate = self.date_input.date()
        return {
            "contract_number": self.contract_number_input.text().strip(),
            "contragent_id": self.contragent_combo.currentData(),
            "currency": self.currency_combo.currentData(),
            "amount": Decimal(str(self.amount_input.value())),
            "contract_date": date(qdate.year(), qdate.month(), qdate.day()),
            "notes": self.notes_input.text().strip() or None,
        }

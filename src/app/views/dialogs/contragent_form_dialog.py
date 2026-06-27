"""Kontragent yaratish/tahrirlash uchun modal forma."""

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
)

from app.models.contragent import Contragent


class ContragentFormDialog(QDialog):
    def __init__(self, contragent: Contragent | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Kontragentni tahrirlash" if contragent else "Yangi kontragent")
        self.setMinimumWidth(420)

        self.name_input = QLineEdit(contragent.name if contragent else "")
        self.inn_input = QLineEdit(contragent.inn or "" if contragent else "")
        self.phone_input = QLineEdit(contragent.phone or "" if contragent else "")
        self.address_input = QLineEdit(contragent.address or "" if contragent else "")

        form = QFormLayout()
        form.addRow("Nomi*", self.name_input)
        form.addRow("INN", self.inn_input)
        form.addRow("Telefon", self.phone_input)
        form.addRow("Manzil", self.address_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        if not self.name_input.text().strip():
            self.name_input.setFocus()
            return
        self.accept()

    @property
    def values(self) -> dict[str, str | None]:
        return {
            "name": self.name_input.text().strip(),
            "inn": self.inn_input.text().strip() or None,
            "phone": self.phone_input.text().strip() or None,
            "address": self.address_input.text().strip() or None,
        }

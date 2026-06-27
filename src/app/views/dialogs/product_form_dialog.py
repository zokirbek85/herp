"""Mahsulot yaratish/tahrirlash uchun modal forma."""

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
)

from app.models.product import Product


class ProductFormDialog(QDialog):
    def __init__(self, product: Product | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Mahsulotni tahrirlash" if product else "Yangi mahsulot")
        self.setMinimumWidth(420)

        self.name_input = QLineEdit(product.name if product else "")
        self.sku_input = QLineEdit(product.sku or "" if product else "")
        self.unit_input = QLineEdit(product.unit if product else "kg")
        self.description_input = QLineEdit(product.description or "" if product else "")

        form = QFormLayout()
        form.addRow("Nomi*", self.name_input)
        form.addRow("SKU", self.sku_input)
        form.addRow("O'lchov birligi*", self.unit_input)
        form.addRow("Tavsif", self.description_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        if not self.name_input.text().strip() or not self.unit_input.text().strip():
            return
        self.accept()

    @property
    def values(self) -> dict[str, str | None]:
        return {
            "name": self.name_input.text().strip(),
            "sku": self.sku_input.text().strip() or None,
            "unit": self.unit_input.text().strip(),
            "description": self.description_input.text().strip() or None,
        }

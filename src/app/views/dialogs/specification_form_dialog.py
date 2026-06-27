"""Shartnoma spetsifikatsiyasiga mahsulot qo'shish uchun modal forma."""

from decimal import Decimal

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QVBoxLayout,
)

from app.services.product_service import ProductService


class SpecificationFormDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Spetsifikatsiyaga mahsulot qo'shish")
        self.setMinimumWidth(380)

        self.product_combo = QComboBox()
        for product in ProductService().list_all():
            self.product_combo.addItem(f"{product.name} ({product.unit})", product.id)

        self.planned_kg_input = QDoubleSpinBox()
        self.planned_kg_input.setRange(0.001, 10_000_000)
        self.planned_kg_input.setDecimals(3)
        self.planned_kg_input.setValue(100.0)

        self.reference_price_input = QDoubleSpinBox()
        self.reference_price_input.setRange(0.0001, 1_000_000)
        self.reference_price_input.setDecimals(4)
        self.reference_price_input.setValue(1.0)

        form = QFormLayout()
        form.addRow("Mahsulot*", self.product_combo)
        form.addRow("Rejalashtirilgan kg*", self.planned_kg_input)
        form.addRow("Mo'ljal narx*", self.reference_price_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        if self.product_combo.count() == 0:
            return
        self.accept()

    @property
    def values(self) -> dict[str, object]:
        return {
            "product_id": self.product_combo.currentData(),
            "planned_kg": Decimal(str(self.planned_kg_input.value())),
            "reference_price": Decimal(str(self.reference_price_input.value())),
        }

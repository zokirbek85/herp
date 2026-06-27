"""Mahsulotlar ro'yxati: qidiruv, qo'shish, tahrirlash, o'chirish."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

import qtawesome as qta

from app.models.product import Product
from app.viewmodels.product_list_viewmodel import ProductListViewModel
from app.views.dialogs.product_form_dialog import ProductFormDialog

_COLUMNS = ("Nomi", "SKU", "Birlik", "Tavsif", "Holati")


class ProductsPage(QWidget):
    def __init__(self, view_model: ProductListViewModel | None = None, parent=None) -> None:
        super().__init__(parent)
        self._view_model = view_model or ProductListViewModel()
        self._view_model.products_changed.connect(self._render_rows)
        self._view_model.error_occurred.connect(self._show_error)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Mahsulot nomi bo'yicha qidirish...")
        self._search_input.textChanged.connect(self._on_search_changed)

        add_button = QPushButton(" Yangi mahsulot")
        add_button.setObjectName("PrimaryButton")
        add_button.setIcon(qta.icon("fa5s.plus", color="#FFFFFF"))
        add_button.clicked.connect(self._on_add_clicked)

        edit_button = QPushButton(" Tahrirlash")
        edit_button.setIcon(qta.icon("fa5s.edit"))
        edit_button.clicked.connect(self._on_edit_clicked)

        delete_button = QPushButton(" O'chirish")
        delete_button.setIcon(qta.icon("fa5s.trash-alt"))
        delete_button.clicked.connect(self._on_delete_clicked)

        toolbar = QHBoxLayout()
        toolbar.addWidget(self._search_input, stretch=1)
        toolbar.addWidget(edit_button)
        toolbar.addWidget(delete_button)
        toolbar.addWidget(add_button)

        self._table = QTableWidget(0, len(_COLUMNS))
        self._table.setHorizontalHeaderLabels(_COLUMNS)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        layout = QVBoxLayout(self)
        layout.addLayout(toolbar)
        layout.addWidget(self._table)

        self._view_model.load()

    def _on_search_changed(self, text: str) -> None:
        self._view_model.load(text)

    def _on_add_clicked(self) -> None:
        dialog = ProductFormDialog(parent=self)
        if dialog.exec():
            self._view_model.create(**dialog.values)

    def _on_edit_clicked(self) -> None:
        product = self._selected_product()
        if product is None:
            return
        dialog = ProductFormDialog(product, parent=self)
        if dialog.exec():
            values = dialog.values
            self._view_model.update(
                product.id,
                name=values["name"],
                sku=values["sku"],
                unit=values["unit"],
                description=values["description"],
                is_active=product.is_active,
            )

    def _on_delete_clicked(self) -> None:
        product = self._selected_product()
        if product is None:
            return
        confirm = QMessageBox.question(
            self, "Tasdiqlash", f"'{product.name}' mahsulotini o'chirishni tasdiqlaysizmi?"
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self._view_model.delete(product.id)

    def _selected_product(self) -> Product | None:
        row = self._table.currentRow()
        if row < 0 or row >= len(self._view_model.products):
            return None
        return self._view_model.products[row]

    def _render_rows(self, products: list[Product]) -> None:
        self._table.setRowCount(len(products))
        for row, product in enumerate(products):
            values = (
                product.name,
                product.sku or "",
                product.unit,
                product.description or "",
                "Faol" if product.is_active else "Faol emas",
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 4:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._table.setItem(row, column, item)

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Xatolik", message)

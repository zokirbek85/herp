"""Valyuta kurslari: ro'yxat va sana bo'yicha kurs kiritish/tahrirlash."""

from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

import qtawesome as qta

from app.models.exchange_rate import ExchangeRate
from app.viewmodels.exchange_rate_list_viewmodel import ExchangeRateListViewModel
from app.views.dialogs.exchange_rate_form_dialog import ExchangeRateFormDialog

_COLUMNS = ("Sana", "1 USD = ... UZS")


class ExchangeRatesPage(QWidget):
    def __init__(self, view_model: ExchangeRateListViewModel | None = None, parent=None) -> None:
        super().__init__(parent)
        self._view_model = view_model or ExchangeRateListViewModel()
        self._view_model.rates_changed.connect(self._render_rows)
        self._view_model.error_occurred.connect(self._show_error)

        add_button = QPushButton(" Kurs kiritish")
        add_button.setObjectName("PrimaryButton")
        add_button.setIcon(qta.icon("fa5s.coins", color="#FFFFFF"))
        add_button.clicked.connect(self._on_add_clicked)

        toolbar = QHBoxLayout()
        toolbar.addStretch()
        toolbar.addWidget(add_button)

        self._table = QTableWidget(0, len(_COLUMNS))
        self._table.setHorizontalHeaderLabels(_COLUMNS)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        layout = QVBoxLayout(self)
        layout.addLayout(toolbar)
        layout.addWidget(self._table)

        self._view_model.load()

    def _on_add_clicked(self) -> None:
        dialog = ExchangeRateFormDialog(parent=self)
        if dialog.exec():
            self._view_model.upsert(**dialog.values)

    def _render_rows(self, rates: list[ExchangeRate]) -> None:
        self._table.setRowCount(len(rates))
        for row, rate in enumerate(rates):
            self._table.setItem(row, 0, QTableWidgetItem(rate.rate_date.strftime("%d.%m.%Y")))
            self._table.setItem(row, 1, QTableWidgetItem(f"{rate.usd_to_uzs:,.4f}"))

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Xatolik", message)

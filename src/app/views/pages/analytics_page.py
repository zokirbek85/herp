"""Analitika: TOP 10 qarzdorlar, TOP 10 kontragent, TOP 10 mahsulot."""

from PySide6.QtWidgets import (
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

from app.viewmodels.analytics_viewmodel import AnalyticsViewModel

_AMOUNT_FORMAT = "{:,.2f}".format


def _make_table(headers: tuple[str, ...]) -> QTableWidget:
    table = QTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setAlternatingRowColors(True)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    return table


class AnalyticsPage(QWidget):
    def __init__(self, view_model: AnalyticsViewModel | None = None, parent=None) -> None:
        super().__init__(parent)
        self._view_model = view_model or AnalyticsViewModel()
        self._view_model.data_changed.connect(self._render)
        self._view_model.error_occurred.connect(self._show_error)

        refresh_button = QPushButton(" Yangilash")
        refresh_button.setIcon(qta.icon("fa5s.sync"))
        refresh_button.clicked.connect(self._view_model.load)

        toolbar = QHBoxLayout()
        toolbar.addStretch()
        toolbar.addWidget(refresh_button)

        self._debtors_table = _make_table(("Kontragent", "INN", "Qarz"))
        self._top_contragents_table = _make_table(("Kontragent", "Sotuv hajmi"))
        self._top_products_table = _make_table(("Mahsulot", "Sotilgan kg"))

        tables_row = QHBoxLayout()
        tables_row.addLayout(self._labeled(("Eng katta qarzdorlar"), self._debtors_table))
        tables_row.addLayout(self._labeled(("TOP kontragentlar"), self._top_contragents_table))
        tables_row.addLayout(self._labeled(("TOP mahsulotlar"), self._top_products_table))

        layout = QVBoxLayout(self)
        layout.addLayout(toolbar)
        layout.addLayout(tables_row)

        self._view_model.load()

    def _labeled(self, title: str, table: QTableWidget) -> QVBoxLayout:
        column = QVBoxLayout()
        label = QLabel(title)
        label.setStyleSheet("font-weight: 600;")
        column.addWidget(label)
        column.addWidget(table)
        return column

    def _render(self) -> None:
        self._debtors_table.setRowCount(len(self._view_model.top_debtors))
        for row, item in enumerate(self._view_model.top_debtors):
            for column, value in enumerate(
                (item.contragent.name, item.contragent.inn or "", _AMOUNT_FORMAT(item.amount))
            ):
                self._debtors_table.setItem(row, column, QTableWidgetItem(value))

        self._top_contragents_table.setRowCount(len(self._view_model.top_contragents))
        for row, item in enumerate(self._view_model.top_contragents):
            for column, value in enumerate((item.contragent.name, _AMOUNT_FORMAT(item.amount))):
                self._top_contragents_table.setItem(row, column, QTableWidgetItem(value))

        self._top_products_table.setRowCount(len(self._view_model.top_products))
        for row, item in enumerate(self._view_model.top_products):
            for column, value in enumerate((item.product.name, f"{item.total_kg:,.3f}")):
                self._top_products_table.setItem(row, column, QTableWidgetItem(value))

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Xatolik", message)

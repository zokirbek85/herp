"""Shartnoma kartochkasi: moliyaviy xulosa + Spetsifikatsiya/Ortishlar/To'lovlar tablari."""

from decimal import Decimal

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

import qtawesome as qta

from app.models.payment import Payment
from app.models.shipment import Shipment
from app.services.shipment_service import ShipmentService
from app.viewmodels.contract_detail_viewmodel import ContractDetailViewModel
from app.views.dialogs.payment_form_dialog import PaymentFormDialog
from app.views.dialogs.shipment_form_dialog import ShipmentFormDialog
from app.views.dialogs.specification_form_dialog import SpecificationFormDialog
from app.widgets.kpi_card import KpiCard

_AMOUNT_FORMAT = "{:,.2f}".format


def _make_table(headers: tuple[str, ...]) -> QTableWidget:
    table = QTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setAlternatingRowColors(True)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
    table.horizontalHeader().setStretchLastSection(True)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
    return table


class ContractDetailDialog(QDialog):
    def __init__(self, contract_id: int, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumSize(900, 640)

        self._view_model = ContractDetailViewModel(contract_id)
        self._view_model.data_changed.connect(self._render)
        self._view_model.error_occurred.connect(self._show_error)

        self._summary_row = QHBoxLayout()
        self._kg_summary_label = QLabel()
        self._kg_summary_label.setStyleSheet("color: #5B6470; padding: 4px 0;")

        self._spec_table = _make_table(
            (
                "Mahsulot",
                "Rejalashtirilgan kg",
                "Yetkazilgan kg",
                "Qoldiq kg",
                "Bajarilish %",
                "Mo'ljal narx",
                "Summa",
            )
        )
        self._shipment_table = _make_table(("Ortish №", "Sana", "Invoice", "TTN", "Summa"))
        self._payment_table = _make_table(("Sana", "Summa", "Valyuta", "Turi"))

        add_spec_button = QPushButton(" Mahsulot qo'shish")
        add_spec_button.setIcon(qta.icon("fa5s.plus"))
        add_spec_button.clicked.connect(self._on_add_specification)
        spec_tab = self._build_tab(self._spec_table, add_spec_button)

        add_shipment_button = QPushButton(" Yangi ortish")
        add_shipment_button.setIcon(qta.icon("fa5s.plus"))
        add_shipment_button.clicked.connect(self._on_add_shipment)
        edit_shipment_button = QPushButton(" Tahrirlash")
        edit_shipment_button.setIcon(qta.icon("fa5s.edit"))
        edit_shipment_button.clicked.connect(self._on_edit_shipment)
        delete_shipment_button = QPushButton(" O'chirish")
        delete_shipment_button.setIcon(qta.icon("fa5s.trash-alt"))
        delete_shipment_button.clicked.connect(self._on_delete_shipment)
        shipment_tab = self._build_tab(
            self._shipment_table, edit_shipment_button, delete_shipment_button, add_shipment_button
        )

        add_payment_button = QPushButton(" Yangi to'lov")
        add_payment_button.setIcon(qta.icon("fa5s.plus"))
        add_payment_button.clicked.connect(self._on_add_payment)
        edit_payment_button = QPushButton(" Tahrirlash")
        edit_payment_button.setIcon(qta.icon("fa5s.edit"))
        edit_payment_button.clicked.connect(self._on_edit_payment)
        delete_payment_button = QPushButton(" O'chirish")
        delete_payment_button.setIcon(qta.icon("fa5s.trash-alt"))
        delete_payment_button.clicked.connect(self._on_delete_payment)
        payment_tab = self._build_tab(
            self._payment_table, edit_payment_button, delete_payment_button, add_payment_button
        )

        tabs = QTabWidget()
        tabs.addTab(spec_tab, "Spetsifikatsiya")
        tabs.addTab(shipment_tab, "Ortishlar")
        tabs.addTab(payment_tab, "To'lovlar")

        cancel_button = QPushButton(" Shartnomani bekor qilish")
        cancel_button.setIcon(qta.icon("fa5s.ban"))
        cancel_button.clicked.connect(self._on_cancel_contract)

        layout = QVBoxLayout(self)
        self._title_label = QLabel()
        self._title_label.setStyleSheet("font-size: 18px; font-weight: 700;")
        layout.addWidget(self._title_label)
        layout.addLayout(self._summary_row)
        layout.addWidget(self._kg_summary_label)
        layout.addWidget(tabs)
        footer = QHBoxLayout()
        footer.addStretch()
        footer.addWidget(cancel_button)
        layout.addLayout(footer)

        self._view_model.load()

    def _build_tab(self, table: QTableWidget, *buttons: QPushButton) -> QWidget:
        widget = QWidget()
        toolbar = QHBoxLayout()
        toolbar.addStretch()
        for button in buttons:
            toolbar.addWidget(button)
        tab_layout = QVBoxLayout(widget)
        tab_layout.addLayout(toolbar)
        tab_layout.addWidget(table)
        return widget

    def _render(self) -> None:
        contract = self._view_model.contract
        summary = self._view_model.summary
        self.setWindowTitle(f"Shartnoma {contract.contract_number}")
        self._title_label.setText(f"Shartnoma № {contract.contract_number} — {contract.status.value}")

        while self._summary_row.count():
            self._summary_row.takeAt(0).widget().deleteLater()
        for title, value in (
            ("Shartnoma summasi", summary.contract_amount),
            ("Yetkazilgan", summary.total_shipped),
            ("To'langan", summary.total_paid),
            ("Avans qoldig'i", summary.advance_balance),
            ("Qarz", summary.debt),
        ):
            self._summary_row.addWidget(KpiCard(title, f"{_AMOUNT_FORMAT(value)} {contract.currency.value}"))

        self._kg_summary_label.setText(
            f"Jami: {summary.total_planned_kg:,.3f} kg / "
            f"{summary.total_shipped_kg:,.3f} kg yetkazildi / "
            f"{summary.total_remaining_kg:,.3f} kg qoldi "
            f"({summary.kg_completion_pct:,.2f}%)"
        )

        spec_by_product = {spec.product_id: spec for spec in self._view_model.specifications}
        self._spec_table.setRowCount(len(summary.per_product))
        for row, product_summary in enumerate(summary.per_product):
            spec = spec_by_product.get(product_summary.product_id)
            values = (
                product_summary.product_name,
                f"{product_summary.planned_kg:,.3f}",
                f"{product_summary.shipped_kg:,.3f}",
                f"{product_summary.remaining_kg:,.3f}",
                f"{product_summary.completion_pct:,.2f}",
                f"{spec.reference_price:,.4f}" if spec is not None else "",
                _AMOUNT_FORMAT(spec.amount) if spec is not None else "",
            )
            for column, value in enumerate(values):
                self._spec_table.setItem(row, column, QTableWidgetItem(value))
        self._spec_table.resizeColumnsToContents()

        self._shipment_table.setRowCount(len(self._view_model.shipments))
        for row, shipment in enumerate(self._view_model.shipments):
            total = self._view_model.shipment_totals.get(shipment.id, Decimal("0"))
            values = (
                shipment.shipment_number,
                shipment.shipment_date.strftime("%d.%m.%Y"),
                shipment.invoice_number or "",
                shipment.ttn_number or "",
                _AMOUNT_FORMAT(total),
            )
            for column, value in enumerate(values):
                self._shipment_table.setItem(row, column, QTableWidgetItem(value))
        self._shipment_table.resizeColumnsToContents()

        self._payment_table.setRowCount(len(self._view_model.payments))
        for row, payment in enumerate(self._view_model.payments):
            values = (
                payment.payment_date.strftime("%d.%m.%Y"),
                _AMOUNT_FORMAT(payment.amount),
                payment.currency.value,
                payment.payment_type.value,
            )
            for column, value in enumerate(values):
                self._payment_table.setItem(row, column, QTableWidgetItem(value))
        self._payment_table.resizeColumnsToContents()

    def _on_add_specification(self) -> None:
        dialog = SpecificationFormDialog(parent=self)
        if dialog.exec():
            self._view_model.add_specification(**dialog.values)

    def _on_add_shipment(self) -> None:
        dialog = ShipmentFormDialog(parent=self)
        if dialog.exec():
            self._view_model.create_shipment(**dialog.values)

    def _on_edit_shipment(self) -> None:
        shipment = self._selected_shipment()
        if shipment is None:
            return
        items = ShipmentService().list_items(shipment.id)
        dialog = ShipmentFormDialog(shipment, parent=self, items=list(items))
        if dialog.exec():
            self._view_model.update_shipment(shipment.id, **dialog.values)

    def _on_delete_shipment(self) -> None:
        shipment = self._selected_shipment()
        if shipment is None:
            return
        confirm = QMessageBox.question(
            self, "Tasdiqlash", f"'{shipment.shipment_number}' ortishni o'chirishni tasdiqlaysizmi?"
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self._view_model.delete_shipment(shipment.id)

    def _selected_shipment(self) -> Shipment | None:
        row = self._shipment_table.currentRow()
        if row < 0 or row >= len(self._view_model.shipments):
            return None
        return self._view_model.shipments[row]

    def _on_add_payment(self) -> None:
        dialog = PaymentFormDialog(parent=self)
        if dialog.exec():
            self._view_model.create_payment(**dialog.values)

    def _on_edit_payment(self) -> None:
        payment = self._selected_payment()
        if payment is None:
            return
        dialog = PaymentFormDialog(payment, parent=self)
        if dialog.exec():
            self._view_model.update_payment(payment.id, **dialog.values)

    def _on_delete_payment(self) -> None:
        payment = self._selected_payment()
        if payment is None:
            return
        confirm = QMessageBox.question(
            self, "Tasdiqlash", "Tanlangan to'lovni o'chirishni tasdiqlaysizmi?"
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self._view_model.delete_payment(payment.id)

    def _selected_payment(self) -> Payment | None:
        row = self._payment_table.currentRow()
        if row < 0 or row >= len(self._view_model.payments):
            return None
        return self._view_model.payments[row]

    def _on_cancel_contract(self) -> None:
        confirm = QMessageBox.question(
            self, "Tasdiqlash", "Shartnomani bekor qilishni tasdiqlaysizmi?"
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self._view_model.cancel_contract()

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Xatolik", message)

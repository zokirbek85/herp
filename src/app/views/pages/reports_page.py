"""Hisobotlar: Shartnoma, Kontragent va Debitorlik hisobotlarini Excel/PDF/CSV'ga eksport qilish."""

import os
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

import qtawesome as qta

from app.reports.base_report import ReportTable
from app.reports.contract_report import build_contract_report
from app.reports.contragent_report import build_contragent_report
from app.reports.debt_report import build_top_debtors_report
from app.services.contract_service import ContractService
from app.services.contragent_service import ContragentService


def _open_file(path: Path) -> None:
    if sys.platform == "win32":
        os.startfile(path)


class _ReportCard(QFrame):
    def __init__(self, title: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 15px; font-weight: 700;")
        self.layout_ = QVBoxLayout(self)
        self.layout_.addWidget(self.title_label)


class ReportsPage(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.addWidget(self._build_contract_report_card())
        layout.addWidget(self._build_contragent_report_card())
        layout.addWidget(self._build_debt_report_card())
        layout.addStretch()

    def _build_contract_report_card(self) -> QFrame:
        card = _ReportCard("Shartnoma bo'yicha hisobot")
        self._contract_combo = QComboBox()
        for contract in ContractService().list_all():
            self._contract_combo.addItem(contract.contract_number, contract.id)

        form = QFormLayout()
        form.addRow("Shartnoma", self._contract_combo)
        card.layout_.addLayout(form)
        card.layout_.addLayout(
            self._export_buttons(lambda: build_contract_report(self._contract_combo.currentData()))
        )
        return card

    def _build_contragent_report_card(self) -> QFrame:
        card = _ReportCard("Kontragent bo'yicha hisobot")
        self._contragent_combo = QComboBox()
        for contragent in ContragentService().list_all():
            self._contragent_combo.addItem(contragent.name, contragent.id)

        form = QFormLayout()
        form.addRow("Kontragent", self._contragent_combo)
        card.layout_.addLayout(form)
        card.layout_.addLayout(
            self._export_buttons(lambda: build_contragent_report(self._contragent_combo.currentData()))
        )
        return card

    def _build_debt_report_card(self) -> QFrame:
        card = _ReportCard("Eng katta qarzdorlar")
        self._debt_limit_input = QSpinBox()
        self._debt_limit_input.setRange(1, 1000)
        self._debt_limit_input.setValue(10)

        form = QFormLayout()
        form.addRow("Soni (TOP)", self._debt_limit_input)
        card.layout_.addLayout(form)
        card.layout_.addLayout(
            self._export_buttons(lambda: build_top_debtors_report(limit=self._debt_limit_input.value()))
        )
        return card

    def _export_buttons(self, build_report) -> QHBoxLayout:
        row = QHBoxLayout()
        for label, icon, extension, method in (
            ("Excel", "fa5s.file-excel", "xlsx", "to_excel"),
            ("PDF", "fa5s.file-pdf", "pdf", "to_pdf"),
            ("CSV", "fa5s.file-csv", "csv", "to_csv"),
        ):
            button = QPushButton(f" {label}")
            button.setIcon(qta.icon(icon))
            button.clicked.connect(
                lambda _checked=False, ext=extension, m=method: self._export(build_report(), ext, m)
            )
            row.addWidget(button)
        row.addStretch()
        return row

    def _export(self, report: ReportTable, extension: str, method: str) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Hisobotni saqlash", f"{report.title}.{extension}", f"*.{extension}"
        )
        if not path:
            return
        saved_path = getattr(report, method)(Path(path))

        confirm = QMessageBox.question(
            self, "Tayyor", "Hisobot saqlandi. Faylni ochishni xohlaysizmi?"
        )
        if confirm == QMessageBox.StandardButton.Yes:
            _open_file(saved_path)

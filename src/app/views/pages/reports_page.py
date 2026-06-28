"""Hisobotlar: Shartnoma, Kontragent va Debitorlik hisobotlarini Excel/PDF/CSV'ga eksport qilish."""

from datetime import date
from pathlib import Path

from PySide6.QtCore import QDate, QUrl, Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

import qtawesome as qta

from app.config.theme import style_calendar_popup
from app.database.session import session_scope
from app.reports.aging_report import build_aging_report
from app.reports.base_report import ReportTable
from app.reports.contract_report import build_contract_report
from app.reports.contragent_report import build_contragent_report
from app.reports.debt_report import build_top_debtors_report
from app.reports.kg_debt_report import build_kg_debt_report
from app.services.aging_service import AgingService
from app.services.contract_service import ContractService
from app.services.contragent_service import ContragentService

_AMOUNT_FORMATTER = "{:,.2f}".format
_AGING_COLUMNS = ("Kontragent", "INN", "0-30 kun", "31-60 kun", "61-90 kun", "91+ kun", "Jami", "Eng qadimgi (kun)")


def _open_file(path: Path) -> None:
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))


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

        page_title = QLabel("Hisobotlar")
        page_title.setObjectName("PageTitle")

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        content = QWidget()
        content.setObjectName("ContentArea")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        layout.addWidget(page_title)
        layout.addWidget(self._build_contract_report_card())
        layout.addWidget(self._build_contragent_report_card())
        layout.addWidget(self._build_debt_report_card())
        layout.addWidget(self._build_kg_debt_report_card())
        layout.addWidget(self._build_aging_report_card())
        layout.addStretch()

        outer_layout.addWidget(content)

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

    def _build_kg_debt_report_card(self) -> QFrame:
        card = _ReportCard("Mahsulot (kg) qarzdorlik hisoboti")
        card.layout_.addLayout(self._export_buttons(build_kg_debt_report))
        return card

    def _build_aging_report_card(self) -> QFrame:
        card = _ReportCard("Aging tahlili (debitorlik yoshi)")

        self._aging_date_input = QDateEdit(QDate.currentDate())
        self._aging_date_input.setCalendarPopup(True)
        style_calendar_popup(self._aging_date_input)

        calculate_button = QPushButton(" Hisoblash")
        calculate_button.setIcon(qta.icon("fa5s.calculator"))
        calculate_button.clicked.connect(self._on_calculate_aging)

        form_row = QHBoxLayout()
        form_row.addWidget(QLabel("Sana bo'yicha"))
        form_row.addWidget(self._aging_date_input)
        form_row.addWidget(calculate_button)
        form_row.addStretch()
        card.layout_.addLayout(form_row)

        self._aging_table = QTableWidget(0, len(_AGING_COLUMNS))
        self._aging_table.setHorizontalHeaderLabels(_AGING_COLUMNS)
        self._aging_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._aging_table.horizontalHeader().setStretchLastSection(True)
        self._aging_table.verticalHeader().setVisible(False)
        self._aging_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._aging_table.verticalHeader().setDefaultSectionSize(38)
        self._aging_table.setShowGrid(False)
        self._aging_table.setFrameShape(QFrame.Shape.NoFrame)
        self._aging_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._aging_table.horizontalHeader().setHighlightSections(False)
        self._aging_table.setMouseTracking(True)
        card.layout_.addWidget(self._aging_table)

        card.layout_.addLayout(self._export_buttons(lambda: build_aging_report(self._aging_as_of())))
        return card

    def _aging_as_of(self) -> date:
        qdate = self._aging_date_input.date()
        return date(qdate.year(), qdate.month(), qdate.day())

    def _on_calculate_aging(self) -> None:
        with session_scope() as session:
            rows = AgingService(session).build(self._aging_as_of())

        self._aging_table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            values = (
                row.contragent_name,
                row.inn or "",
                _AMOUNT_FORMATTER(row.buckets[0].amount),
                _AMOUNT_FORMATTER(row.buckets[1].amount),
                _AMOUNT_FORMATTER(row.buckets[2].amount),
                _AMOUNT_FORMATTER(row.buckets[3].amount),
                _AMOUNT_FORMATTER(row.total_debt),
                str(row.oldest_invoice_days),
            )
            for column, value in enumerate(values):
                self._aging_table.setItem(row_index, column, QTableWidgetItem(value))

        self._aging_table.resizeColumnsToContents()

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

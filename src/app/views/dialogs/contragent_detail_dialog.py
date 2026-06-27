"""Kontragent kartochkasi: ma'lumotlari, shartnomalari va umumiy qarzi."""

from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

import qtawesome as qta

from app.reports.contragent_report import build_contragent_report
from app.viewmodels.contragent_detail_viewmodel import ContragentDetailViewModel
from app.widgets.kpi_card import KpiCard

_COLUMNS = ("Shartnoma №", "Sana", "Valyuta", "Summa", "Status", "Qarz")
_AMOUNT_FORMAT = "{:,.2f}".format


class ContragentDetailDialog(QDialog):
    def __init__(self, contragent_id: int, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumSize(800, 560)

        self._view_model = ContragentDetailViewModel(contragent_id)
        self._view_model.data_changed.connect(self._render)
        self._view_model.error_occurred.connect(self._show_error)

        self._title_label = QLabel()
        self._title_label.setStyleSheet("font-size: 18px; font-weight: 700;")
        self._info_label = QLabel()
        self._info_label.setStyleSheet("color: #5B6470;")

        self._summary_row = QHBoxLayout()

        self._table = QTableWidget(0, len(_COLUMNS))
        self._table.setHorizontalHeaderLabels(_COLUMNS)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        export_excel_button = QPushButton(" Excel'ga eksport")
        export_excel_button.setIcon(qta.icon("fa5s.file-excel"))
        export_excel_button.clicked.connect(lambda: self._export("excel"))

        export_pdf_button = QPushButton(" PDF'ga eksport")
        export_pdf_button.setIcon(qta.icon("fa5s.file-pdf"))
        export_pdf_button.clicked.connect(lambda: self._export("pdf"))

        footer = QHBoxLayout()
        footer.addStretch()
        footer.addWidget(export_excel_button)
        footer.addWidget(export_pdf_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self._title_label)
        layout.addWidget(self._info_label)
        layout.addLayout(self._summary_row)
        layout.addWidget(self._table)
        layout.addLayout(footer)

        self._view_model.load()

    def _render(self) -> None:
        contragent = self._view_model.contragent
        self.setWindowTitle(contragent.name)
        self._title_label.setText(contragent.name)
        info_parts = [part for part in (contragent.inn, contragent.phone, contragent.address) if part]
        self._info_label.setText(" • ".join(info_parts) if info_parts else "Qo'shimcha ma'lumot yo'q")

        while self._summary_row.count():
            self._summary_row.takeAt(0).widget().deleteLater()
        self._summary_row.addWidget(KpiCard("Shartnomalar soni", str(len(self._view_model.rows))))
        self._summary_row.addWidget(KpiCard("Umumiy qarz", _AMOUNT_FORMAT(self._view_model.total_debt)))

        self._table.setRowCount(len(self._view_model.rows))
        for row_index, row in enumerate(self._view_model.rows):
            values = (
                row.contract.contract_number,
                row.contract.contract_date.strftime("%d.%m.%Y"),
                row.contract.currency.value,
                _AMOUNT_FORMAT(row.contract.amount),
                row.contract.status.value,
                _AMOUNT_FORMAT(row.debt),
            )
            for column, value in enumerate(values):
                self._table.setItem(row_index, column, QTableWidgetItem(value))

    def _export(self, fmt: str) -> None:
        extension = {"excel": "xlsx", "pdf": "pdf"}[fmt]
        path, _ = QFileDialog.getSaveFileName(
            self, "Hisobotni saqlash", f"{self._view_model.contragent.name}.{extension}",
            f"*.{extension}",
        )
        if not path:
            return
        report = build_contragent_report(self._view_model.contragent_id)
        if fmt == "excel":
            report.to_excel(Path(path))
        else:
            report.to_pdf(Path(path))
        QMessageBox.information(self, "Tayyor", "Hisobot muvaffaqiyatli saqlandi")

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Xatolik", message)

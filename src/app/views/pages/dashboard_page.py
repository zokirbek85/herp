"""Dashboard: asosiy KPI'lar va grafiklar (Power BI uslubida)."""

from datetime import date

from PySide6.QtCharts import (
    QBarCategoryAxis,
    QBarSeries,
    QBarSet,
    QChart,
    QChartView,
    QPieSeries,
    QValueAxis,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QMessageBox, QPushButton, QVBoxLayout, QWidget

import qtawesome as qta

from app.viewmodels.dashboard_viewmodel import DashboardViewModel
from app.widgets.kpi_card import KpiCard

_AMOUNT_FORMAT = "{:,.2f}".format
_STATUS_LABELS = {
    "NEW": "Yangi",
    "IN_PROGRESS": "Jarayonda",
    "COMPLETED": "Yakunlangan",
    "CANCELLED": "Bekor qilingan",
}
_MONTH_LABELS = ("Yan", "Fev", "Mar", "Apr", "May", "Iyun", "Iyul", "Avg", "Sen", "Okt", "Noy", "Dek")


class DashboardPage(QWidget):
    def __init__(self, view_model: DashboardViewModel | None = None, parent=None) -> None:
        super().__init__(parent)
        self._view_model = view_model or DashboardViewModel()
        self._view_model.data_changed.connect(self._render)
        self._view_model.error_occurred.connect(self._show_error)

        refresh_button = QPushButton(" Yangilash")
        refresh_button.setIcon(qta.icon("fa5s.sync"))
        refresh_button.clicked.connect(self._view_model.load)

        toolbar = QHBoxLayout()
        toolbar.addStretch()
        toolbar.addWidget(refresh_button)

        self._kpi_grid = QGridLayout()
        self._kpi_grid.setSpacing(12)

        self._status_chart_view = QChartView()
        self._status_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._status_chart_view.setMinimumHeight(320)

        self._monthly_chart_view = QChartView()
        self._monthly_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._monthly_chart_view.setMinimumHeight(320)

        charts_row = QHBoxLayout()
        charts_row.addWidget(self._status_chart_view, stretch=1)
        charts_row.addWidget(self._monthly_chart_view, stretch=2)

        layout = QVBoxLayout(self)
        layout.addLayout(toolbar)
        layout.addLayout(self._kpi_grid)
        layout.addLayout(charts_row)
        layout.addStretch()

        self._view_model.load()

    def _render(self) -> None:
        vm = self._view_model

        while self._kpi_grid.count():
            self._kpi_grid.takeAt(0).widget().deleteLater()

        cards = (
            ("Kontragentlar", str(vm.contragent_count)),
            ("Shartnomalar", str(vm.contract_count)),
            ("Jami sotuv", _AMOUNT_FORMAT(vm.total_shipped)),
            ("Jami tushum", _AMOUNT_FORMAT(vm.total_paid)),
            ("Avans qoldig'i", _AMOUNT_FORMAT(vm.total_advance_balance)),
            ("Debitorlik", _AMOUNT_FORMAT(vm.total_debt)),
            ("O'rtacha narx", _AMOUNT_FORMAT(vm.average_price)),
        )
        for index, (title, value) in enumerate(cards):
            self._kpi_grid.addWidget(KpiCard(title, value), index // 4, index % 4)

        self._render_status_chart()
        self._render_monthly_chart()

    def _render_status_chart(self) -> None:
        series = QPieSeries()
        for status, count in self._view_model.status_breakdown.items():
            if count > 0:
                series.append(_STATUS_LABELS.get(status.value, status.value), count)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Shartnomalar statusi")
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        self._status_chart_view.setChart(chart)

    def _render_monthly_chart(self) -> None:
        shipped_set = QBarSet("Sotuv")
        paid_set = QBarSet("Tushum")
        max_value = 1.0
        for shipped_row, paid_row in zip(
            self._view_model.monthly_shipped, self._view_model.monthly_paid, strict=True
        ):
            shipped_set.append(float(shipped_row.total_amount))
            paid_set.append(float(paid_row.total_amount))
            max_value = max(max_value, float(shipped_row.total_amount), float(paid_row.total_amount))

        series = QBarSeries()
        series.append(shipped_set)
        series.append(paid_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"Oylik sotuv va tushum ({date.today().year})")
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        axis_x = QBarCategoryAxis()
        axis_x.append(list(_MONTH_LABELS))
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setRange(0, max_value * 1.1)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        self._monthly_chart_view.setChart(chart)

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Xatolik", message)

"""Dashboard: asosiy KPI'lar va grafiklar (Power BI uslubida)."""

from PySide6.QtCharts import (
    QBarCategoryAxis,
    QBarSeries,
    QBarSet,
    QChart,
    QChartView,
    QPieSeries,
    QValueAxis,
)
from PySide6.QtCore import QMargins, Qt, Signal
from PySide6.QtGui import QFont, QPainter
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import qtawesome as qta

from app.viewmodels.dashboard_viewmodel import DashboardViewModel
from app.widgets.kpi_card import KpiCard

_AMOUNT_FORMAT = "{:,.2f}".format
_KG_FORMAT = "{:,.3f} kg".format
_STATUS_LABELS = {
    "NEW": "Yangi",
    "IN_PROGRESS": "Jarayonda",
    "COMPLETED": "Yakunlangan",
    "CANCELLED": "Bekor qilingan",
}
_MONTH_LABELS = ("Yan", "Fev", "Mar", "Apr", "May", "Iyun", "Iyul", "Avg", "Sen", "Okt", "Noy", "Dek")


class DashboardPage(QWidget):
    navigate_requested = Signal(str)

    def __init__(self, view_model: DashboardViewModel | None = None, parent=None) -> None:
        super().__init__(parent)
        self._view_model = view_model or DashboardViewModel()
        self._view_model.data_changed.connect(self._render)
        self._view_model.error_occurred.connect(self._show_error)

        page_title = QLabel("Dashboard")
        page_title.setObjectName("PageTitle")

        refresh_button = QPushButton(" Yangilash")
        refresh_button.setIcon(qta.icon("fa5s.sync"))
        refresh_button.clicked.connect(self._view_model.load)

        toolbar = QHBoxLayout()
        toolbar.addWidget(page_title)
        toolbar.addStretch()
        toolbar.addWidget(refresh_button)

        self._kpi_grid = QGridLayout()
        self._kpi_grid.setSpacing(12)

        self._aging_label = QLabel("Debitorlik yoshi")
        self._aging_label.setStyleSheet("font-weight: 600; margin-top: 8px;")
        self._aging_grid = QGridLayout()
        self._aging_grid.setSpacing(12)

        self._status_chart_view = QChartView()
        self._status_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._status_chart_view.setMinimumHeight(320)
        self._status_chart_view.setBackgroundBrush(Qt.BrushStyle.NoBrush)
        self._status_chart_view.setFrameShape(QFrame.Shape.NoFrame)

        self._monthly_chart_view = QChartView()
        self._monthly_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._monthly_chart_view.setMinimumHeight(320)
        self._monthly_chart_view.setBackgroundBrush(Qt.BrushStyle.NoBrush)
        self._monthly_chart_view.setFrameShape(QFrame.Shape.NoFrame)

        charts_row = QHBoxLayout()
        charts_row.addWidget(self._status_chart_view, stretch=1)
        charts_row.addWidget(self._monthly_chart_view, stretch=2)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        content = QWidget()
        content.setObjectName("ContentArea")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 16, 20, 16)
        content_layout.setSpacing(12)
        content_layout.addLayout(toolbar)
        content_layout.addLayout(self._kpi_grid)
        content_layout.addWidget(self._aging_label)
        content_layout.addLayout(self._aging_grid)
        content_layout.addLayout(charts_row)
        content_layout.addStretch()

        outer_layout.addWidget(content)

        self._view_model.load()

    def _render(self) -> None:
        vm = self._view_model

        while self._kpi_grid.count():
            self._kpi_grid.takeAt(0).widget().deleteLater()

        debt_variant = "danger" if vm.total_debt > 0 else "muted"
        kg_debt_variant = "danger" if vm.total_remaining_kg > 0 else "muted"

        kontragentlar_card = KpiCard(
            "Kontragentlar", str(vm.contragent_count),
            variant="info", icon_name="fa5s.users", clickable=True,
        )
        kontragentlar_card.clicked.connect(lambda: self.navigate_requested.emit("contragents"))

        shartnomalar_card = KpiCard(
            "Shartnomalar", str(vm.contract_count),
            variant="default", icon_name="fa5s.file-contract", clickable=True,
        )
        shartnomalar_card.clicked.connect(lambda: self.navigate_requested.emit("contracts"))

        jami_sotuv_card = KpiCard(
            "Jami sotuv", _AMOUNT_FORMAT(vm.total_shipped),
            variant="info", icon_name="fa5s.truck", clickable=True,
        )
        jami_sotuv_card.clicked.connect(lambda: self.navigate_requested.emit("shipments"))

        jami_tushum_card = KpiCard(
            "Jami tushum", _AMOUNT_FORMAT(vm.total_paid),
            variant="success", icon_name="fa5s.money-bill-wave", clickable=True,
        )
        jami_tushum_card.clicked.connect(lambda: self.navigate_requested.emit("payments"))

        cards = (
            kontragentlar_card,
            shartnomalar_card,
            jami_sotuv_card,
            jami_tushum_card,
            KpiCard(
                "Avans qoldig'i", _AMOUNT_FORMAT(vm.total_advance_balance),
                variant="warning", icon_name="fa5s.piggy-bank",
            ),
            KpiCard(
                "Debitorlik (so'm)", _AMOUNT_FORMAT(vm.total_debt),
                variant=debt_variant, icon_name="fa5s.exclamation-circle",
            ),
            KpiCard(
                "Qarzdorlik (kg)", _KG_FORMAT(vm.total_remaining_kg),
                variant=kg_debt_variant, icon_name="fa5s.weight-hanging",
                subtitle="Rejalashtirilgan, lekin yetkazilmagan",
            ),
            KpiCard(
                "O'rtacha narx", _AMOUNT_FORMAT(vm.average_price),
                variant="default", icon_name="fa5s.tag",
            ),
        )
        for index, card in enumerate(cards):
            self._kpi_grid.addWidget(card, index // 4, index % 4)

        while self._aging_grid.count():
            self._aging_grid.takeAt(0).widget().deleteLater()
        for index, bucket in enumerate(vm.aging_summary):
            self._aging_grid.addWidget(KpiCard(bucket.label, _AMOUNT_FORMAT(bucket.amount)), 0, index)

        self._render_status_chart()
        self._render_monthly_chart()

    def _render_status_chart(self) -> None:
        series = QPieSeries()
        for status, count in self._view_model.status_breakdown.items():
            if count > 0:
                series.append(_STATUS_LABELS.get(status.value, status.value), count)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("")
        chart.setBackgroundVisible(False)
        chart.setMargins(QMargins(0, 0, 0, 0))
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        chart.legend().setFont(QFont("-apple-system", 11))
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
        chart.setTitle("")
        chart.setBackgroundVisible(False)
        chart.setMargins(QMargins(0, 0, 0, 0))
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        chart.legend().setFont(QFont("-apple-system", 11))

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

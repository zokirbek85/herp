"""Asosiy oyna: chap tomonda navigatsiya, o'ngda joriy modul sahifasi, pastda status bar."""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

import qtawesome as qta

from app.config.preferences import save_theme
from app.config.settings import get_settings
from app.config.theme import apply_theme
from app.utils.device import get_device_id
from app.views.pages.analytics_page import AnalyticsPage
from app.views.pages.backup_page import BackupPage
from app.views.pages.contracts_page import ContractsPage
from app.views.pages.contragents_page import ContragentsPage
from app.views.pages.dashboard_page import DashboardPage
from app.views.pages.exchange_rates_page import ExchangeRatesPage
from app.views.pages.payments_page import PaymentsPage
from app.views.pages.products_page import ProductsPage
from app.views.pages.reports_page import ReportsPage
from app.views.pages.settings_page import SettingsPage
from app.views.pages.shipments_page import ShipmentsPage
from app.views.pages.sync_page import SyncPage

_PAGE_FACTORIES = {
    "dashboard": DashboardPage,
    "contragents": ContragentsPage,
    "products": ProductsPage,
    "contracts": ContractsPage,
    "shipments": ShipmentsPage,
    "payments": PaymentsPage,
    "exchange_rates": ExchangeRatesPage,
    "analytics": AnalyticsPage,
    "reports": ReportsPage,
    "backup": BackupPage,
    "sync": SyncPage,
    "settings": SettingsPage,
}

_NAV_GROUPS = (
    (None, (  # None = sarlavhasiz (Dashboard alohida)
        ("dashboard", "Dashboard", "fa5s.tachometer-alt"),
    )),
    ("Asosiy", (
        ("contragents", "Kontragentlar", "fa5s.users"),
        ("contracts", "Shartnomalar", "fa5s.file-contract"),
        ("shipments", "Ortishlar", "fa5s.truck"),
        ("payments", "To'lovlar", "fa5s.money-bill-wave"),
        ("exchange_rates", "Valyuta kurslari", "fa5s.coins"),
    )),
    ("Tahlil", (
        ("products", "Mahsulotlar", "fa5s.box"),
        ("analytics", "Analitika", "fa5s.chart-line"),
        ("reports", "Hisobotlar", "fa5s.file-pdf"),
    )),
    ("Tizim", (
        ("backup", "Backup", "fa5s.database"),
        ("sync", "Sinxronlash", "fa5s.sync"),
        ("settings", "Sozlamalar", "fa5s.cog"),
    )),
)

# Tartibni saqlash uchun flat ro'yxat (sahifa indekslari uchun):
_NAV_ITEMS = tuple(item for _, group in _NAV_GROUPS for item in group)


class MainWindow(QMainWindow):
    def __init__(self, initial_theme: str | None = None) -> None:
        super().__init__()
        settings = get_settings()
        self._theme = initial_theme or settings.theme
        self.setWindowTitle(settings.app_name)
        self.resize(1300, 820)

        self._pages = QStackedWidget()
        self._build_pages()

        sidebar = self._build_sidebar()

        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(sidebar)
        layout.addWidget(self._pages, stretch=1)
        self.setCentralWidget(central)

        self._build_status_bar(settings.app_version)

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(210)

        logo = QLabel("HERP")
        logo.setObjectName("SidebarLogo")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(8, 4, 8, 12)
        layout.setSpacing(0)
        layout.addWidget(logo)
        layout.addSpacing(4)

        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)

        page_index = 0
        icon_color = "#8E8E93"

        for group_label, items in _NAV_GROUPS:
            if group_label is not None:
                separator = QLabel(group_label.upper())
                separator.setObjectName("SidebarGroupLabel")
                layout.addWidget(separator)

            for _key, title, icon_name in items:
                button = QPushButton(f"  {title}")
                button.setCheckable(True)
                button.setIcon(qta.icon(icon_name, color=icon_color))
                button.setIconSize(QSize(16, 16))
                button.clicked.connect(
                    lambda _checked, i=page_index: self._pages.setCurrentIndex(i)
                )
                self._nav_group.addButton(button, page_index)
                layout.addWidget(button)
                page_index += 1

        layout.addStretch()

        theme_button = QPushButton("  Tungi rejim")
        theme_button.setCheckable(True)
        theme_button.setChecked(self._theme == "dark")
        theme_button.setIcon(qta.icon("fa5s.moon", color=icon_color))
        theme_button.toggled.connect(self._on_theme_toggled)
        layout.addWidget(theme_button)

        self._nav_group.button(0).setChecked(True)
        return sidebar

    def _on_theme_toggled(self, checked: bool) -> None:
        self._theme = "dark" if checked else "light"
        app = QApplication.instance()
        if app is not None:
            apply_theme(app, self._theme)
        save_theme(self._theme)

    def _build_pages(self) -> None:
        for key, _title, _icon_name in _NAV_ITEMS:
            page = _PAGE_FACTORIES[key]()
            if isinstance(page, DashboardPage):
                page.navigate_requested.connect(self._navigate_to)
            self._pages.addWidget(page)

    def _navigate_to(self, key: str) -> None:
        index = next(i for i, (item_key, _, _) in enumerate(_NAV_ITEMS) if item_key == key)
        self._pages.setCurrentIndex(index)
        button = self._nav_group.button(index)
        if button is not None:
            button.setChecked(True)

    def _build_status_bar(self, app_version: str) -> None:
        status_bar = QStatusBar()
        status_bar.addWidget(QLabel(f"Versiya {app_version}"))
        status_bar.addPermanentWidget(QLabel(f"Qurilma: {get_device_id()[:8]}"))
        self.setStatusBar(status_bar)

"""Analitika sahifasi uchun ViewModel: TOP10 ro'yxatlar."""

from decimal import Decimal

from PySide6.QtCore import Signal

from app.services.analytics_service import AnalyticsService, ContragentAmountRow, ProductVolumeRow
from app.viewmodels.base_viewmodel import BaseViewModel


class AnalyticsViewModel(BaseViewModel):
    data_changed = Signal()

    def __init__(self, service: AnalyticsService | None = None) -> None:
        super().__init__()
        self._service = service or AnalyticsService()
        self.top_debtors: list[ContragentAmountRow] = []
        self.top_contragents: list[ContragentAmountRow] = []
        self.top_products: list[ProductVolumeRow] = []
        self.kg_debt_by_product: list[tuple[str, Decimal]] = []
        self.completion_distribution: dict[str, int] = {}

    def load(self) -> None:
        def action() -> None:
            self.top_debtors = self._service.top_debtors(limit=10)
            self.top_contragents = self._service.top_contragents_by_shipped_amount(limit=10)
            self.top_products = self._service.top_products_by_shipped_kg(limit=10)
            self.kg_debt_by_product = self._service.kg_debt_by_product()
            self.completion_distribution = self._service.contract_completion_distribution()
            self.data_changed.emit()

        self.run_safely(action)

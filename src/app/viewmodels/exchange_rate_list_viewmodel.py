"""Valyuta kurslari sahifasi uchun ViewModel."""

from collections.abc import Sequence
from datetime import date
from decimal import Decimal

from PySide6.QtCore import Signal

from app.models.exchange_rate import ExchangeRate
from app.services.exchange_rate_service import ExchangeRateService
from app.viewmodels.base_viewmodel import BaseViewModel


class ExchangeRateListViewModel(BaseViewModel):
    rates_changed = Signal(list)

    def __init__(self, service: ExchangeRateService | None = None) -> None:
        super().__init__()
        self._service = service or ExchangeRateService()
        self._rates: Sequence[ExchangeRate] = []

    @property
    def rates(self) -> Sequence[ExchangeRate]:
        return self._rates

    def load(self) -> None:
        def action() -> None:
            self._rates = self._service.list_recent(100)
            self.rates_changed.emit(list(self._rates))

        self.run_safely(action)

    def upsert(self, rate_date: date, usd_to_uzs: Decimal) -> bool:
        def action() -> None:
            self._service.upsert(rate_date, usd_to_uzs)
            self.load()

        return self.run_safely(action)

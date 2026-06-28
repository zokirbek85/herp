"""Dashboard uchun KPI va grafik ma'lumotlarini agregatsiya qiladi."""

from datetime import date
from decimal import Decimal

from PySide6.QtCore import Signal

from app.core.enums import ContractStatus
from app.database.session import session_scope
from app.services.aging_service import AgingBucket, AgingService
from app.services.analytics_service import AnalyticsService, MonthlyAmountRow
from app.services.contract_service import ContractService
from app.services.contragent_service import ContragentService
from app.viewmodels.base_viewmodel import BaseViewModel


class DashboardViewModel(BaseViewModel):
    data_changed = Signal()

    def __init__(
        self,
        contragent_service: ContragentService | None = None,
        contract_service: ContractService | None = None,
        analytics_service: AnalyticsService | None = None,
    ) -> None:
        super().__init__()
        self._contragent_service = contragent_service or ContragentService()
        self._contract_service = contract_service or ContractService()
        self._analytics_service = analytics_service or AnalyticsService()

        self.contragent_count = 0
        self.contract_count = 0
        self.total_shipped = Decimal("0")
        self.total_paid = Decimal("0")
        self.total_advance_balance = Decimal("0")
        self.total_debt = Decimal("0")
        self.total_remaining_kg = Decimal("0")
        self.average_price = Decimal("0")
        self.status_breakdown: dict[ContractStatus, int] = {}
        self.monthly_shipped: list[MonthlyAmountRow] = []
        self.monthly_paid: list[MonthlyAmountRow] = []
        self.aging_summary: list[AgingBucket] = []

    def load(self) -> None:
        def action() -> None:
            self.contragent_count = self._contragent_service.count()
            self.contract_count = self._contract_service.count()

            total_shipped = Decimal("0")
            total_paid = Decimal("0")
            total_advance_balance = Decimal("0")
            total_debt = Decimal("0")
            total_remaining_kg = Decimal("0")
            for contract in self._contract_service.list_all():
                summary = self._contract_service.get_financial_summary(contract.id)
                total_shipped += summary.total_shipped
                total_paid += summary.total_paid
                total_advance_balance += summary.advance_balance
                total_debt += summary.debt
                total_remaining_kg += summary.total_remaining_kg

            self.total_shipped = total_shipped
            self.total_paid = total_paid
            self.total_advance_balance = total_advance_balance
            self.total_debt = total_debt
            self.total_remaining_kg = total_remaining_kg

            self.average_price = self._analytics_service.average_price()
            self.status_breakdown = self._analytics_service.contract_status_breakdown()

            current_year = date.today().year
            self.monthly_shipped = self._analytics_service.monthly_shipped_amount(current_year)
            self.monthly_paid = self._analytics_service.monthly_payment_amount(current_year)

            with session_scope() as session:
                self.aging_summary = AgingService(session).summary_by_bucket()

            self.data_changed.emit()

        self.run_safely(action)

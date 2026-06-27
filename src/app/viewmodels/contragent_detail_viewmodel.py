"""Kontragent kartochkasi uchun ViewModel: shartnomalar ro'yxati va umumiy qarz."""

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

from PySide6.QtCore import Signal

from app.models.contract import Contract
from app.models.contragent import Contragent
from app.services.contract_service import ContractService
from app.services.contragent_service import ContragentService
from app.viewmodels.base_viewmodel import BaseViewModel


@dataclass(frozen=True, slots=True)
class ContragentContractRow:
    contract: Contract
    debt: Decimal


class ContragentDetailViewModel(BaseViewModel):
    data_changed = Signal()

    def __init__(
        self,
        contragent_id: int,
        contragent_service: ContragentService | None = None,
        contract_service: ContractService | None = None,
    ) -> None:
        super().__init__()
        self.contragent_id = contragent_id
        self._contragent_service = contragent_service or ContragentService()
        self._contract_service = contract_service or ContractService()

        self.contragent: Contragent | None = None
        self.rows: Sequence[ContragentContractRow] = []
        self.total_debt: Decimal = Decimal("0")

    def load(self) -> None:
        def action() -> None:
            self.contragent = self._contragent_service.get(self.contragent_id)
            rows: list[ContragentContractRow] = []
            total_debt = Decimal("0")
            for contract in self._contract_service.list_by_contragent(self.contragent_id):
                summary = self._contract_service.get_financial_summary(contract.id)
                rows.append(ContragentContractRow(contract=contract, debt=summary.debt))
                total_debt += summary.debt
            self.rows = rows
            self.total_debt = total_debt
            self.data_changed.emit()

        self.run_safely(action)

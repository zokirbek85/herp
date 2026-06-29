"""Shartnomalar ro'yxati sahifasi uchun ViewModel."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from PySide6.QtCore import Signal

from app.core.enums import Currency
from app.models.contract import Contract
from app.services.contract_service import ContractService
from app.services.contragent_service import ContragentService
from app.viewmodels.base_viewmodel import BaseViewModel


@dataclass(frozen=True, slots=True)
class ContractRow:
    contract: Contract
    contragent_name: str
    debt: Decimal


class ContractListViewModel(BaseViewModel):
    rows_changed = Signal(list)

    def __init__(
        self,
        contract_service: ContractService | None = None,
        contragent_service: ContragentService | None = None,
    ) -> None:
        super().__init__()
        self._contract_service = contract_service or ContractService()
        self._contragent_service = contragent_service or ContragentService()
        self._rows: Sequence[ContractRow] = []

    @property
    def rows(self) -> Sequence[ContractRow]:
        return self._rows

    def load(self) -> None:
        def action() -> None:
            contragent_names: dict[int, str] = {}
            rows: list[ContractRow] = []
            for contract in self._contract_service.list_all():
                if contract.contragent_id not in contragent_names:
                    contragent_names[contract.contragent_id] = self._contragent_service.get(
                        contract.contragent_id
                    ).name
                summary = self._contract_service.get_financial_summary(contract.id)
                rows.append(
                    ContractRow(
                        contract=contract,
                        contragent_name=contragent_names[contract.contragent_id],
                        debt=summary.debt,
                    )
                )
            self._rows = rows
            self.rows_changed.emit(list(self._rows))

        self.run_safely(action)

    def create(
        self,
        *,
        contract_number: str,
        contragent_id: int,
        currency: Currency,
        amount: Decimal,
        contract_date: date,
        notes: str | None,
    ) -> bool:
        def action() -> None:
            self._contract_service.create(
                contract_number=contract_number,
                contragent_id=contragent_id,
                currency=currency,
                amount=amount,
                contract_date=contract_date,
                notes=notes,
            )
            self.load()

        return self.run_safely(action)

    def update(
        self,
        contract_id: int,
        *,
        contract_number: str,
        contragent_id: int,
        currency: Currency,
        amount: Decimal,
        contract_date: date,
        notes: str | None,
    ) -> bool:
        def action() -> None:
            self._contract_service.update(
                contract_id,
                contract_number=contract_number,
                contragent_id=contragent_id,
                currency=currency,
                amount=amount,
                contract_date=contract_date,
                notes=notes,
            )
            self.load()

        return self.run_safely(action)

    def delete(self, contract_id: int) -> bool:
        def action() -> None:
            self._contract_service.soft_delete(contract_id)
            self.load()

        return self.run_safely(action)

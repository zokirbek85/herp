"""Barcha shartnomalar bo'yicha To'lovlar ro'yxati uchun ViewModel."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from PySide6.QtCore import Signal

from app.core.enums import PaymentType
from app.models.payment import Payment
from app.services.contract_service import ContractService
from app.services.payment_service import PaymentService
from app.viewmodels.base_viewmodel import BaseViewModel


@dataclass(frozen=True, slots=True)
class PaymentRow:
    payment: Payment
    contract_number: str


class PaymentListViewModel(BaseViewModel):
    rows_changed = Signal(list)

    def __init__(
        self,
        payment_service: PaymentService | None = None,
        contract_service: ContractService | None = None,
    ) -> None:
        super().__init__()
        self._payment_service = payment_service or PaymentService()
        self._contract_service = contract_service or ContractService()
        self._rows: Sequence[PaymentRow] = []

    @property
    def rows(self) -> Sequence[PaymentRow]:
        return self._rows

    def load(self) -> None:
        def action() -> None:
            contract_numbers: dict[int, str] = {}
            rows: list[PaymentRow] = []
            for payment in self._payment_service.list_all():
                if payment.contract_id not in contract_numbers:
                    contract_numbers[payment.contract_id] = self._contract_service.get(
                        payment.contract_id
                    ).contract_number
                rows.append(
                    PaymentRow(payment=payment, contract_number=contract_numbers[payment.contract_id])
                )
            rows.sort(key=lambda row: row.payment.payment_date, reverse=True)
            self._rows = rows
            self.rows_changed.emit(list(self._rows))

        self.run_safely(action)

    def create(
        self, *, contract_id: int, payment_date: date, amount: Decimal, payment_type: PaymentType
    ) -> bool:
        def action() -> None:
            self._payment_service.create_payment(
                contract_id=contract_id, payment_date=payment_date, amount=amount, payment_type=payment_type
            )
            self.load()

        return self.run_safely(action)

    def contract_choices(self) -> list[tuple[int, str]]:
        return [
            (contract.id, contract.contract_number) for contract in self._contract_service.list_all()
        ]

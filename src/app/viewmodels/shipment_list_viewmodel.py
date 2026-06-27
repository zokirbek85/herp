"""Barcha shartnomalar bo'yicha Ortishlar ro'yxati uchun ViewModel."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from PySide6.QtCore import Signal

from app.models.shipment import Shipment
from app.services.contract_service import ContractService
from app.services.dto import ShipmentItemInput
from app.services.shipment_service import ShipmentService
from app.viewmodels.base_viewmodel import BaseViewModel


@dataclass(frozen=True, slots=True)
class ShipmentRow:
    shipment: Shipment
    contract_number: str
    total_amount: Decimal


class ShipmentListViewModel(BaseViewModel):
    rows_changed = Signal(list)

    def __init__(
        self,
        shipment_service: ShipmentService | None = None,
        contract_service: ContractService | None = None,
    ) -> None:
        super().__init__()
        self._shipment_service = shipment_service or ShipmentService()
        self._contract_service = contract_service or ContractService()
        self._rows: Sequence[ShipmentRow] = []

    @property
    def rows(self) -> Sequence[ShipmentRow]:
        return self._rows

    def load(self) -> None:
        def action() -> None:
            contract_numbers: dict[int, str] = {}
            rows: list[ShipmentRow] = []
            for shipment in self._shipment_service.list_all():
                if shipment.contract_id not in contract_numbers:
                    contract_numbers[shipment.contract_id] = self._contract_service.get(
                        shipment.contract_id
                    ).contract_number
                total = sum(
                    (item.amount for item in self._shipment_service.list_items(shipment.id)),
                    start=Decimal("0"),
                )
                rows.append(
                    ShipmentRow(
                        shipment=shipment,
                        contract_number=contract_numbers[shipment.contract_id],
                        total_amount=total,
                    )
                )
            rows.sort(key=lambda row: row.shipment.shipment_date, reverse=True)
            self._rows = rows
            self.rows_changed.emit(list(self._rows))

        self.run_safely(action)

    def create(
        self,
        *,
        contract_id: int,
        shipment_number: str,
        shipment_date: date,
        items: list[ShipmentItemInput],
        invoice_number: str | None,
        ttn_number: str | None,
    ) -> bool:
        def action() -> None:
            self._shipment_service.create_shipment(
                contract_id=contract_id,
                shipment_number=shipment_number,
                shipment_date=shipment_date,
                items=items,
                invoice_number=invoice_number,
                ttn_number=ttn_number,
            )
            self.load()

        return self.run_safely(action)

    def contract_choices(self) -> list[tuple[int, str]]:
        return [
            (contract.id, contract.contract_number) for contract in self._contract_service.list_all()
        ]

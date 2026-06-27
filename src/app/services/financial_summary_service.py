"""Shartnoma kartochkasi/Dashboard uchun moliyaviy KPI'larni hisoblaydi
(Jami buyurtma, Jami yetkazilgan, Qoldiq, To'langan, Qarz)."""

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.repositories.payment_allocation_repository import PaymentAllocationRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.shipment_item_repository import ShipmentItemRepository
from app.repositories.shipment_repository import ShipmentRepository


@dataclass(frozen=True, slots=True)
class ContractFinancialSummary:
    contract_amount: Decimal
    total_shipped: Decimal
    remaining_to_ship: Decimal
    total_paid: Decimal
    total_allocated_to_shipments: Decimal
    advance_balance: Decimal
    debt: Decimal


class FinancialSummaryService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self._shipment_repo = ShipmentRepository(session)
        self._item_repo = ShipmentItemRepository(session)
        self._payment_repo = PaymentRepository(session)
        self._allocation_repo = PaymentAllocationRepository(session)

    def build(self, contract: Contract) -> ContractFinancialSummary:
        total_shipped = Decimal("0")
        total_allocated_to_shipments = Decimal("0")
        for shipment in self._shipment_repo.list_by_contract(contract.id):
            for item in self._item_repo.list_by_shipment(shipment.id):
                total_shipped += item.amount
            total_allocated_to_shipments += self._allocation_repo.total_allocated_for_shipment(
                shipment.id
            )

        total_paid = Decimal("0")
        total_allocated_from_payments = Decimal("0")
        for payment in self._payment_repo.list_by_contract(contract.id):
            total_paid += payment.amount
            total_allocated_from_payments += self._allocation_repo.total_allocated_for_payment(
                payment.id
            )

        advance_balance = total_paid - total_allocated_from_payments
        debt = max(total_shipped - total_allocated_to_shipments, Decimal("0"))
        remaining_to_ship = max(contract.amount - total_shipped, Decimal("0"))

        return ContractFinancialSummary(
            contract_amount=contract.amount,
            total_shipped=total_shipped,
            remaining_to_ship=remaining_to_ship,
            total_paid=total_paid,
            total_allocated_to_shipments=total_allocated_to_shipments,
            advance_balance=advance_balance,
            debt=debt,
        )

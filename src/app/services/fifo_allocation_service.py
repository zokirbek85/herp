"""FIFO to'lov taqsimoti: ortishlar eng eski sanadan boshlab to'lovlar bilan yopiladi."""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.payment_allocation import PaymentAllocation
from app.repositories.payment_allocation_repository import PaymentAllocationRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.shipment_item_repository import ShipmentItemRepository
from app.repositories.shipment_repository import ShipmentRepository


class FifoAllocationService:
    """Bitta shartnoma doirasida to'lov va ortishlarni FIFO tartibida moslashtiradi.

    Algoritm idempotent: har safar to'liq qayta hisoblanadi — mavjud allocation'lar hisobga
    olinadi, faqat yetishmayotgan qism uchun yangi `PaymentAllocation` yaratiladi. Shu sababli
    bu metod yangi to'lov qo'shilganda ham, yangi ortish qo'shilganda ham bir xil chaqiriladi:
    avans sifatida kelgan to'lov keyinroq paydo bo'lgan ortishga avtomatik yopiladi, va aksincha.
    """

    def __init__(self, session: Session) -> None:
        self.session = session
        self._shipment_repo = ShipmentRepository(session)
        self._item_repo = ShipmentItemRepository(session)
        self._payment_repo = PaymentRepository(session)
        self._allocation_repo = PaymentAllocationRepository(session)

    def reconcile_contract(self, contract_id: int) -> None:
        shipment_outstanding = self._collect_shipment_outstanding(contract_id)
        payment_available = self._collect_payment_available(contract_id)

        shipment_idx = 0
        payment_idx = 0

        while shipment_idx < len(shipment_outstanding) and payment_idx < len(payment_available):
            shipment_id, outstanding = shipment_outstanding[shipment_idx]
            payment_id, available = payment_available[payment_idx]

            matched = min(outstanding, available)
            if matched > 0:
                self._allocation_repo.add(
                    PaymentAllocation(
                        payment_id=payment_id,
                        shipment_id=shipment_id,
                        allocated_amount=matched,
                    )
                )

            outstanding -= matched
            available -= matched
            shipment_outstanding[shipment_idx] = (shipment_id, outstanding)
            payment_available[payment_idx] = (payment_id, available)

            if outstanding <= 0:
                shipment_idx += 1
            if available <= 0:
                payment_idx += 1

    def _collect_shipment_outstanding(self, contract_id: int) -> list[tuple[int, Decimal]]:
        result: list[tuple[int, Decimal]] = []
        for shipment in self._shipment_repo.list_by_contract(contract_id):
            total_amount = sum(
                (item.amount for item in self._item_repo.list_by_shipment(shipment.id)),
                Decimal("0"),
            )
            allocated = self._allocation_repo.total_allocated_for_shipment(shipment.id)
            outstanding = total_amount - allocated
            if outstanding > 0:
                result.append((shipment.id, outstanding))
        return result

    def _collect_payment_available(self, contract_id: int) -> list[tuple[int, Decimal]]:
        result: list[tuple[int, Decimal]] = []
        for payment in self._payment_repo.list_by_contract(contract_id):
            allocated = self._allocation_repo.total_allocated_for_payment(payment.id)
            available = payment.amount - allocated
            if available > 0:
                result.append((payment.id, available))
        return result

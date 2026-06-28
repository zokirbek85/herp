"""FIFO to'lov taqsimoti: ortishlar eng eski sanadan boshlab to'lovlar bilan yopiladi.

Valyuta: `ShipmentItem`da o'z valyuta ustuni yo'q — uning summasi har doim shartnoma
valyutasida hisoblanadi (narx ham shu valyutada kiritiladi), shu sababli konversiyasiz
ishlatiladi. `Payment.currency` esa nazariy jihatdan shartnoma valyutasidan farq qilishi
mumkin bo'lgan mustaqil ustun — shu sababli FIFO'dan oldin har doim shartnoma valyutasiga
o'tkaziladi, aks holda USD shartnomaga UZS to'lov (yoki aksincha) noto'g'ri taqsimlanardi.
"""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.contract import Contract
from app.models.payment_allocation import PaymentAllocation
from app.repositories.payment_allocation_repository import PaymentAllocationRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.shipment_item_repository import ShipmentItemRepository
from app.repositories.shipment_repository import ShipmentRepository
from app.services.currency_service import CurrencyConversionError, CurrencyService


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
        self._currency_service = CurrencyService(session)

    def reconcile_contract(self, contract: Contract) -> None:
        try:
            shipment_outstanding = self._collect_shipment_outstanding(contract)
            payment_available = self._collect_payment_available(contract)
        except CurrencyConversionError as exc:
            raise AppError(str(exc)) from exc

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

    def _collect_shipment_outstanding(self, contract: Contract) -> list[tuple[int, Decimal]]:
        result: list[tuple[int, Decimal]] = []
        for shipment in self._shipment_repo.list_by_contract(contract.id):
            # ShipmentItem'da mustaqil valyuta ustuni yo'q — narx/summa allaqachon shartnoma
            # valyutasida, shu sababli konversiya kerak emas.
            total_amount = sum(
                (item.amount for item in self._item_repo.list_by_shipment(shipment.id)),
                Decimal("0"),
            )
            allocated = self._allocation_repo.total_allocated_for_shipment(shipment.id)
            outstanding = total_amount - allocated
            if outstanding > 0:
                result.append((shipment.id, outstanding))
        return result

    def _collect_payment_available(self, contract: Contract) -> list[tuple[int, Decimal]]:
        result: list[tuple[int, Decimal]] = []
        for payment in self._payment_repo.list_by_contract(contract.id):
            amount_in_contract_currency = self._currency_service.convert(
                payment.amount, payment.currency, contract.currency, payment.payment_date
            )
            allocated = self._allocation_repo.total_allocated_for_payment(payment.id)
            available = amount_in_contract_currency - allocated
            if available > 0:
                result.append((payment.id, available))
        return result

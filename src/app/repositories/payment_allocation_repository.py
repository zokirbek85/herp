from collections.abc import Sequence
from decimal import Decimal

from sqlalchemy import func, select

from app.models.payment_allocation import PaymentAllocation
from app.repositories.base_repository import BaseRepository


class PaymentAllocationRepository(BaseRepository[PaymentAllocation]):
    model = PaymentAllocation

    def list_by_payment(self, payment_id: int) -> Sequence[PaymentAllocation]:
        stmt = select(PaymentAllocation).where(
            PaymentAllocation.payment_id == payment_id, PaymentAllocation.deleted_at.is_(None)
        )
        return self.session.execute(stmt).scalars().all()

    def list_by_shipment(self, shipment_id: int) -> Sequence[PaymentAllocation]:
        stmt = select(PaymentAllocation).where(
            PaymentAllocation.shipment_id == shipment_id, PaymentAllocation.deleted_at.is_(None)
        )
        return self.session.execute(stmt).scalars().all()

    def total_allocated_for_payment(self, payment_id: int) -> Decimal:
        stmt = select(func.coalesce(func.sum(PaymentAllocation.allocated_amount), 0)).where(
            PaymentAllocation.payment_id == payment_id, PaymentAllocation.deleted_at.is_(None)
        )
        return self.session.execute(stmt).scalar_one()

    def total_allocated_for_shipment(self, shipment_id: int) -> Decimal:
        stmt = select(func.coalesce(func.sum(PaymentAllocation.allocated_amount), 0)).where(
            PaymentAllocation.shipment_id == shipment_id, PaymentAllocation.deleted_at.is_(None)
        )
        return self.session.execute(stmt).scalar_one()

    def soft_delete_by_payment(self, payment_id: int) -> None:
        for allocation in self.list_by_payment(payment_id):
            self.soft_delete(allocation)

    def soft_delete_by_shipment(self, shipment_id: int) -> None:
        for allocation in self.list_by_shipment(shipment_id):
            self.soft_delete(allocation)

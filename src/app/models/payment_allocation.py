from decimal import Decimal

from sqlalchemy import Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditMixin, Base


class PaymentAllocation(Base, AuditMixin):
    """FIFO mantig'i bo'yicha bitta to'lovning qaysi ortish(lar)ga necha pul yopilganini kuzatadi.

    `payment_id`/`shipment_id`da DB darajasida FK yo'q (DuckDB FK cheklovi — [[contract.py]]ga qarang).
    """

    __tablename__ = "payment_allocations"

    payment_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    shipment_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    allocated_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    payment: Mapped["Payment"] = relationship(  # noqa: F821
        primaryjoin="PaymentAllocation.payment_id == Payment.id",
        foreign_keys="[PaymentAllocation.payment_id]",
        back_populates="allocations",
    )
    shipment: Mapped["Shipment"] = relationship(  # noqa: F821
        primaryjoin="PaymentAllocation.shipment_id == Shipment.id",
        foreign_keys="[PaymentAllocation.shipment_id]",
        back_populates="allocations",
    )

    def __repr__(self) -> str:
        return f"<PaymentAllocation payment_id={self.payment_id} shipment_id={self.shipment_id}>"

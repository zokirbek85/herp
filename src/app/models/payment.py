from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import Currency, PaymentType
from app.database.base import AuditMixin, Base


class Payment(Base, AuditMixin):
    """`contract_id`da DB darajasida FK yo'q (DuckDB FK cheklovi — [[contract.py]]ga qarang)."""

    __tablename__ = "payments"

    contract_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[Currency] = mapped_column(Enum(Currency, native_enum=False, length=10), nullable=False)
    payment_type: Mapped[PaymentType] = mapped_column(
        Enum(PaymentType, native_enum=False, length=20), nullable=False
    )
    notes: Mapped[str | None] = mapped_column(String(1000))

    contract: Mapped["Contract"] = relationship(  # noqa: F821
        primaryjoin="Payment.contract_id == Contract.id",
        foreign_keys="[Payment.contract_id]",
        back_populates="payments",
    )
    allocations: Mapped[list["PaymentAllocation"]] = relationship(  # noqa: F821
        primaryjoin="Payment.id == PaymentAllocation.payment_id",
        foreign_keys="[PaymentAllocation.payment_id]",
        back_populates="payment",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Payment id={self.id} amount={self.amount} {self.currency}>"

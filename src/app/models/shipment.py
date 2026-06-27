from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditMixin, Base


class Shipment(Base, AuditMixin):
    """`contract_id`da DB darajasida FK yo'q (DuckDB FK cheklovi — [[contract.py]]ga qarang)."""

    __tablename__ = "shipments"

    shipment_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    contract_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    shipment_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    invoice_number: Mapped[str | None] = mapped_column(String(100), index=True)
    ttn_number: Mapped[str | None] = mapped_column(String(100), index=True)
    notes: Mapped[str | None] = mapped_column(String(1000))

    contract: Mapped["Contract"] = relationship(  # noqa: F821
        primaryjoin="Shipment.contract_id == Contract.id",
        foreign_keys="[Shipment.contract_id]",
        back_populates="shipments",
    )
    items: Mapped[list["ShipmentItem"]] = relationship(  # noqa: F821
        primaryjoin="Shipment.id == ShipmentItem.shipment_id",
        foreign_keys="[ShipmentItem.shipment_id]",
        back_populates="shipment",
        cascade="all, delete-orphan",
    )
    allocations: Mapped[list["PaymentAllocation"]] = relationship(  # noqa: F821
        primaryjoin="Shipment.id == PaymentAllocation.shipment_id",
        foreign_keys="[PaymentAllocation.shipment_id]",
        back_populates="shipment",
    )

    def __repr__(self) -> str:
        return f"<Shipment id={self.id} number={self.shipment_number!r}>"

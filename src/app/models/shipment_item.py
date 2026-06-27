from decimal import Decimal

from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditMixin, Base


class ShipmentItem(Base, AuditMixin):
    """`shipment_id`/`product_id`da DB darajasida FK yo'q (DuckDB FK cheklovi — [[contract.py]]ga qarang)."""

    __tablename__ = "shipment_items"

    shipment_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    lot_number: Mapped[str | None] = mapped_column(String(100))
    kg: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    shipment: Mapped["Shipment"] = relationship(  # noqa: F821
        primaryjoin="ShipmentItem.shipment_id == Shipment.id",
        foreign_keys="[ShipmentItem.shipment_id]",
        back_populates="items",
    )
    product: Mapped["Product"] = relationship(  # noqa: F821
        primaryjoin="ShipmentItem.product_id == Product.id",
        foreign_keys="[ShipmentItem.product_id]",
    )

    def __repr__(self) -> str:
        return f"<ShipmentItem id={self.id} shipment_id={self.shipment_id}>"

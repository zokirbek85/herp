from decimal import Decimal

from sqlalchemy import Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditMixin, Base


class ContractSpecification(Base, AuditMixin):
    """`contract_id`/`product_id`da DB darajasida FK yo'q (DuckDB FK cheklovi — [[contract.py]]ga qarang)."""

    __tablename__ = "contract_specifications"
    __table_args__ = (UniqueConstraint("contract_id", "product_id", name="uq_contract_product"),)

    contract_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    planned_kg: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    reference_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    contract: Mapped["Contract"] = relationship(  # noqa: F821
        primaryjoin="ContractSpecification.contract_id == Contract.id",
        foreign_keys="[ContractSpecification.contract_id]",
        back_populates="specifications",
    )
    product: Mapped["Product"] = relationship(  # noqa: F821
        primaryjoin="ContractSpecification.product_id == Product.id",
        foreign_keys="[ContractSpecification.product_id]",
    )

    def __repr__(self) -> str:
        return f"<ContractSpecification id={self.id} contract_id={self.contract_id}>"

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ContractStatus, Currency
from app.database.base import AuditMixin, Base


class Contract(Base, AuditMixin):
    """`contragent_id`da DB darajasida FK yo'q — DuckDB FK bilan bog'langan qatorni UPDATE
    qilishni butunlay bloklaydi. Yaxlitlik `ContractService` ichida tekshiriladi."""

    __tablename__ = "contracts"

    contract_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    contragent_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    currency: Mapped[Currency] = mapped_column(Enum(Currency, native_enum=False, length=10), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    contract_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[ContractStatus] = mapped_column(
        Enum(ContractStatus, native_enum=False, length=20),
        default=ContractStatus.NEW,
        nullable=False,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(String(1000))

    contragent: Mapped["Contragent"] = relationship(  # noqa: F821
        primaryjoin="Contract.contragent_id == Contragent.id",
        foreign_keys="[Contract.contragent_id]",
        back_populates="contracts",
    )
    specifications: Mapped[list["ContractSpecification"]] = relationship(  # noqa: F821
        primaryjoin="Contract.id == ContractSpecification.contract_id",
        foreign_keys="[ContractSpecification.contract_id]",
        back_populates="contract",
        cascade="all, delete-orphan",
    )
    shipments: Mapped[list["Shipment"]] = relationship(  # noqa: F821
        primaryjoin="Contract.id == Shipment.contract_id",
        foreign_keys="[Shipment.contract_id]",
        back_populates="contract",
    )
    payments: Mapped[list["Payment"]] = relationship(  # noqa: F821
        primaryjoin="Contract.id == Payment.contract_id",
        foreign_keys="[Payment.contract_id]",
        back_populates="contract",
    )

    def __repr__(self) -> str:
        return f"<Contract id={self.id} number={self.contract_number!r}>"

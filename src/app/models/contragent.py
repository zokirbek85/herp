from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditMixin, Base


class Contragent(Base, AuditMixin):
    __tablename__ = "contragents"

    name: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    inn: Mapped[str | None] = mapped_column(String(20), unique=True)
    phone: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(String(500))
    contact_person: Mapped[str | None] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(String(1000))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    contracts: Mapped[list["Contract"]] = relationship(  # noqa: F821
        primaryjoin="Contragent.id == Contract.contragent_id",
        foreign_keys="[Contract.contragent_id]",
        back_populates="contragent",
    )

    def __repr__(self) -> str:
        return f"<Contragent id={self.id} name={self.name!r}>"

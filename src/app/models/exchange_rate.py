from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import AuditMixin, Base


class ExchangeRate(Base, AuditMixin):
    """Dashboard/Analitika'da USD va UZS shartnomalarini bitta valyutada aralashtirib ko'rsatish uchun kurs."""

    __tablename__ = "exchange_rates"

    rate_date: Mapped[date] = mapped_column(Date, unique=True, nullable=False, index=True)
    usd_to_uzs: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)

    def __repr__(self) -> str:
        return f"<ExchangeRate date={self.rate_date} rate={self.usd_to_uzs}>"

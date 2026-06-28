"""Valyuta kurslari uchun CRUD biznes qoidalari."""

from collections.abc import Sequence
from datetime import date
from decimal import Decimal

from app.core.exceptions import ValidationError
from app.database.session import session_scope
from app.models.exchange_rate import ExchangeRate
from app.repositories.exchange_rate_repository import ExchangeRateRepository


class ExchangeRateService:
    def upsert(self, rate_date: date, usd_to_uzs: Decimal) -> ExchangeRate:
        """Shu sana uchun kurs mavjud bo'lsa yangilaydi, bo'lmasa yangi yozuv yaratadi."""
        if usd_to_uzs <= 0:
            raise ValidationError("Kurs musbat bo'lishi kerak")

        with session_scope() as session:
            repo = ExchangeRateRepository(session)
            existing = repo.get_by_date(rate_date)
            if existing is not None:
                existing.usd_to_uzs = usd_to_uzs
                session.flush()
                return existing
            return repo.add(ExchangeRate(rate_date=rate_date, usd_to_uzs=usd_to_uzs))

    def list_recent(self, limit: int = 30) -> Sequence[ExchangeRate]:
        with session_scope() as session:
            return ExchangeRateRepository(session).list_recent(limit)

    def get_latest(self) -> ExchangeRate | None:
        with session_scope() as session:
            return ExchangeRateRepository(session).get_latest_on_or_before(date.today())

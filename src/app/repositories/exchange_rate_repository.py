from datetime import date

from sqlalchemy import select

from app.models.exchange_rate import ExchangeRate
from app.repositories.base_repository import BaseRepository


class ExchangeRateRepository(BaseRepository[ExchangeRate]):
    model = ExchangeRate

    def get_latest_on_or_before(self, target_date: date) -> ExchangeRate | None:
        stmt = (
            select(ExchangeRate)
            .where(ExchangeRate.rate_date <= target_date, ExchangeRate.deleted_at.is_(None))
            .order_by(ExchangeRate.rate_date.desc())
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none()

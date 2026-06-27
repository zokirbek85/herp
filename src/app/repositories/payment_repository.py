from collections.abc import Sequence

from sqlalchemy import select

from app.models.payment import Payment
from app.repositories.base_repository import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    model = Payment

    def list_by_contract(self, contract_id: int) -> Sequence[Payment]:
        """FIFO tartibida (sana, keyin id bo'yicha) — eng eski to'lov birinchi keladi."""
        stmt = (
            select(Payment)
            .where(Payment.contract_id == contract_id, Payment.deleted_at.is_(None))
            .order_by(Payment.payment_date, Payment.id)
        )
        return self.session.execute(stmt).scalars().all()

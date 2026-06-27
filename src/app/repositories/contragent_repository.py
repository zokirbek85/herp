from collections.abc import Sequence

from sqlalchemy import select

from app.models.contragent import Contragent
from app.repositories.base_repository import BaseRepository


class ContragentRepository(BaseRepository[Contragent]):
    model = Contragent

    def get_by_inn(self, inn: str) -> Contragent | None:
        stmt = select(Contragent).where(Contragent.inn == inn, Contragent.deleted_at.is_(None))
        return self.session.execute(stmt).scalar_one_or_none()

    def search_by_name(self, query: str, *, limit: int = 20) -> Sequence[Contragent]:
        stmt = (
            select(Contragent)
            .where(Contragent.name.ilike(f"%{query}%"), Contragent.deleted_at.is_(None))
            .order_by(Contragent.name)
            .limit(limit)
        )
        return self.session.execute(stmt).scalars().all()

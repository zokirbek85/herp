from collections.abc import Sequence

from sqlalchemy import select

from app.core.enums import ContractStatus
from app.models.contract import Contract
from app.repositories.base_repository import BaseRepository


class ContractRepository(BaseRepository[Contract]):
    model = Contract

    def get_by_number(self, contract_number: str) -> Contract | None:
        stmt = select(Contract).where(
            Contract.contract_number == contract_number, Contract.deleted_at.is_(None)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def list_by_contragent(self, contragent_id: int) -> Sequence[Contract]:
        stmt = (
            select(Contract)
            .where(Contract.contragent_id == contragent_id, Contract.deleted_at.is_(None))
            .order_by(Contract.contract_date.desc())
        )
        return self.session.execute(stmt).scalars().all()

    def list_by_status(self, status: ContractStatus) -> Sequence[Contract]:
        stmt = select(Contract).where(Contract.status == status, Contract.deleted_at.is_(None))
        return self.session.execute(stmt).scalars().all()

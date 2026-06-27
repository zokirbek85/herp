from collections.abc import Sequence

from sqlalchemy import select

from app.models.contract_specification import ContractSpecification
from app.repositories.base_repository import BaseRepository


class ContractSpecificationRepository(BaseRepository[ContractSpecification]):
    model = ContractSpecification

    def list_by_contract(self, contract_id: int) -> Sequence[ContractSpecification]:
        stmt = select(ContractSpecification).where(
            ContractSpecification.contract_id == contract_id,
            ContractSpecification.deleted_at.is_(None),
        )
        return self.session.execute(stmt).scalars().all()

    def get_by_contract_and_product(
        self, contract_id: int, product_id: int
    ) -> ContractSpecification | None:
        stmt = select(ContractSpecification).where(
            ContractSpecification.contract_id == contract_id,
            ContractSpecification.product_id == product_id,
            ContractSpecification.deleted_at.is_(None),
        )
        return self.session.execute(stmt).scalar_one_or_none()

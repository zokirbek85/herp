from collections.abc import Sequence

from sqlalchemy import select

from app.models.shipment import Shipment
from app.repositories.base_repository import BaseRepository


class ShipmentRepository(BaseRepository[Shipment]):
    model = Shipment

    def get_by_number(self, shipment_number: str) -> Shipment | None:
        stmt = select(Shipment).where(
            Shipment.shipment_number == shipment_number, Shipment.deleted_at.is_(None)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def list_by_contract(self, contract_id: int) -> Sequence[Shipment]:
        stmt = (
            select(Shipment)
            .where(Shipment.contract_id == contract_id, Shipment.deleted_at.is_(None))
            .order_by(Shipment.shipment_date)
        )
        return self.session.execute(stmt).scalars().all()

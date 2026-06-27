from collections.abc import Sequence

from sqlalchemy import select

from app.models.shipment_item import ShipmentItem
from app.repositories.base_repository import BaseRepository


class ShipmentItemRepository(BaseRepository[ShipmentItem]):
    model = ShipmentItem

    def list_by_shipment(self, shipment_id: int) -> Sequence[ShipmentItem]:
        stmt = select(ShipmentItem).where(
            ShipmentItem.shipment_id == shipment_id, ShipmentItem.deleted_at.is_(None)
        )
        return self.session.execute(stmt).scalars().all()

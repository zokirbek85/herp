"""Shartnoma statusini ortishlar hajmiga qarab avtomatik hisoblaydi (Exceldagi kabi)."""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.enums import ContractStatus
from app.models.contract import Contract
from app.repositories.shipment_item_repository import ShipmentItemRepository
from app.repositories.shipment_repository import ShipmentRepository


class ContractStatusService:
    """Bekor qilingan (CANCELLED) shartnoma statusi faqat foydalanuvchi tomonidan qo'lda
    o'zgartiriladi — avtomatik hisoblash uni qayta tiklamaydi."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self._shipment_repo = ShipmentRepository(session)
        self._item_repo = ShipmentItemRepository(session)

    def total_shipped_amount(self, contract_id: int) -> Decimal:
        total = Decimal("0")
        for shipment in self._shipment_repo.list_by_contract(contract_id):
            for item in self._item_repo.list_by_shipment(shipment.id):
                total += item.amount
        return total

    def recalculate(self, contract: Contract) -> None:
        if contract.status == ContractStatus.CANCELLED:
            return

        total_shipped = self.total_shipped_amount(contract.id)
        if total_shipped <= 0:
            contract.status = ContractStatus.NEW
        elif total_shipped >= contract.amount:
            contract.status = ContractStatus.COMPLETED
        else:
            contract.status = ContractStatus.IN_PROGRESS

        self.session.flush()

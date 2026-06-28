"""Shartnoma statusini ortishlar va to'lovlar holatiga qarab avtomatik hisoblaydi (Exceldagi kabi)."""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.enums import ContractStatus
from app.models.contract import Contract
from app.repositories.shipment_item_repository import ShipmentItemRepository
from app.repositories.shipment_repository import ShipmentRepository
from app.services.financial_summary_service import FinancialSummaryService


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
        """CANCELLED — faqat qo'lda, avtomatik tiklanmaydi.

        Qolganlar:
          NEW         — ortish ham, to'lov ham yo'q
          IN_PROGRESS — biror harakat bor, lekin to'liq emas (yoki qarz hali yopilmagan)
          COMPLETED   — yetkazish summa va (agar spetsifikatsiya kiritilgan bo'lsa) kg
                        bo'yicha 100% VA pul qarzi yo'q (`debt == 0`)
        """
        if contract.status == ContractStatus.CANCELLED:
            return

        total_shipped = self.total_shipped_amount(contract.id)
        summary = FinancialSummaryService(self.session).build(contract)

        has_any_activity = total_shipped > 0 or summary.total_paid > 0
        fully_shipped_amount = total_shipped >= contract.amount
        # Spetsifikatsiya kiritilmagan bo'lsa (planned_kg yo'q), kg bo'yicha tekshirish
        # ma'nosiz — bu holda faqat summa va qarzga qaraladi.
        fully_shipped_kg = (
            summary.total_planned_kg <= 0 or summary.total_shipped_kg >= summary.total_planned_kg
        )
        no_debt = summary.debt == Decimal("0") and summary.advance_balance >= 0

        if not has_any_activity:
            contract.status = ContractStatus.NEW
        elif fully_shipped_amount and fully_shipped_kg and no_debt:
            contract.status = ContractStatus.COMPLETED
        else:
            contract.status = ContractStatus.IN_PROGRESS

        self.session.flush()

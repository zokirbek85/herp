"""Debitorlik qarzi yoshi (aging) tahlili.

Mantiq: har bir ortish bo'yicha yopilmagan qarz (outstanding) hisoblanadi.
Ortish sanasidan bugungi sanagacha bo'lgan farq = kechikish kunlari.
Guruhlar: 0-30, 31-60, 61-90, 91+ kun.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories.contract_repository import ContractRepository
from app.repositories.contragent_repository import ContragentRepository
from app.repositories.payment_allocation_repository import PaymentAllocationRepository
from app.repositories.shipment_item_repository import ShipmentItemRepository
from app.repositories.shipment_repository import ShipmentRepository

AGING_BUCKETS: list[tuple[str, int, int | None]] = [
    ("0-30 kun", 0, 30),
    ("31-60 kun", 31, 60),
    ("61-90 kun", 61, 90),
    ("91+ kun", 91, None),
]


@dataclass(frozen=True, slots=True)
class AgingBucket:
    label: str
    min_days: int
    max_days: int | None
    amount: Decimal


@dataclass(frozen=True, slots=True)
class ContragentAgingRow:
    contragent_id: int
    contragent_name: str
    inn: str | None
    total_debt: Decimal
    buckets: list[AgingBucket]
    oldest_invoice_days: int


class AgingService:
    def __init__(self, session: Session) -> None:
        self._contract_repo = ContractRepository(session)
        self._contragent_repo = ContragentRepository(session)
        self._shipment_repo = ShipmentRepository(session)
        self._item_repo = ShipmentItemRepository(session)
        self._alloc_repo = PaymentAllocationRepository(session)

    def _days_outstanding(self, shipment_date: date, as_of: date) -> int:
        return (as_of - shipment_date).days

    def _get_bucket_index(self, days: int) -> int:
        for index, (_, _min_days, max_days) in enumerate(AGING_BUCKETS):
            if max_days is None or days <= max_days:
                return index
        return len(AGING_BUCKETS) - 1

    def build(self, as_of: date | None = None) -> list[ContragentAgingRow]:
        """Barcha kontragentlar bo'yicha aging jadvalini qaytaradi.

        `as_of`: aging hisoblanadigan sana (default: bugun). Faqat qarz > 0 bo'lgan
        kontragentlar qaytariladi.
        """
        if as_of is None:
            as_of = date.today()

        debt_by_contragent: dict[int, list[Decimal]] = {}
        oldest_by_contragent: dict[int, int] = {}

        for contract in self._contract_repo.list_all():
            for shipment in self._shipment_repo.list_by_contract(contract.id):
                total_shipped = sum(
                    (item.amount for item in self._item_repo.list_by_shipment(shipment.id)),
                    Decimal("0"),
                )
                allocated = self._alloc_repo.total_allocated_for_shipment(shipment.id)
                outstanding = max(total_shipped - allocated, Decimal("0"))
                if outstanding <= 0:
                    continue

                days = self._days_outstanding(shipment.shipment_date, as_of)
                contragent_id = contract.contragent_id

                if contragent_id not in debt_by_contragent:
                    debt_by_contragent[contragent_id] = [Decimal("0")] * len(AGING_BUCKETS)
                    oldest_by_contragent[contragent_id] = 0

                bucket_index = self._get_bucket_index(days)
                debt_by_contragent[contragent_id][bucket_index] += outstanding
                oldest_by_contragent[contragent_id] = max(oldest_by_contragent[contragent_id], days)

        rows: list[ContragentAgingRow] = []
        for contragent_id, amounts in debt_by_contragent.items():
            total = sum(amounts, Decimal("0"))
            if total <= 0:
                continue
            contragent = self._contragent_repo.get_by_id(contragent_id)
            if contragent is None:
                continue
            buckets = [
                AgingBucket(label=label, min_days=min_days, max_days=max_days, amount=amounts[index])
                for index, (label, min_days, max_days) in enumerate(AGING_BUCKETS)
            ]
            rows.append(
                ContragentAgingRow(
                    contragent_id=contragent_id,
                    contragent_name=contragent.name,
                    inn=contragent.inn,
                    total_debt=total,
                    buckets=buckets,
                    oldest_invoice_days=oldest_by_contragent[contragent_id],
                )
            )

        rows.sort(key=lambda row: row.total_debt, reverse=True)
        return rows

    def summary_by_bucket(self, as_of: date | None = None) -> list[AgingBucket]:
        """Barcha kontragentlarni birlashtirgan holda bucket yig'indisi (dashboard uchun)."""
        rows = self.build(as_of)
        totals = [Decimal("0")] * len(AGING_BUCKETS)
        for row in rows:
            for index, bucket in enumerate(row.buckets):
                totals[index] += bucket.amount
        return [
            AgingBucket(label=label, min_days=min_days, max_days=max_days, amount=totals[index])
            for index, (label, min_days, max_days) in enumerate(AGING_BUCKETS)
        ]

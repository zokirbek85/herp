"""Dashboard va Analitika moduli uchun agregatsiya hisob-kitoblari.

E'tibor: bu yerdagi metodlar butun portfolio bo'yicha to'liq skanerlash (`list_all()`)
talab qiladi — pagination'siz. Bu Dashboard/Analitika uchun tabiiy (KPI butun ma'lumotlar
asosida hisoblanishi shart), lekin juda katta hajmda (100k+ shartnoma) keyinchalik SQL
darajasidagi GROUP BY agregatsiyasiga o'tish kerak bo'lishi mumkin — hozircha to'g'rilik
va kodning soddaligi ustunlik qiladi.
"""

from dataclasses import dataclass
from decimal import Decimal

from app.core.enums import ContractStatus
from app.database.session import session_scope
from app.models.contragent import Contragent
from app.models.product import Product
from app.repositories.contract_repository import ContractRepository
from app.repositories.contragent_repository import ContragentRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.shipment_item_repository import ShipmentItemRepository
from app.repositories.shipment_repository import ShipmentRepository
from app.services.contract_status_service import ContractStatusService
from app.services.financial_summary_service import FinancialSummaryService


@dataclass(frozen=True, slots=True)
class ContragentAmountRow:
    contragent: Contragent
    amount: Decimal


@dataclass(frozen=True, slots=True)
class ProductVolumeRow:
    product: Product
    total_kg: Decimal


@dataclass(frozen=True, slots=True)
class MonthlyAmountRow:
    month: int
    total_amount: Decimal


class AnalyticsService:
    def top_debtors(self, *, limit: int = 10) -> list[ContragentAmountRow]:
        """Eng katta qarzdorlar — TOP N kontragent."""
        with session_scope() as session:
            contract_repo = ContractRepository(session)
            contragent_repo = ContragentRepository(session)
            summary_service = FinancialSummaryService(session)

            debt_by_contragent: dict[int, Decimal] = {}
            for contract in contract_repo.list_all():
                summary = summary_service.build(contract)
                if summary.debt > 0:
                    debt_by_contragent[contract.contragent_id] = (
                        debt_by_contragent.get(contract.contragent_id, Decimal("0")) + summary.debt
                    )

            rows = [
                ContragentAmountRow(contragent, debt)
                for contragent_id, debt in debt_by_contragent.items()
                if (contragent := contragent_repo.get_by_id(contragent_id)) is not None
            ]
            rows.sort(key=lambda row: row.amount, reverse=True)
            return rows[:limit]

    def top_contragents_by_shipped_amount(self, *, limit: int = 10) -> list[ContragentAmountRow]:
        """TOP 10 kontragent — eng ko'p sotuv hajmi bo'yicha."""
        with session_scope() as session:
            contract_repo = ContractRepository(session)
            contragent_repo = ContragentRepository(session)
            status_service = ContractStatusService(session)

            shipped_by_contragent: dict[int, Decimal] = {}
            for contract in contract_repo.list_all():
                shipped = status_service.total_shipped_amount(contract.id)
                if shipped > 0:
                    shipped_by_contragent[contract.contragent_id] = (
                        shipped_by_contragent.get(contract.contragent_id, Decimal("0")) + shipped
                    )

            rows = [
                ContragentAmountRow(contragent, amount)
                for contragent_id, amount in shipped_by_contragent.items()
                if (contragent := contragent_repo.get_by_id(contragent_id)) is not None
            ]
            rows.sort(key=lambda row: row.amount, reverse=True)
            return rows[:limit]

    def top_products_by_shipped_kg(self, *, limit: int = 10) -> list[ProductVolumeRow]:
        """TOP mahsulot — eng ko'p sotilgan kg bo'yicha."""
        with session_scope() as session:
            item_repo = ShipmentItemRepository(session)
            product_repo = ProductRepository(session)

            kg_by_product: dict[int, Decimal] = {}
            for item in item_repo.list_all():
                kg_by_product[item.product_id] = (
                    kg_by_product.get(item.product_id, Decimal("0")) + item.kg
                )

            rows = [
                ProductVolumeRow(product, total_kg)
                for product_id, total_kg in kg_by_product.items()
                if (product := product_repo.get_by_id(product_id)) is not None
            ]
            rows.sort(key=lambda row: row.total_kg, reverse=True)
            return rows[:limit]

    def monthly_shipped_amount(self, year: int) -> list[MonthlyAmountRow]:
        """Oylik sotuv (yetkazib berilgan summa, 1-12 oylar)."""
        with session_scope() as session:
            shipment_repo = ShipmentRepository(session)
            item_repo = ShipmentItemRepository(session)

            totals: dict[int, Decimal] = {month: Decimal("0") for month in range(1, 13)}
            for shipment in shipment_repo.list_all():
                if shipment.shipment_date.year != year:
                    continue
                for item in item_repo.list_by_shipment(shipment.id):
                    totals[shipment.shipment_date.month] += item.amount

            return [MonthlyAmountRow(month, totals[month]) for month in range(1, 13)]

    def monthly_payment_amount(self, year: int) -> list[MonthlyAmountRow]:
        """Oylik tushum (qabul qilingan to'lovlar, 1-12 oylar)."""
        with session_scope() as session:
            payment_repo = PaymentRepository(session)

            totals: dict[int, Decimal] = {month: Decimal("0") for month in range(1, 13)}
            for payment in payment_repo.list_all():
                if payment.payment_date.year != year:
                    continue
                totals[payment.payment_date.month] += payment.amount

            return [MonthlyAmountRow(month, totals[month]) for month in range(1, 13)]

    def average_price(self) -> Decimal:
        """Barcha ortishlar bo'yicha kg-vaznlangan o'rtacha narx."""
        with session_scope() as session:
            item_repo = ShipmentItemRepository(session)

            total_amount = Decimal("0")
            total_kg = Decimal("0")
            for item in item_repo.list_all():
                total_amount += item.amount
                total_kg += item.kg

            if total_kg == 0:
                return Decimal("0")
            return (total_amount / total_kg).quantize(Decimal("0.0001"))

    def contract_status_breakdown(self) -> dict[ContractStatus, int]:
        """Dashboard'dagi status donut-chart uchun: har bir status bo'yicha shartnomalar soni."""
        with session_scope() as session:
            contract_repo = ContractRepository(session)
            breakdown = {status: 0 for status in ContractStatus}
            for contract in contract_repo.list_all():
                breakdown[contract.status] += 1
            return breakdown

    def kg_debt_by_product(self) -> list[tuple[str, Decimal]]:
        """Har bir mahsulot bo'yicha barcha shartnomalardagi qolgan yetkazilmagan umumiy kg."""
        with session_scope() as session:
            contract_repo = ContractRepository(session)
            summary_service = FinancialSummaryService(session)

            remaining_by_product: dict[str, Decimal] = {}
            for contract in contract_repo.list_all():
                summary = summary_service.build(contract)
                for product_summary in summary.per_product:
                    if product_summary.remaining_kg <= 0:
                        continue
                    remaining_by_product[product_summary.product_name] = (
                        remaining_by_product.get(product_summary.product_name, Decimal("0"))
                        + product_summary.remaining_kg
                    )

            rows = list(remaining_by_product.items())
            rows.sort(key=lambda row: row[1], reverse=True)
            return rows

    def contract_completion_distribution(self) -> dict[str, int]:
        """Shartnomalar bajarilish % (kg bo'yicha) guruhlari: 0-25%, 25-50%, 50-75%, 75-99%, 100%."""
        buckets = ("0-25%", "25-50%", "50-75%", "75-99%", "100%")
        with session_scope() as session:
            contract_repo = ContractRepository(session)
            summary_service = FinancialSummaryService(session)

            distribution = dict.fromkeys(buckets, 0)
            for contract in contract_repo.list_all():
                summary = summary_service.build(contract)
                pct = summary.kg_completion_pct
                if pct >= 100:
                    distribution["100%"] += 1
                elif pct >= 75:
                    distribution["75-99%"] += 1
                elif pct >= 50:
                    distribution["50-75%"] += 1
                elif pct >= 25:
                    distribution["25-50%"] += 1
                else:
                    distribution["0-25%"] += 1
            return distribution

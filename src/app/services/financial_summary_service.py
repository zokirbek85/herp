"""Shartnoma kartochkasi/Dashboard uchun moliyaviy va tovar (kg) KPI'larni hisoblaydi
(Jami buyurtma, Jami yetkazilgan, Qoldiq, To'langan, Qarz, mahsulot bo'yicha kg qoldig'i)."""

from dataclasses import dataclass, field
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.enums import Currency
from app.models.contract import Contract
from app.repositories.contract_specification_repository import ContractSpecificationRepository
from app.repositories.payment_allocation_repository import PaymentAllocationRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.shipment_item_repository import ShipmentItemRepository
from app.repositories.shipment_repository import ShipmentRepository
from app.services.currency_service import CurrencyConversionError, CurrencyService

_UNKNOWN_PRODUCT_NAME = "Noma'lum"


@dataclass(frozen=True, slots=True)
class ProductKgSummary:
    product_id: int
    product_name: str
    planned_kg: Decimal
    shipped_kg: Decimal
    remaining_kg: Decimal
    completion_pct: Decimal


@dataclass(frozen=True, slots=True)
class ContractFinancialSummary:
    contract_amount: Decimal
    total_shipped: Decimal
    remaining_to_ship: Decimal
    total_paid: Decimal
    total_allocated_to_shipments: Decimal
    advance_balance: Decimal
    debt: Decimal
    base_currency: Currency
    total_paid_in_base: Decimal
    total_planned_kg: Decimal
    total_shipped_kg: Decimal
    total_remaining_kg: Decimal
    kg_completion_pct: Decimal
    per_product: list[ProductKgSummary] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class FinancialSummaryService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self._shipment_repo = ShipmentRepository(session)
        self._item_repo = ShipmentItemRepository(session)
        self._payment_repo = PaymentRepository(session)
        self._allocation_repo = PaymentAllocationRepository(session)
        self._spec_repo = ContractSpecificationRepository(session)
        self._product_repo = ProductRepository(session)
        self._currency_service = CurrencyService(session)

    def build(self, contract: Contract) -> ContractFinancialSummary:
        total_shipped = Decimal("0")
        total_allocated_to_shipments = Decimal("0")
        shipped_kg_by_product: dict[int, Decimal] = {}
        for shipment in self._shipment_repo.list_by_contract(contract.id):
            for item in self._item_repo.list_by_shipment(shipment.id):
                total_shipped += item.amount
                shipped_kg_by_product[item.product_id] = (
                    shipped_kg_by_product.get(item.product_id, Decimal("0")) + item.kg
                )
            total_allocated_to_shipments += self._allocation_repo.total_allocated_for_shipment(
                shipment.id
            )

        total_paid = Decimal("0")
        total_paid_in_base = Decimal("0")
        total_allocated_from_payments = Decimal("0")
        warnings: list[str] = []
        for payment in self._payment_repo.list_by_contract(contract.id):
            total_paid += payment.amount
            try:
                total_paid_in_base += self._currency_service.convert(
                    payment.amount, payment.currency, contract.currency, payment.payment_date
                )
            except CurrencyConversionError as exc:
                warnings.append(str(exc))
            total_allocated_from_payments += self._allocation_repo.total_allocated_for_payment(
                payment.id
            )

        advance_balance = total_paid_in_base - total_allocated_from_payments
        debt = total_paid_in_base - total_shipped
        remaining_to_ship = max(contract.amount - total_shipped, Decimal("0"))

        per_product = self._build_per_product_kg(contract.id, shipped_kg_by_product)
        total_planned_kg = sum((spec.planned_kg for spec in per_product), Decimal("0"))
        total_shipped_kg = sum((spec.shipped_kg for spec in per_product), Decimal("0"))
        total_remaining_kg = sum((spec.remaining_kg for spec in per_product), Decimal("0"))
        kg_completion_pct = (
            (total_shipped_kg / total_planned_kg * 100).quantize(Decimal("0.01"))
            if total_planned_kg > 0
            else Decimal("0")
        )

        return ContractFinancialSummary(
            contract_amount=contract.amount,
            total_shipped=total_shipped,
            remaining_to_ship=remaining_to_ship,
            total_paid=total_paid,
            total_allocated_to_shipments=total_allocated_to_shipments,
            advance_balance=advance_balance,
            debt=debt,
            base_currency=contract.currency,
            total_paid_in_base=total_paid_in_base,
            total_planned_kg=total_planned_kg,
            total_shipped_kg=total_shipped_kg,
            total_remaining_kg=total_remaining_kg,
            kg_completion_pct=kg_completion_pct,
            per_product=per_product,
            warnings=warnings,
        )

    def _build_per_product_kg(
        self, contract_id: int, shipped_kg_by_product: dict[int, Decimal]
    ) -> list[ProductKgSummary]:
        per_product: list[ProductKgSummary] = []
        for spec in self._spec_repo.list_by_contract(contract_id):
            shipped = shipped_kg_by_product.get(spec.product_id, Decimal("0"))
            remaining = max(spec.planned_kg - shipped, Decimal("0"))
            pct = (
                (shipped / spec.planned_kg * 100).quantize(Decimal("0.01"))
                if spec.planned_kg > 0
                else Decimal("0")
            )
            product = self._product_repo.get_by_id(spec.product_id)
            per_product.append(
                ProductKgSummary(
                    product_id=spec.product_id,
                    product_name=product.name if product is not None else _UNKNOWN_PRODUCT_NAME,
                    planned_kg=spec.planned_kg,
                    shipped_kg=shipped,
                    remaining_kg=remaining,
                    completion_pct=pct,
                )
            )
        return per_product

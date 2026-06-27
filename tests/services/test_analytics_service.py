"""AnalyticsService hisob-kitoblarini tekshiradi.

Eslatma: test bazasi butun test session davomida bitta fayl bo'lib qoladi, shuning uchun
bu testlar global "TOP1" pozitsiyasini tasdiqlamaydi — buning o'rniga natijalar ro'yxatidan
o'zining yozuvini topib, hisoblangan qiymatni tekshiradi. Oylik agregatsiya testlari boshqa
testlar bilan to'qnashmasligi uchun kelajakdagi (2099) yilni ishlatadi.
"""

import uuid
from datetime import date
from decimal import Decimal

import pytest

from app.core.enums import ContractStatus, Currency, PaymentType
from app.services.analytics_service import AnalyticsService
from app.services.contract_service import ContractService
from app.services.contragent_service import ContragentService
from app.services.dto import ShipmentItemInput
from app.services.payment_service import PaymentService
from app.services.product_service import ProductService
from app.services.shipment_service import ShipmentService

_ANALYTICS_YEAR = 2099


@pytest.fixture
def contragent_id() -> int:
    return ContragentService().create(name=f"Analytics Kontragent {uuid.uuid4().hex[:8]}").id


@pytest.fixture
def product_id() -> int:
    return ProductService().create(
        name="Analytics Mahsulot", sku=f"ANALYTICS-{uuid.uuid4().hex[:8]}"
    ).id


def test_top_debtors_includes_contract_with_outstanding_debt(contragent_id, product_id) -> None:
    contract = ContractService().create(
        contract_number=f"ANALYTICS-DEBT-{uuid.uuid4().hex[:8]}",
        contragent_id=contragent_id,
        currency=Currency.USD,
        amount=Decimal("500.00"),
        contract_date=date(_ANALYTICS_YEAR, 1, 1),
    )
    ShipmentService().create_shipment(
        contract_id=contract.id,
        shipment_number=f"ANALYTICS-DEBT-SH-{uuid.uuid4().hex[:8]}",
        shipment_date=date(_ANALYTICS_YEAR, 1, 5),
        items=[ShipmentItemInput(product_id=product_id, kg=Decimal("100.000"), price=Decimal("5.0000"))],
    )

    rows = AnalyticsService().top_debtors(limit=10_000)
    matching = [row for row in rows if row.contragent.id == contragent_id]

    assert len(matching) == 1
    assert matching[0].amount == Decimal("500.00")


def test_top_contragents_by_shipped_amount(contragent_id, product_id) -> None:
    contract = ContractService().create(
        contract_number=f"ANALYTICS-SHIP-{uuid.uuid4().hex[:8]}",
        contragent_id=contragent_id,
        currency=Currency.USD,
        amount=Decimal("1000.00"),
        contract_date=date(_ANALYTICS_YEAR, 1, 1),
    )
    ShipmentService().create_shipment(
        contract_id=contract.id,
        shipment_number=f"ANALYTICS-SHIP-SH-{uuid.uuid4().hex[:8]}",
        shipment_date=date(_ANALYTICS_YEAR, 1, 5),
        items=[ShipmentItemInput(product_id=product_id, kg=Decimal("50.000"), price=Decimal("4.0000"))],
    )

    rows = AnalyticsService().top_contragents_by_shipped_amount(limit=10_000)
    matching = [row for row in rows if row.contragent.id == contragent_id]

    assert len(matching) == 1
    assert matching[0].amount == Decimal("200.00")


def test_top_products_by_shipped_kg(contragent_id, product_id) -> None:
    contract = ContractService().create(
        contract_number=f"ANALYTICS-KG-{uuid.uuid4().hex[:8]}",
        contragent_id=contragent_id,
        currency=Currency.UZS,
        amount=Decimal("1000.00"),
        contract_date=date(_ANALYTICS_YEAR, 1, 1),
    )
    ShipmentService().create_shipment(
        contract_id=contract.id,
        shipment_number=f"ANALYTICS-KG-SH-{uuid.uuid4().hex[:8]}",
        shipment_date=date(_ANALYTICS_YEAR, 1, 5),
        items=[ShipmentItemInput(product_id=product_id, kg=Decimal("321.500"), price=Decimal("1.0000"))],
    )

    rows = AnalyticsService().top_products_by_shipped_kg(limit=10_000)
    matching = [row for row in rows if row.product.id == product_id]

    assert len(matching) == 1
    assert matching[0].total_kg == Decimal("321.500")


def test_monthly_shipped_and_payment_amounts(contragent_id, product_id) -> None:
    contract = ContractService().create(
        contract_number=f"ANALYTICS-MONTHLY-{uuid.uuid4().hex[:8]}",
        contragent_id=contragent_id,
        currency=Currency.USD,
        amount=Decimal("1000.00"),
        contract_date=date(_ANALYTICS_YEAR, 3, 1),
    )
    ShipmentService().create_shipment(
        contract_id=contract.id,
        shipment_number=f"ANALYTICS-MONTHLY-SH-{uuid.uuid4().hex[:8]}",
        shipment_date=date(_ANALYTICS_YEAR, 3, 10),
        items=[ShipmentItemInput(product_id=product_id, kg=Decimal("100.000"), price=Decimal("3.0000"))],
    )
    PaymentService().create_payment(
        contract_id=contract.id,
        payment_date=date(_ANALYTICS_YEAR, 3, 15),
        amount=Decimal("150.00"),
        payment_type=PaymentType.REGULAR,
    )

    analytics = AnalyticsService()
    monthly_shipped = analytics.monthly_shipped_amount(_ANALYTICS_YEAR)
    monthly_paid = analytics.monthly_payment_amount(_ANALYTICS_YEAR)

    assert len(monthly_shipped) == 12
    assert monthly_shipped[2].month == 3
    assert monthly_shipped[2].total_amount == Decimal("300.00")
    assert monthly_paid[2].total_amount == Decimal("150.00")


def test_contract_status_breakdown_counts_cancelled_contract(contragent_id) -> None:
    contract_service = ContractService()
    contract = contract_service.create(
        contract_number=f"ANALYTICS-STATUS-{uuid.uuid4().hex[:8]}",
        contragent_id=contragent_id,
        currency=Currency.USD,
        amount=Decimal("100.00"),
        contract_date=date(_ANALYTICS_YEAR, 1, 1),
    )
    contract_service.cancel(contract.id)

    breakdown = AnalyticsService().contract_status_breakdown()
    assert breakdown[ContractStatus.CANCELLED] >= 1
    assert sum(breakdown.values()) >= 1

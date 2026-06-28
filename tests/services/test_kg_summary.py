"""FinancialSummaryService: mahsulot bo'yicha kg rejalashtirilgan/yetkazilgan/qoldiq hisobi."""

import uuid
from datetime import date
from decimal import Decimal

import pytest

from app.core.enums import Currency
from app.services.contract_service import ContractService
from app.services.contragent_service import ContragentService
from app.services.dto import ShipmentItemInput
from app.services.product_service import ProductService
from app.services.shipment_service import ShipmentService


@pytest.fixture
def contragent_id() -> int:
    return ContragentService().create(name="Kg Summary Test Kontragent").id


def _new_product() -> int:
    sku = f"KG-SUMMARY-{uuid.uuid4().hex[:8]}"
    return ProductService().create(name="Kg Summary Mahsulot", sku=sku).id


def _new_contract(contragent_id: int) -> int:
    return ContractService().create(
        contract_number=f"KG-SUMMARY-{uuid.uuid4().hex[:8]}",
        contragent_id=contragent_id,
        currency=Currency.USD,
        amount=Decimal("10000.00"),
        contract_date=date(2026, 1, 1),
    ).id


def test_partial_shipment_computes_remaining_and_percentage(contragent_id) -> None:
    product_id = _new_product()
    contract_id = _new_contract(contragent_id)
    ContractService().add_specification(
        contract_id, product_id=product_id, planned_kg=Decimal("1000.000"), reference_price=Decimal("2.0000")
    )
    ShipmentService().create_shipment(
        contract_id=contract_id,
        shipment_number=f"KG-SH-{uuid.uuid4().hex[:8]}",
        shipment_date=date(2026, 1, 10),
        items=[ShipmentItemInput(product_id=product_id, kg=Decimal("600.000"), price=Decimal("2.0000"))],
    )

    summary = ContractService().get_financial_summary(contract_id)

    assert len(summary.per_product) == 1
    product_summary = summary.per_product[0]
    assert product_summary.planned_kg == Decimal("1000.000")
    assert product_summary.shipped_kg == Decimal("600.000")
    assert product_summary.remaining_kg == Decimal("400.000")
    assert product_summary.completion_pct == Decimal("60.00")
    assert summary.total_planned_kg == Decimal("1000.000")
    assert summary.total_shipped_kg == Decimal("600.000")
    assert summary.total_remaining_kg == Decimal("400.000")
    assert summary.kg_completion_pct == Decimal("60.00")


def test_multiple_products_are_summarized_separately(contragent_id) -> None:
    product_a = _new_product()
    product_b = _new_product()
    contract_id = _new_contract(contragent_id)
    ContractService().add_specification(
        contract_id, product_id=product_a, planned_kg=Decimal("100.000"), reference_price=Decimal("1.0000")
    )
    ContractService().add_specification(
        contract_id, product_id=product_b, planned_kg=Decimal("200.000"), reference_price=Decimal("1.0000")
    )
    ShipmentService().create_shipment(
        contract_id=contract_id,
        shipment_number=f"KG-SH-{uuid.uuid4().hex[:8]}",
        shipment_date=date(2026, 1, 10),
        items=[
            ShipmentItemInput(product_id=product_a, kg=Decimal("100.000"), price=Decimal("1.0000")),
            ShipmentItemInput(product_id=product_b, kg=Decimal("50.000"), price=Decimal("1.0000")),
        ],
    )

    summary = ContractService().get_financial_summary(contract_id)
    by_product = {p.product_id: p for p in summary.per_product}

    assert by_product[product_a].remaining_kg == Decimal("0")
    assert by_product[product_a].completion_pct == Decimal("100.00")
    assert by_product[product_b].remaining_kg == Decimal("150.000")
    assert by_product[product_b].completion_pct == Decimal("25.00")


def test_no_specification_yields_empty_per_product(contragent_id) -> None:
    contract_id = _new_contract(contragent_id)

    summary = ContractService().get_financial_summary(contract_id)

    assert summary.per_product == []
    assert summary.total_planned_kg == Decimal("0")
    assert summary.kg_completion_pct == Decimal("0")

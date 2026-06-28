"""ContractStatusService.recalculate(): to'lov trigger qiladi, COMPLETED faqat qarzsiz."""

import uuid
from datetime import date
from decimal import Decimal

import pytest

from app.core.enums import ContractStatus, Currency, PaymentType
from app.services.contract_service import ContractService
from app.services.contragent_service import ContragentService
from app.services.dto import ShipmentItemInput
from app.services.payment_service import PaymentService
from app.services.product_service import ProductService
from app.services.shipment_service import ShipmentService


@pytest.fixture
def contragent_id() -> int:
    return ContragentService().create(name="Status Test Kontragent").id


@pytest.fixture
def product_id() -> int:
    sku = f"STATUS-TEST-{uuid.uuid4().hex[:8]}"
    return ProductService().create(name="Status Test Mahsulot", sku=sku).id


def _new_contract(contragent_id: int, *, amount: Decimal = Decimal("1000.00")) -> int:
    return ContractService().create(
        contract_number=f"STATUS-{uuid.uuid4().hex[:8]}",
        contragent_id=contragent_id,
        currency=Currency.USD,
        amount=amount,
        contract_date=date(2026, 1, 1),
    ).id


def test_payment_alone_triggers_status_update(contragent_id) -> None:
    contract_id = _new_contract(contragent_id)
    contract_service = ContractService()
    assert contract_service.get(contract_id).status == ContractStatus.NEW

    PaymentService().create_payment(
        contract_id=contract_id,
        payment_date=date(2026, 1, 5),
        amount=Decimal("200.00"),
        payment_type=PaymentType.ADVANCE,
    )

    assert contract_service.get(contract_id).status == ContractStatus.IN_PROGRESS


def test_fully_shipped_and_paid_becomes_completed(contragent_id, product_id) -> None:
    contract_id = _new_contract(contragent_id, amount=Decimal("500.00"))
    shipment_service = ShipmentService()
    payment_service = PaymentService()
    contract_service = ContractService()

    shipment_service.create_shipment(
        contract_id=contract_id,
        shipment_number=f"STATUS-SH-{uuid.uuid4().hex[:8]}",
        shipment_date=date(2026, 1, 10),
        items=[ShipmentItemInput(product_id=product_id, kg=Decimal("100.000"), price=Decimal("5.0000"))],
    )
    payment_service.create_payment(
        contract_id=contract_id,
        payment_date=date(2026, 1, 11),
        amount=Decimal("500.00"),
        payment_type=PaymentType.REGULAR,
    )

    summary = contract_service.get_financial_summary(contract_id)
    assert summary.debt == Decimal("0")
    assert contract_service.get(contract_id).status == ContractStatus.COMPLETED


def test_fully_shipped_but_unpaid_stays_in_progress(contragent_id, product_id) -> None:
    contract_id = _new_contract(contragent_id, amount=Decimal("500.00"))
    shipment_service = ShipmentService()
    contract_service = ContractService()

    shipment_service.create_shipment(
        contract_id=contract_id,
        shipment_number=f"STATUS-SH-{uuid.uuid4().hex[:8]}",
        shipment_date=date(2026, 1, 10),
        items=[ShipmentItemInput(product_id=product_id, kg=Decimal("100.000"), price=Decimal("5.0000"))],
    )

    summary = contract_service.get_financial_summary(contract_id)
    assert summary.debt == Decimal("500.00")
    assert contract_service.get(contract_id).status == ContractStatus.IN_PROGRESS


def test_cancelled_status_is_not_changed_by_payment(contragent_id) -> None:
    contract_id = _new_contract(contragent_id)
    contract_service = ContractService()
    contract_service.cancel(contract_id)
    assert contract_service.get(contract_id).status == ContractStatus.CANCELLED

    PaymentService().create_payment(
        contract_id=contract_id,
        payment_date=date(2026, 1, 5),
        amount=Decimal("100.00"),
        payment_type=PaymentType.ADVANCE,
    )

    assert contract_service.get(contract_id).status == ContractStatus.CANCELLED

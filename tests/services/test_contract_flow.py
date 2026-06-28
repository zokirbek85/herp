"""ContractService/ShipmentService/PaymentService orqali to'liq biznes oqimi: FIFO va status."""

import uuid
from datetime import date
from decimal import Decimal

import pytest

from app.core.enums import ContractStatus, Currency, PaymentType
from app.core.exceptions import DuplicateError, ValidationError
from app.services.contract_service import ContractService
from app.services.contragent_service import ContragentService
from app.services.dto import ShipmentItemInput
from app.services.payment_service import PaymentService
from app.services.product_service import ProductService
from app.services.shipment_service import ShipmentService


@pytest.fixture
def contragent_id() -> int:
    return ContragentService().create(name="FIFO Flow Kontragent").id


@pytest.fixture
def product_id() -> int:
    sku = f"FIFO-FLOW-COTTON-{uuid.uuid4().hex[:8]}"
    return ProductService().create(name="Paxta tolasi", sku=sku).id


def _new_contract(contragent_id: int, *, amount: Decimal = Decimal("1000.00")) -> int:
    contract = ContractService().create(
        contract_number=f"FIFO-{amount}-{contragent_id}-{uuid.uuid4().hex[:8]}",
        contragent_id=contragent_id,
        currency=Currency.USD,
        amount=amount,
        contract_date=date(2026, 1, 1),
    )
    return contract.id


def test_fifo_allocates_advance_payment_to_later_shipment(contragent_id, product_id) -> None:
    contract_id = _new_contract(contragent_id)
    payment_service = PaymentService()
    shipment_service = ShipmentService()
    contract_service = ContractService()

    # Avans: hali ortish yo'q, to'liq taqsimlanmagan holda qoladi.
    payment_service.create_payment(
        contract_id=contract_id,
        payment_date=date(2026, 1, 5),
        amount=Decimal("500.00"),
        payment_type=PaymentType.ADVANCE,
    )
    summary = contract_service.get_financial_summary(contract_id)
    assert summary.advance_balance == Decimal("500.00")
    assert summary.debt == Decimal("0")

    # Birinchi ortish: avans avtomatik yopiladi, 100 qarz qoladi.
    shipment_service.create_shipment(
        contract_id=contract_id,
        shipment_number=f"SH-{contract_id}-1",
        shipment_date=date(2026, 1, 10),
        items=[ShipmentItemInput(product_id=product_id, kg=Decimal("240.000"), price=Decimal("2.5000"))],
    )
    summary = contract_service.get_financial_summary(contract_id)
    assert summary.total_shipped == Decimal("600.00")
    assert summary.advance_balance == Decimal("0")
    assert summary.debt == Decimal("100.00")

    contract = contract_service.get(contract_id)
    assert contract.status == ContractStatus.IN_PROGRESS

    # Ikkinchi ortish: hali to'lov yo'q, butunlay qarz bo'lib qo'shiladi.
    shipment_service.create_shipment(
        contract_id=contract_id,
        shipment_number=f"SH-{contract_id}-2",
        shipment_date=date(2026, 1, 20),
        items=[ShipmentItemInput(product_id=product_id, kg=Decimal("160.000"), price=Decimal("2.5000"))],
    )
    summary = contract_service.get_financial_summary(contract_id)
    assert summary.total_shipped == Decimal("1000.00")
    assert summary.debt == Decimal("500.00")

    # Yangi to'lov: FIFO bo'yicha avval birinchi ortishning qolgan 100'i, keyin ikkinchisi yopiladi.
    payment_service.create_payment(
        contract_id=contract_id,
        payment_date=date(2026, 2, 1),
        amount=Decimal("300.00"),
        payment_type=PaymentType.REGULAR,
    )
    summary = contract_service.get_financial_summary(contract_id)
    assert summary.total_paid == Decimal("800.00")
    assert summary.debt == Decimal("200.00")
    assert summary.advance_balance == Decimal("0")

    # To'liq yetkazilgan bo'lsa-da, qarz (200) hali yopilmagani uchun COMPLETED emas.
    contract = contract_service.get(contract_id)
    assert contract.status == ContractStatus.IN_PROGRESS

    # Qarzni butunlay yopadigan yakuniy to'lov — endi yetkazish ham, to'lov ham 100%.
    payment_service.create_payment(
        contract_id=contract_id,
        payment_date=date(2026, 2, 10),
        amount=Decimal("200.00"),
        payment_type=PaymentType.REGULAR,
    )
    summary = contract_service.get_financial_summary(contract_id)
    assert summary.debt == Decimal("0")

    contract = contract_service.get(contract_id)
    assert contract.status == ContractStatus.COMPLETED


def test_cancelled_contract_status_is_not_overwritten_by_recalculation(
    contragent_id, product_id
) -> None:
    contract_id = _new_contract(contragent_id, amount=Decimal("500.00"))
    contract_service = ContractService()
    shipment_service = ShipmentService()

    contract_service.cancel(contract_id)
    assert contract_service.get(contract_id).status == ContractStatus.CANCELLED

    with pytest.raises(ValidationError):
        shipment_service.create_shipment(
            contract_id=contract_id,
            shipment_number=f"SH-{contract_id}-CANCELLED",
            shipment_date=date(2026, 1, 10),
            items=[ShipmentItemInput(product_id=product_id, kg=Decimal("10.000"), price=Decimal("1.0000"))],
        )


def test_duplicate_contract_number_is_rejected(contragent_id) -> None:
    contract_service = ContractService()
    contract_service.create(
        contract_number="DUP-001",
        contragent_id=contragent_id,
        currency=Currency.UZS,
        amount=Decimal("100.00"),
        contract_date=date(2026, 1, 1),
    )
    with pytest.raises(DuplicateError):
        contract_service.create(
            contract_number="DUP-001",
            contragent_id=contragent_id,
            currency=Currency.UZS,
            amount=Decimal("200.00"),
            contract_date=date(2026, 1, 2),
        )


def test_duplicate_specification_for_same_product_is_rejected(contragent_id, product_id) -> None:
    contract_id = _new_contract(contragent_id)
    contract_service = ContractService()
    contract_service.add_specification(
        contract_id, product_id=product_id, planned_kg=Decimal("100.000"), reference_price=Decimal("2.0000")
    )
    with pytest.raises(DuplicateError):
        contract_service.add_specification(
            contract_id,
            product_id=product_id,
            planned_kg=Decimal("50.000"),
            reference_price=Decimal("2.0000"),
        )


def test_negative_payment_amount_is_rejected(contragent_id) -> None:
    contract_id = _new_contract(contragent_id)
    with pytest.raises(ValidationError):
        PaymentService().create_payment(
            contract_id=contract_id,
            payment_date=date(2026, 1, 1),
            amount=Decimal("-10.00"),
            payment_type=PaymentType.REGULAR,
        )

"""ShipmentService: validatsiya va NotFoundError/DuplicateError yo'llari."""

import uuid
from datetime import date
from decimal import Decimal

import pytest

from app.core.enums import Currency
from app.core.exceptions import DuplicateError, NotFoundError, ValidationError
from app.services.contract_service import ContractService
from app.services.contragent_service import ContragentService
from app.services.dto import ShipmentItemInput
from app.services.product_service import ProductService
from app.services.shipment_service import ShipmentService


@pytest.fixture
def contract_id() -> int:
    contragent_id = ContragentService().create(name="Shipment Service Test Kontragent").id
    return ContractService().create(
        contract_number=f"SHIP-SVC-{uuid.uuid4().hex[:8]}",
        contragent_id=contragent_id,
        currency=Currency.USD,
        amount=Decimal("1000.00"),
        contract_date=date(2026, 1, 1),
    ).id


@pytest.fixture
def product_id() -> int:
    sku = f"SHIP-SVC-PRODUCT-{uuid.uuid4().hex[:8]}"
    return ProductService().create(name="Test Mahsulot", sku=sku).id


def test_create_shipment_with_no_items_raises_validation_error(contract_id) -> None:
    with pytest.raises(ValidationError):
        ShipmentService().create_shipment(
            contract_id=contract_id,
            shipment_number=f"EMPTY-{uuid.uuid4().hex[:8]}",
            shipment_date=date(2026, 1, 10),
            items=[],
        )


def test_create_shipment_with_nonexistent_contract_raises_not_found(product_id) -> None:
    with pytest.raises(NotFoundError):
        ShipmentService().create_shipment(
            contract_id=999_999,
            shipment_number=f"NOCONTRACT-{uuid.uuid4().hex[:8]}",
            shipment_date=date(2026, 1, 10),
            items=[ShipmentItemInput(product_id=product_id, kg=Decimal("10.000"), price=Decimal("1.0000"))],
        )


def test_create_shipment_with_nonexistent_product_raises_not_found(contract_id) -> None:
    with pytest.raises(NotFoundError):
        ShipmentService().create_shipment(
            contract_id=contract_id,
            shipment_number=f"NOPRODUCT-{uuid.uuid4().hex[:8]}",
            shipment_date=date(2026, 1, 10),
            items=[ShipmentItemInput(product_id=999_999, kg=Decimal("10.000"), price=Decimal("1.0000"))],
        )


def test_create_shipment_with_non_positive_item_values_raises_validation_error(
    contract_id, product_id
) -> None:
    with pytest.raises(ValidationError):
        ShipmentService().create_shipment(
            contract_id=contract_id,
            shipment_number=f"BADKG-{uuid.uuid4().hex[:8]}",
            shipment_date=date(2026, 1, 10),
            items=[ShipmentItemInput(product_id=product_id, kg=Decimal("0"), price=Decimal("1.0000"))],
        )
    with pytest.raises(ValidationError):
        ShipmentService().create_shipment(
            contract_id=contract_id,
            shipment_number=f"BADPRICE-{uuid.uuid4().hex[:8]}",
            shipment_date=date(2026, 1, 10),
            items=[ShipmentItemInput(product_id=product_id, kg=Decimal("10.000"), price=Decimal("0"))],
        )


def test_duplicate_shipment_number_raises_duplicate_error(contract_id, product_id) -> None:
    shipment_number = f"SHIPDUP-{uuid.uuid4().hex[:8]}"
    ShipmentService().create_shipment(
        contract_id=contract_id,
        shipment_number=shipment_number,
        shipment_date=date(2026, 1, 10),
        items=[ShipmentItemInput(product_id=product_id, kg=Decimal("10.000"), price=Decimal("1.0000"))],
    )
    with pytest.raises(DuplicateError):
        ShipmentService().create_shipment(
            contract_id=contract_id,
            shipment_number=shipment_number,
            shipment_date=date(2026, 1, 11),
            items=[ShipmentItemInput(product_id=product_id, kg=Decimal("5.000"), price=Decimal("1.0000"))],
        )


def test_get_nonexistent_shipment_raises_not_found() -> None:
    with pytest.raises(NotFoundError):
        ShipmentService().get(999_999)


def test_update_shipment_changes_items_and_recalculates_debt(contract_id, product_id) -> None:
    from app.core.enums import PaymentType
    from app.services.contract_service import ContractService
    from app.services.payment_service import PaymentService

    shipment = ShipmentService().create_shipment(
        contract_id=contract_id,
        shipment_number=f"UPDATE-SHIP-{uuid.uuid4().hex[:8]}",
        shipment_date=date(2026, 1, 10),
        items=[ShipmentItemInput(product_id=product_id, kg=Decimal("10.000"), price=Decimal("1.0000"))],
    )
    PaymentService().create_payment(
        contract_id=contract_id,
        payment_date=date(2026, 1, 11),
        amount=Decimal("10.00"),
        payment_type=PaymentType.REGULAR,
    )
    summary = ContractService().get_financial_summary(contract_id)
    assert summary.debt == Decimal("0")

    ShipmentService().update_shipment(
        shipment.id,
        shipment_number=shipment.shipment_number,
        shipment_date=date(2026, 1, 10),
        items=[ShipmentItemInput(product_id=product_id, kg=Decimal("20.000"), price=Decimal("1.0000"))],
    )

    summary = ContractService().get_financial_summary(contract_id)
    assert summary.total_shipped == Decimal("20.00")
    assert summary.debt == Decimal("-10.00")


def test_delete_shipment_frees_payment_allocation(contract_id, product_id) -> None:
    from app.core.enums import PaymentType
    from app.services.contract_service import ContractService
    from app.services.payment_service import PaymentService

    shipment = ShipmentService().create_shipment(
        contract_id=contract_id,
        shipment_number=f"DELETE-SHIP-{uuid.uuid4().hex[:8]}",
        shipment_date=date(2026, 1, 10),
        items=[ShipmentItemInput(product_id=product_id, kg=Decimal("10.000"), price=Decimal("1.0000"))],
    )
    PaymentService().create_payment(
        contract_id=contract_id,
        payment_date=date(2026, 1, 11),
        amount=Decimal("10.00"),
        payment_type=PaymentType.REGULAR,
    )
    summary = ContractService().get_financial_summary(contract_id)
    assert summary.debt == Decimal("0")
    assert summary.advance_balance == Decimal("0")

    ShipmentService().soft_delete(shipment.id)

    summary = ContractService().get_financial_summary(contract_id)
    assert summary.total_shipped == Decimal("0")
    assert summary.advance_balance == Decimal("10.00")


def test_update_nonexistent_shipment_raises_not_found(product_id) -> None:
    with pytest.raises(NotFoundError):
        ShipmentService().update_shipment(
            999_999,
            shipment_number=f"UPDATE-NOTFOUND-{uuid.uuid4().hex[:8]}",
            shipment_date=date(2026, 1, 10),
            items=[ShipmentItemInput(product_id=product_id, kg=Decimal("10.000"), price=Decimal("1.0000"))],
        )

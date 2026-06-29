"""ContractService: NotFoundError va ValidationError yo'llari hozirgi testlarda yo'q edi."""

import uuid
from datetime import date
from decimal import Decimal

import pytest

from app.core.enums import Currency
from app.core.exceptions import DuplicateError, NotFoundError, ValidationError
from app.services.contract_service import ContractService
from app.services.contragent_service import ContragentService
from app.services.product_service import ProductService


@pytest.fixture
def contragent_id() -> int:
    return ContragentService().create(name="Contract Service Test Kontragent").id


@pytest.fixture
def product_id() -> int:
    sku = f"CONTRACT-SVC-{uuid.uuid4().hex[:8]}"
    return ProductService().create(name="Test Mahsulot", sku=sku).id


def test_create_with_nonexistent_contragent_raises_not_found() -> None:
    with pytest.raises(NotFoundError):
        ContractService().create(
            contract_number=f"NOTFOUND-{uuid.uuid4().hex[:8]}",
            contragent_id=999_999,
            currency=Currency.USD,
            amount=Decimal("100.00"),
            contract_date=date(2026, 1, 1),
        )


def test_create_with_zero_or_negative_amount_raises_validation_error(contragent_id) -> None:
    for amount in (Decimal("0"), Decimal("-1.00")):
        with pytest.raises(ValidationError):
            ContractService().create(
                contract_number=f"BADAMOUNT-{uuid.uuid4().hex[:8]}",
                contragent_id=contragent_id,
                currency=Currency.USD,
                amount=amount,
                contract_date=date(2026, 1, 1),
            )


def test_add_specification_to_nonexistent_contract_raises_not_found(product_id) -> None:
    with pytest.raises(NotFoundError):
        ContractService().add_specification(
            999_999,
            product_id=product_id,
            planned_kg=Decimal("100.000"),
            reference_price=Decimal("2.0000"),
        )


def test_add_specification_with_nonexistent_product_raises_not_found(contragent_id) -> None:
    contract = ContractService().create(
        contract_number=f"SPEC-NOPRODUCT-{uuid.uuid4().hex[:8]}",
        contragent_id=contragent_id,
        currency=Currency.USD,
        amount=Decimal("100.00"),
        contract_date=date(2026, 1, 1),
    )
    with pytest.raises(NotFoundError):
        ContractService().add_specification(
            contract.id,
            product_id=999_999,
            planned_kg=Decimal("100.000"),
            reference_price=Decimal("2.0000"),
        )


def test_add_specification_with_non_positive_values_raises_validation_error(
    contragent_id, product_id
) -> None:
    contract = ContractService().create(
        contract_number=f"SPEC-BADVALUE-{uuid.uuid4().hex[:8]}",
        contragent_id=contragent_id,
        currency=Currency.USD,
        amount=Decimal("100.00"),
        contract_date=date(2026, 1, 1),
    )
    with pytest.raises(ValidationError):
        ContractService().add_specification(
            contract.id,
            product_id=product_id,
            planned_kg=Decimal("0"),
            reference_price=Decimal("2.0000"),
        )
    with pytest.raises(ValidationError):
        ContractService().add_specification(
            contract.id,
            product_id=product_id,
            planned_kg=Decimal("100.000"),
            reference_price=Decimal("0"),
        )


def test_get_nonexistent_contract_raises_not_found() -> None:
    with pytest.raises(NotFoundError):
        ContractService().get(999_999)


def test_cancel_nonexistent_contract_raises_not_found() -> None:
    with pytest.raises(NotFoundError):
        ContractService().cancel(999_999)


def test_update_nonexistent_contract_raises_not_found(contragent_id) -> None:
    with pytest.raises(NotFoundError):
        ContractService().update(
            999_999,
            contract_number=f"UPDATE-NOTFOUND-{uuid.uuid4().hex[:8]}",
            contragent_id=contragent_id,
            currency=Currency.USD,
            amount=Decimal("100.00"),
            contract_date=date(2026, 1, 1),
        )


def test_update_changes_fields(contragent_id) -> None:
    contract = ContractService().create(
        contract_number=f"UPDATE-{uuid.uuid4().hex[:8]}",
        contragent_id=contragent_id,
        currency=Currency.USD,
        amount=Decimal("100.00"),
        contract_date=date(2026, 1, 1),
    )
    new_number = f"UPDATED-{uuid.uuid4().hex[:8]}"
    updated = ContractService().update(
        contract.id,
        contract_number=new_number,
        contragent_id=contragent_id,
        currency=Currency.UZS,
        amount=Decimal("250.00"),
        contract_date=date(2026, 2, 1),
        notes="updated",
    )
    assert updated.contract_number == new_number
    assert updated.currency == Currency.UZS
    assert updated.amount == Decimal("250.00")
    assert updated.notes == "updated"


def test_update_with_duplicate_contract_number_raises_duplicate_error(contragent_id) -> None:
    first = ContractService().create(
        contract_number=f"DUP-A-{uuid.uuid4().hex[:8]}",
        contragent_id=contragent_id,
        currency=Currency.USD,
        amount=Decimal("100.00"),
        contract_date=date(2026, 1, 1),
    )
    second = ContractService().create(
        contract_number=f"DUP-B-{uuid.uuid4().hex[:8]}",
        contragent_id=contragent_id,
        currency=Currency.USD,
        amount=Decimal("100.00"),
        contract_date=date(2026, 1, 1),
    )
    with pytest.raises(DuplicateError):
        ContractService().update(
            second.id,
            contract_number=first.contract_number,
            contragent_id=contragent_id,
            currency=Currency.USD,
            amount=Decimal("100.00"),
            contract_date=date(2026, 1, 1),
        )


def test_delete_contract_with_no_activity_succeeds(contragent_id) -> None:
    contract = ContractService().create(
        contract_number=f"DELETE-{uuid.uuid4().hex[:8]}",
        contragent_id=contragent_id,
        currency=Currency.USD,
        amount=Decimal("100.00"),
        contract_date=date(2026, 1, 1),
    )
    ContractService().soft_delete(contract.id)
    with pytest.raises(NotFoundError):
        ContractService().get(contract.id)


def test_delete_contract_with_shipments_raises_validation_error(contragent_id, product_id) -> None:
    from app.services.dto import ShipmentItemInput
    from app.services.shipment_service import ShipmentService

    contract = ContractService().create(
        contract_number=f"DELETE-BLOCKED-{uuid.uuid4().hex[:8]}",
        contragent_id=contragent_id,
        currency=Currency.USD,
        amount=Decimal("100.00"),
        contract_date=date(2026, 1, 1),
    )
    ShipmentService().create_shipment(
        contract_id=contract.id,
        shipment_number=f"DELETE-BLOCKED-SHIP-{uuid.uuid4().hex[:8]}",
        shipment_date=date(2026, 1, 5),
        items=[ShipmentItemInput(product_id=product_id, kg=Decimal("10.000"), price=Decimal("1.0000"))],
    )
    with pytest.raises(ValidationError):
        ContractService().soft_delete(contract.id)

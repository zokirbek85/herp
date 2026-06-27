"""ContractService: NotFoundError va ValidationError yo'llari hozirgi testlarda yo'q edi."""

import uuid
from datetime import date
from decimal import Decimal

import pytest

from app.core.enums import Currency
from app.core.exceptions import NotFoundError, ValidationError
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

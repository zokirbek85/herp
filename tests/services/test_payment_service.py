"""PaymentService: NotFoundError yo'li hozirgi testlarda yo'q edi."""

import uuid
from datetime import date
from decimal import Decimal

import pytest

from app.core.enums import Currency, PaymentType
from app.core.exceptions import NotFoundError, ValidationError
from app.services.contract_service import ContractService
from app.services.contragent_service import ContragentService
from app.services.payment_service import PaymentService


def test_create_payment_with_nonexistent_contract_raises_not_found() -> None:
    with pytest.raises(NotFoundError):
        PaymentService().create_payment(
            contract_id=999_999,
            payment_date=date(2026, 1, 1),
            amount=Decimal("100.00"),
            payment_type=PaymentType.REGULAR,
        )


def test_payment_currency_is_inherited_from_contract() -> None:
    contragent_id = ContragentService().create(name="Payment Currency Test Kontragent").id
    contract = ContractService().create(
        contract_number=f"PAY-CURRENCY-{uuid.uuid4().hex[:8]}",
        contragent_id=contragent_id,
        currency=Currency.UZS,
        amount=Decimal("1000.00"),
        contract_date=date(2026, 1, 1),
    )

    payment = PaymentService().create_payment(
        contract_id=contract.id,
        payment_date=date(2026, 1, 5),
        amount=Decimal("100.00"),
        payment_type=PaymentType.ADVANCE,
    )

    assert payment.currency == Currency.UZS


def test_update_nonexistent_payment_raises_not_found() -> None:
    with pytest.raises(NotFoundError):
        PaymentService().update_payment(
            999_999,
            payment_date=date(2026, 1, 1),
            amount=Decimal("100.00"),
            payment_type=PaymentType.REGULAR,
        )


def test_update_payment_with_non_positive_amount_raises_validation_error() -> None:
    contragent_id = ContragentService().create(name="Payment Update Test Kontragent").id
    contract = ContractService().create(
        contract_number=f"PAY-UPDATE-{uuid.uuid4().hex[:8]}",
        contragent_id=contragent_id,
        currency=Currency.USD,
        amount=Decimal("1000.00"),
        contract_date=date(2026, 1, 1),
    )
    payment = PaymentService().create_payment(
        contract_id=contract.id,
        payment_date=date(2026, 1, 5),
        amount=Decimal("100.00"),
        payment_type=PaymentType.REGULAR,
    )
    with pytest.raises(ValidationError):
        PaymentService().update_payment(
            payment.id,
            payment_date=date(2026, 1, 5),
            amount=Decimal("0"),
            payment_type=PaymentType.REGULAR,
        )


def test_update_payment_amount_recalculates_contract_debt() -> None:
    contragent_id = ContragentService().create(name="Payment Update Debt Test Kontragent").id
    contract = ContractService().create(
        contract_number=f"PAY-UPDATE-DEBT-{uuid.uuid4().hex[:8]}",
        contragent_id=contragent_id,
        currency=Currency.USD,
        amount=Decimal("1000.00"),
        contract_date=date(2026, 1, 1),
    )
    payment = PaymentService().create_payment(
        contract_id=contract.id,
        payment_date=date(2026, 1, 5),
        amount=Decimal("100.00"),
        payment_type=PaymentType.ADVANCE,
    )
    summary = ContractService().get_financial_summary(contract.id)
    assert summary.advance_balance == Decimal("100.00")

    PaymentService().update_payment(
        payment.id,
        payment_date=date(2026, 1, 5),
        amount=Decimal("50.00"),
        payment_type=PaymentType.ADVANCE,
    )
    summary = ContractService().get_financial_summary(contract.id)
    assert summary.advance_balance == Decimal("50.00")


def test_delete_payment_removes_advance_balance() -> None:
    contragent_id = ContragentService().create(name="Payment Delete Test Kontragent").id
    contract = ContractService().create(
        contract_number=f"PAY-DELETE-{uuid.uuid4().hex[:8]}",
        contragent_id=contragent_id,
        currency=Currency.USD,
        amount=Decimal("1000.00"),
        contract_date=date(2026, 1, 1),
    )
    payment = PaymentService().create_payment(
        contract_id=contract.id,
        payment_date=date(2026, 1, 5),
        amount=Decimal("100.00"),
        payment_type=PaymentType.ADVANCE,
    )
    PaymentService().soft_delete(payment.id)

    with pytest.raises(NotFoundError):
        PaymentService().get(payment.id)
    summary = ContractService().get_financial_summary(contract.id)
    assert summary.advance_balance == Decimal("0")

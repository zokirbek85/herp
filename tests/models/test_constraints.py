"""DB darajasidagi unique/nullable constraint'lar — Service qatlamini chetlab o'tib tekshiriladi."""

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.enums import ContractStatus, Currency
from app.database.session import session_scope
from app.models import Contract, Contragent, Product, User
from app.repositories import ContractRepository, ContragentRepository, ProductRepository, UserRepository


def test_duplicate_contract_number_raises_integrity_error_at_db_level() -> None:
    with session_scope() as session:
        contragent = ContragentRepository(session).add(Contragent(name="Constraint Test Kontragent"))
        contragent_id = contragent.id

    with session_scope() as session:
        ContractRepository(session).add(
            Contract(
                contract_number="CONSTRAINT-DUP-001",
                contragent_id=contragent_id,
                currency=Currency.USD,
                amount=Decimal("100.00"),
                contract_date=date(2026, 1, 1),
                status=ContractStatus.NEW,
            )
        )

    with pytest.raises(IntegrityError):
        with session_scope() as session:
            ContractRepository(session).add(
                Contract(
                    contract_number="CONSTRAINT-DUP-001",
                    contragent_id=contragent_id,
                    currency=Currency.USD,
                    amount=Decimal("200.00"),
                    contract_date=date(2026, 1, 2),
                    status=ContractStatus.NEW,
                )
            )


def test_duplicate_product_sku_raises_integrity_error_at_db_level() -> None:
    with session_scope() as session:
        ProductRepository(session).add(Product(name="Mahsulot A", sku="CONSTRAINT-SKU-1"))

    with pytest.raises(IntegrityError):
        with session_scope() as session:
            ProductRepository(session).add(Product(name="Mahsulot B", sku="CONSTRAINT-SKU-1"))


def test_duplicate_username_raises_integrity_error_at_db_level() -> None:
    with session_scope() as session:
        UserRepository(session).add(User(full_name="Birinchi Foydalanuvchi", username="constraint.user"))

    with pytest.raises(IntegrityError):
        with session_scope() as session:
            UserRepository(session).add(User(full_name="Ikkinchi Foydalanuvchi", username="constraint.user"))


def test_contract_without_required_field_raises_integrity_error() -> None:
    with session_scope() as session:
        contragent = ContragentRepository(session).add(Contragent(name="Nullable Test Kontragent"))
        contragent_id = contragent.id

    with pytest.raises(IntegrityError):
        with session_scope() as session:
            ContractRepository(session).add(
                Contract(
                    contract_number="CONSTRAINT-NULL-001",
                    contragent_id=contragent_id,
                    currency=Currency.USD,
                    amount=None,
                    contract_date=date(2026, 1, 1),
                    status=ContractStatus.NEW,
                )
            )

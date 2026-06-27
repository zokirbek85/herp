from datetime import date
from decimal import Decimal

import pytest

from app.core.enums import Currency
from app.core.exceptions import DuplicateError, ValidationError
from app.services.contract_service import ContractService
from app.services.contragent_service import ContragentService
from app.services.product_service import ProductService


def test_duplicate_inn_is_rejected() -> None:
    service = ContragentService()
    service.create(name="Birinchi MCHJ", inn="111222333")
    with pytest.raises(DuplicateError):
        service.create(name="Ikkinchi MCHJ", inn="111222333")


def test_duplicate_sku_is_rejected() -> None:
    service = ProductService()
    service.create(name="Mahsulot A", sku="SKU-X")
    with pytest.raises(DuplicateError):
        service.create(name="Mahsulot B", sku="SKU-X")


def test_cannot_soft_delete_contragent_with_active_contract() -> None:
    contragent_service = ContragentService()
    contract_service = ContractService()

    contragent = contragent_service.create(name="Faol shartnomali kontragent")
    contract_service.create(
        contract_number="GUARD-001",
        contragent_id=contragent.id,
        currency=Currency.USD,
        amount=Decimal("100.00"),
        contract_date=date(2026, 1, 1),
    )

    with pytest.raises(ValidationError):
        contragent_service.soft_delete(contragent.id)


def test_update_contragent_changes_fields() -> None:
    service = ContragentService()
    contragent = service.create(name="Eski nom")
    updated = service.update(
        contragent.id,
        name="Yangi nom",
        inn=None,
        phone="+998901234567",
        address=None,
        contact_person=None,
        notes=None,
        is_active=True,
    )
    assert updated.name == "Yangi nom"
    assert updated.phone == "+998901234567"

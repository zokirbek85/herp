"""AgingService: debitorlik qarzi yoshi (0-30/31-60/61-90/91+ kun) guruhlanishi.

`build()`/`summary_by_bucket()` butun portfolio bo'yicha global ro'yxat qaytaradi (boshqa
testlar ham shu umumiy DB'ga shartnoma/ortish qo'shadi) — shu sababli har bir test natijani
har doim o'z `contragent_id`si bo'yicha filtrlab tekshiradi, global ro'yxatning uzunligi yoki
birinchi elementiga tayanmaydi.
"""

import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.core.enums import Currency
from app.database.session import session_scope
from app.services.aging_service import AgingService
from app.services.contract_service import ContractService
from app.services.contragent_service import ContragentService
from app.services.dto import ShipmentItemInput
from app.services.product_service import ProductService
from app.services.shipment_service import ShipmentService


@pytest.fixture
def contragent_id() -> int:
    return ContragentService().create(name="Aging Test Kontragent").id


@pytest.fixture
def product_id() -> int:
    sku = f"AGING-TEST-{uuid.uuid4().hex[:8]}"
    return ProductService().create(name="Aging Test Mahsulot", sku=sku).id


def _new_contract(contragent_id: int, *, amount: Decimal = Decimal("100000.00")) -> int:
    return ContractService().create(
        contract_number=f"AGING-{uuid.uuid4().hex[:8]}",
        contragent_id=contragent_id,
        currency=Currency.USD,
        amount=amount,
        contract_date=date(2026, 1, 1),
    ).id


def _ship(contract_id: int, product_id: int, shipment_date: date, amount: Decimal) -> None:
    ShipmentService().create_shipment(
        contract_id=contract_id,
        shipment_number=f"AGING-SH-{uuid.uuid4().hex[:8]}",
        shipment_date=shipment_date,
        items=[ShipmentItemInput(product_id=product_id, kg=amount, price=Decimal("1.0000"))],
    )


def _row_for(rows, contragent_id: int):
    matching = [row for row in rows if row.contragent_id == contragent_id]
    assert len(matching) == 1
    return matching[0]


def test_shipment_45_days_old_falls_in_31_60_bucket(contragent_id, product_id) -> None:
    as_of = date(2026, 6, 1)
    shipment_date = as_of - timedelta(days=45)
    contract_id = _new_contract(contragent_id)
    _ship(contract_id, product_id, shipment_date, Decimal("1000.00"))

    with session_scope() as session:
        rows = AgingService(session).build(as_of)

    row = _row_for(rows, contragent_id)
    assert row.total_debt == Decimal("1000.00")
    assert row.buckets[0].amount == Decimal("0")
    assert row.buckets[1].amount == Decimal("1000.00")
    assert row.buckets[2].amount == Decimal("0")
    assert row.buckets[3].amount == Decimal("0")
    assert row.oldest_invoice_days == 45


def test_fully_paid_shipment_does_not_appear_in_aging(contragent_id, product_id) -> None:
    from app.core.enums import PaymentType
    from app.services.payment_service import PaymentService

    contract_id = _new_contract(contragent_id)
    _ship(contract_id, product_id, date(2026, 1, 1), Decimal("500.00"))
    PaymentService().create_payment(
        contract_id=contract_id,
        payment_date=date(2026, 1, 2),
        amount=Decimal("500.00"),
        payment_type=PaymentType.REGULAR,
    )

    with session_scope() as session:
        rows = AgingService(session).build(date(2026, 6, 1))

    assert all(row.contragent_id != contragent_id for row in rows)


def test_multiple_contracts_for_same_contragent_are_aggregated(contragent_id, product_id) -> None:
    as_of = date(2026, 6, 1)
    contract_1 = _new_contract(contragent_id)
    contract_2 = _new_contract(contragent_id)
    _ship(contract_1, product_id, as_of - timedelta(days=10), Decimal("300.00"))
    _ship(contract_2, product_id, as_of - timedelta(days=10), Decimal("200.00"))

    with session_scope() as session:
        rows = AgingService(session).build(as_of)

    row = _row_for(rows, contragent_id)
    assert row.total_debt == Decimal("500.00")


def test_summary_by_bucket_matches_sum_of_all_rows(contragent_id, product_id) -> None:
    """Bucket'lar yig'indisi butun portfolio bo'yicha barcha qatorlar yig'indisiga teng
    bo'lishi kerak — yangi shartnoma qo'shilishi bu invariantni buzmasligini tekshiradi."""
    as_of = date(2026, 6, 1)
    contract_id = _new_contract(contragent_id)
    _ship(contract_id, product_id, as_of - timedelta(days=10), Decimal("100.00"))
    _ship(contract_id, product_id, as_of - timedelta(days=50), Decimal("200.00"))
    _ship(contract_id, product_id, as_of - timedelta(days=200), Decimal("300.00"))

    with session_scope() as session:
        service = AgingService(session)
        rows = service.build(as_of)
        summary = service.summary_by_bucket(as_of)

    total_from_rows = sum((row.total_debt for row in rows), Decimal("0"))
    total_from_summary = sum((bucket.amount for bucket in summary), Decimal("0"))
    assert total_from_rows == total_from_summary

    our_row = _row_for(rows, contragent_id)
    assert our_row.total_debt == Decimal("600.00")


def test_as_of_parameter_changes_bucket_assignment(contragent_id, product_id) -> None:
    shipment_date = date(2026, 1, 1)
    contract_id = _new_contract(contragent_id)
    _ship(contract_id, product_id, shipment_date, Decimal("100.00"))

    with session_scope() as session:
        service = AgingService(session)
        early_rows = service.build(shipment_date + timedelta(days=10))
        late_rows = service.build(shipment_date + timedelta(days=100))

    early_row = _row_for(early_rows, contragent_id)
    late_row = _row_for(late_rows, contragent_id)
    assert early_row.buckets[0].amount == Decimal("100.00")
    assert late_row.buckets[3].amount == Decimal("100.00")

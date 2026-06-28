"""CurrencyService: USD/UZS konversiya va FIFO'ning valyutalararo to'g'ri ishlashi."""

import uuid
from datetime import date
from decimal import Decimal

import pytest

from app.core.enums import Currency, PaymentType
from app.database.session import session_scope
from app.services.contract_service import ContractService
from app.services.contragent_service import ContragentService
from app.services.currency_service import CurrencyConversionError, CurrencyService
from app.services.dto import ShipmentItemInput
from app.services.exchange_rate_service import ExchangeRateService
from app.services.product_service import ProductService
from app.services.shipment_service import ShipmentService


@pytest.fixture
def contragent_id() -> int:
    return ContragentService().create(name="Currency Test Kontragent").id


@pytest.fixture
def product_id() -> int:
    sku = f"CURRENCY-TEST-{uuid.uuid4().hex[:8]}"
    return ProductService().create(name="Currency Test Mahsulot", sku=sku).id


def test_uzs_to_uzs_is_unchanged() -> None:
    with session_scope() as session:
        result = CurrencyService(session).to_uzs(Decimal("100.00"), Currency.UZS, date(2026, 1, 1))
    assert result == Decimal("100.00")


def test_usd_to_uzs_converts_using_rate() -> None:
    rate_date = date(2026, 4, 1)
    ExchangeRateService().upsert(rate_date, Decimal("12500.0000"))

    with session_scope() as session:
        result = CurrencyService(session).to_uzs(Decimal("10.00"), Currency.USD, rate_date)
    assert result == Decimal("125000.00")


def test_missing_rate_raises_conversion_error() -> None:
    with session_scope() as session:
        with pytest.raises(CurrencyConversionError):
            CurrencyService(session).to_uzs(Decimal("10.00"), Currency.USD, date(1999, 1, 1))


def test_to_usd_converts_using_rate() -> None:
    rate_date = date(2026, 4, 2)
    ExchangeRateService().upsert(rate_date, Decimal("12500.0000"))

    with session_scope() as session:
        result = CurrencyService(session).to_usd(Decimal("125000.00"), Currency.UZS, rate_date)
    assert result == Decimal("10.0000")


def test_exchange_rate_service_upsert_updates_existing_rate() -> None:
    rate_date = date(2026, 4, 3)
    service = ExchangeRateService()
    service.upsert(rate_date, Decimal("12000.0000"))
    updated = service.upsert(rate_date, Decimal("12600.0000"))

    assert updated.usd_to_uzs == Decimal("12600.0000")
    assert len([r for r in service.list_recent(100) if r.rate_date == rate_date]) == 1


def test_fifo_allocates_uzs_payment_against_usd_contract(contragent_id, product_id) -> None:
    rate_date = date(2026, 5, 1)
    ExchangeRateService().upsert(rate_date, Decimal("12000.0000"))

    contract = ContractService().create(
        contract_number=f"CUR-FIFO-{uuid.uuid4().hex[:8]}",
        contragent_id=contragent_id,
        currency=Currency.USD,
        amount=Decimal("1000.00"),
        contract_date=date(2026, 5, 1),
    )

    ShipmentService().create_shipment(
        contract_id=contract.id,
        shipment_number=f"CUR-FIFO-SH-{uuid.uuid4().hex[:8]}",
        shipment_date=date(2026, 5, 1),
        items=[ShipmentItemInput(product_id=product_id, kg=Decimal("100.000"), price=Decimal("10.0000"))],
    )

    # Hozirgi PaymentService har doim shartnoma valyutasini majburlaydi (UZS to'lov sahnasi
    # uchun to'g'ridan-to'g'ri PaymentAllocation orqali emas, balki Payment.currency ustuni
    # mustaqil ekanini ko'rsatish uchun pastda to'g'ridan-to'g'ri model orqali UZS to'lov
    # yaratiladi va reconcile_contract konversiyani to'g'ri qo'llaganini tekshiramiz).
    from app.models.payment import Payment
    from app.repositories.contract_repository import ContractRepository
    from app.repositories.payment_repository import PaymentRepository
    from app.services.fifo_allocation_service import FifoAllocationService

    with session_scope() as session:
        payment_repo = PaymentRepository(session)
        payment_repo.add(
            Payment(
                contract_id=contract.id,
                payment_date=rate_date,
                amount=Decimal("12000000.00"),
                currency=Currency.UZS,
                payment_type=PaymentType.REGULAR,
            )
        )
        contract_obj = ContractRepository(session).get_by_id_or_raise(contract.id)
        FifoAllocationService(session).reconcile_contract(contract_obj)

    summary = ContractService().get_financial_summary(contract.id)
    # 12,000,000 UZS / 12000 = 1000.00 USD — 1000 USD'lik ortishni to'liq yopadi.
    assert summary.debt == Decimal("0")
    assert summary.advance_balance == Decimal("0")

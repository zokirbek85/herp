"""Repository qatlamining asosiy CRUD oqimini real DuckDB faylida tekshiradi."""

from datetime import date
from decimal import Decimal

import pytest

from app.core.enums import ContractStatus, Currency, PaymentType
from app.core.exceptions import NotFoundError
from app.database.session import session_scope
from app.models import (
    Contract,
    ContractSpecification,
    Contragent,
    Payment,
    PaymentAllocation,
    Product,
    Shipment,
    ShipmentItem,
)
from app.repositories import (
    ContractRepository,
    ContractSpecificationRepository,
    ContragentRepository,
    PaymentAllocationRepository,
    PaymentRepository,
    ProductRepository,
    ShipmentItemRepository,
    ShipmentRepository,
)


def test_full_crud_flow_across_repositories() -> None:
    with session_scope() as session:
        contragent_repo = ContragentRepository(session)
        product_repo = ProductRepository(session)
        contract_repo = ContractRepository(session)
        spec_repo = ContractSpecificationRepository(session)
        shipment_repo = ShipmentRepository(session)
        item_repo = ShipmentItemRepository(session)
        payment_repo = PaymentRepository(session)
        allocation_repo = PaymentAllocationRepository(session)

        contragent = contragent_repo.add(
            Contragent(name="Hazorasp Tekstil MCHJ", inn="123456789")
        )
        product = product_repo.add(Product(name="Paxta tolasi", sku="COTTON-01"))

        contract = contract_repo.add(
            Contract(
                contract_number="2026-001",
                contragent_id=contragent.id,
                currency=Currency.USD,
                amount=Decimal("10000.00"),
                contract_date=date(2026, 1, 10),
                status=ContractStatus.NEW,
            )
        )
        spec_repo.add(
            ContractSpecification(
                contract_id=contract.id,
                product_id=product.id,
                planned_kg=Decimal("1000.000"),
                reference_price=Decimal("2.5000"),
                amount=Decimal("2500.00"),
            )
        )

        shipment = shipment_repo.add(
            Shipment(
                shipment_number="SH-2026-001",
                contract_id=contract.id,
                shipment_date=date(2026, 2, 1),
                invoice_number="INV-001",
                ttn_number="TTN-001",
            )
        )
        item_repo.add(
            ShipmentItem(
                shipment_id=shipment.id,
                product_id=product.id,
                lot_number="LOT-1",
                kg=Decimal("500.000"),
                price=Decimal("2.5000"),
                amount=Decimal("1250.00"),
            )
        )

        payment = payment_repo.add(
            Payment(
                contract_id=contract.id,
                payment_date=date(2026, 1, 15),
                amount=Decimal("1250.00"),
                currency=Currency.USD,
                payment_type=PaymentType.ADVANCE,
            )
        )
        allocation_repo.add(
            PaymentAllocation(
                payment_id=payment.id,
                shipment_id=shipment.id,
                allocated_amount=Decimal("1250.00"),
            )
        )

        contragent_id = contragent.id
        contract_id = contract.id
        shipment_id = shipment.id

    # Yangi transaction'da yozuvlar saqlanganini tekshiramiz.
    with session_scope() as session:
        contragent_repo = ContragentRepository(session)
        contract_repo = ContractRepository(session)
        shipment_repo = ShipmentRepository(session)
        allocation_repo = PaymentAllocationRepository(session)

        saved_contragent = contragent_repo.get_by_id_or_raise(contragent_id)
        assert saved_contragent.name == "Hazorasp Tekstil MCHJ"
        assert saved_contragent.inn == "123456789"

        saved_contract = contract_repo.get_by_number("2026-001")
        assert saved_contract is not None
        assert saved_contract.id == contract_id
        assert saved_contract.contragent_id == contragent_id

        shipments = shipment_repo.list_by_contract(contract_id)
        assert len(shipments) == 1
        assert shipments[0].id == shipment_id

        total_allocated = allocation_repo.total_allocated_for_shipment(shipment_id)
        assert total_allocated == Decimal("1250.00")

    # Soft delete: yozuv "yo'qoladi", lekin DB'da jismonan qoladi.
    with session_scope() as session:
        contragent_repo = ContragentRepository(session)
        contragent = contragent_repo.get_by_id_or_raise(contragent_id)
        contragent_repo.soft_delete(contragent)

    with session_scope() as session:
        contragent_repo = ContragentRepository(session)
        assert contragent_repo.get_by_id(contragent_id) is None
        with pytest.raises(NotFoundError):
            contragent_repo.get_by_id_or_raise(contragent_id)

        all_including_deleted = contragent_repo.list(include_deleted=True)
        assert any(c.id == contragent_id for c in all_including_deleted)


def test_payment_repository_returns_fifo_order() -> None:
    with session_scope() as session:
        contragent_repo = ContragentRepository(session)
        contract_repo = ContractRepository(session)
        payment_repo = PaymentRepository(session)

        contragent = contragent_repo.add(Contragent(name="FIFO Test Kontragent"))
        contract = contract_repo.add(
            Contract(
                contract_number="2026-FIFO-1",
                contragent_id=contragent.id,
                currency=Currency.UZS,
                amount=Decimal("5000.00"),
                contract_date=date(2026, 3, 1),
            )
        )
        payment_repo.add(
            Payment(
                contract_id=contract.id,
                payment_date=date(2026, 3, 10),
                amount=Decimal("100.00"),
                currency=Currency.UZS,
                payment_type=PaymentType.REGULAR,
            )
        )
        payment_repo.add(
            Payment(
                contract_id=contract.id,
                payment_date=date(2026, 3, 5),
                amount=Decimal("200.00"),
                currency=Currency.UZS,
                payment_type=PaymentType.ADVANCE,
            )
        )
        contract_id = contract.id

    with session_scope() as session:
        payment_repo = PaymentRepository(session)
        ordered = payment_repo.list_by_contract(contract_id)
        assert [p.amount for p in ordered] == [Decimal("200.00"), Decimal("100.00")]

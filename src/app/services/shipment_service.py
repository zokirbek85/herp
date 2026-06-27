"""Ortishlar bilan bog'liq biznes qoidalari: header+tarkib yaratish, FIFO va status yangilanishi."""

from collections.abc import Sequence
from datetime import date
from decimal import Decimal

from app.core.enums import ContractStatus
from app.core.exceptions import DuplicateError, ValidationError
from app.database.session import session_scope
from app.models.shipment import Shipment
from app.models.shipment_item import ShipmentItem
from app.repositories.contract_repository import ContractRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.shipment_item_repository import ShipmentItemRepository
from app.repositories.shipment_repository import ShipmentRepository
from app.services.contract_status_service import ContractStatusService
from app.services.dto import ShipmentItemInput
from app.services.fifo_allocation_service import FifoAllocationService


class ShipmentService:
    def create_shipment(
        self,
        *,
        contract_id: int,
        shipment_number: str,
        shipment_date: date,
        items: list[ShipmentItemInput],
        invoice_number: str | None = None,
        ttn_number: str | None = None,
        notes: str | None = None,
    ) -> Shipment:
        if not items:
            raise ValidationError("Ortishda kamida bitta mahsulot bo'lishi kerak")

        with session_scope() as session:
            contract_repo = ContractRepository(session)
            product_repo = ProductRepository(session)
            shipment_repo = ShipmentRepository(session)
            item_repo = ShipmentItemRepository(session)

            contract = contract_repo.get_by_id_or_raise(contract_id)
            if contract.status == ContractStatus.CANCELLED:
                raise ValidationError(
                    "Bekor qilingan shartnoma bo'yicha ortish qo'shib bo'lmaydi"
                )
            if shipment_repo.get_by_number(shipment_number) is not None:
                raise DuplicateError("Shipment", "shipment_number", shipment_number)

            shipment = shipment_repo.add(
                Shipment(
                    shipment_number=shipment_number,
                    contract_id=contract_id,
                    shipment_date=shipment_date,
                    invoice_number=invoice_number,
                    ttn_number=ttn_number,
                    notes=notes,
                )
            )

            for item in items:
                if item.kg <= 0 or item.price <= 0:
                    raise ValidationError("Kg va narx musbat bo'lishi kerak")
                product_repo.get_by_id_or_raise(item.product_id)
                amount = (item.kg * item.price).quantize(Decimal("0.01"))
                item_repo.add(
                    ShipmentItem(
                        shipment_id=shipment.id,
                        product_id=item.product_id,
                        lot_number=item.lot_number,
                        kg=item.kg,
                        price=item.price,
                        amount=amount,
                    )
                )

            FifoAllocationService(session).reconcile_contract(contract_id)
            ContractStatusService(session).recalculate(contract)

            return shipment

    def list_by_contract(self, contract_id: int) -> Sequence[Shipment]:
        with session_scope() as session:
            return ShipmentRepository(session).list_by_contract(contract_id)

    def list_all(self) -> Sequence[Shipment]:
        with session_scope() as session:
            return ShipmentRepository(session).list_all()

    def list_items(self, shipment_id: int) -> Sequence[ShipmentItem]:
        with session_scope() as session:
            return ShipmentItemRepository(session).list_by_shipment(shipment_id)

    def get(self, shipment_id: int) -> Shipment:
        with session_scope() as session:
            return ShipmentRepository(session).get_by_id_or_raise(shipment_id)

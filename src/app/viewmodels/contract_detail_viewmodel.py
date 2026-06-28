"""Shartnoma kartochkasi uchun ViewModel: spetsifikatsiya, ortishlar, to'lovlar, moliyaviy xulosa."""

from collections.abc import Sequence
from datetime import date
from decimal import Decimal

from PySide6.QtCore import Signal

from app.core.enums import PaymentType
from app.models.contract import Contract
from app.models.contract_specification import ContractSpecification
from app.models.payment import Payment
from app.models.shipment import Shipment
from app.services.contract_service import ContractService
from app.services.dto import ShipmentItemInput
from app.services.financial_summary_service import ContractFinancialSummary
from app.services.payment_service import PaymentService
from app.services.shipment_service import ShipmentService
from app.viewmodels.base_viewmodel import BaseViewModel


class ContractDetailViewModel(BaseViewModel):
    data_changed = Signal()

    def __init__(
        self,
        contract_id: int,
        contract_service: ContractService | None = None,
        shipment_service: ShipmentService | None = None,
        payment_service: PaymentService | None = None,
    ) -> None:
        super().__init__()
        self.contract_id = contract_id
        self._contract_service = contract_service or ContractService()
        self._shipment_service = shipment_service or ShipmentService()
        self._payment_service = payment_service or PaymentService()

        self.contract: Contract | None = None
        self.summary: ContractFinancialSummary | None = None
        self.specifications: Sequence[ContractSpecification] = []
        self.shipments: Sequence[Shipment] = []
        self.payments: Sequence[Payment] = []
        # Lazy SQLAlchemy relationship `shipment.items` session yopilgandan keyin View
        # qatlamida ishlatilsa DetachedInstanceError beradi — shu sababli shartnoma summasi
        # shu yerda, session ochiq paytida, oddiy dict'ga ko'chiriladi. Mahsulot nomi va
        # kg progress endi `summary.per_product`dan (FinancialSummaryService) olinadi.
        self.shipment_totals: dict[int, Decimal] = {}

    def load(self) -> None:
        def action() -> None:
            self.contract = self._contract_service.get(self.contract_id)
            self.summary = self._contract_service.get_financial_summary(self.contract_id)
            self.specifications = self._contract_service.list_specifications(self.contract_id)
            self.shipments = self._shipment_service.list_by_contract(self.contract_id)
            self.payments = self._payment_service.list_by_contract(self.contract_id)

            self.shipment_totals = {
                shipment.id: sum(
                    (item.amount for item in self._shipment_service.list_items(shipment.id)),
                    start=Decimal("0"),
                )
                for shipment in self.shipments
            }
            self.data_changed.emit()

        self.run_safely(action)

    def add_specification(self, *, product_id: int, planned_kg: Decimal, reference_price: Decimal) -> bool:
        def action() -> None:
            self._contract_service.add_specification(
                self.contract_id,
                product_id=product_id,
                planned_kg=planned_kg,
                reference_price=reference_price,
            )
            self.load()

        return self.run_safely(action)

    def create_shipment(
        self,
        *,
        shipment_number: str,
        shipment_date: date,
        items: list[ShipmentItemInput],
        invoice_number: str | None,
        ttn_number: str | None,
    ) -> bool:
        def action() -> None:
            self._shipment_service.create_shipment(
                contract_id=self.contract_id,
                shipment_number=shipment_number,
                shipment_date=shipment_date,
                items=items,
                invoice_number=invoice_number,
                ttn_number=ttn_number,
            )
            self.load()

        return self.run_safely(action)

    def create_payment(
        self, *, payment_date: date, amount: Decimal, payment_type: PaymentType
    ) -> bool:
        def action() -> None:
            self._payment_service.create_payment(
                contract_id=self.contract_id,
                payment_date=payment_date,
                amount=amount,
                payment_type=payment_type,
            )
            self.load()

        return self.run_safely(action)

    def cancel_contract(self) -> bool:
        def action() -> None:
            self._contract_service.cancel(self.contract_id)
            self.load()

        return self.run_safely(action)

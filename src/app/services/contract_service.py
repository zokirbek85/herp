"""Shartnomalar bilan bog'liq biznes qoidalari: yagona raqam, kontragent mavjudligi,
spetsifikatsiya boshqaruvi va moliyaviy xulosa."""

from collections.abc import Sequence
from datetime import date
from decimal import Decimal

from app.core.enums import ContractStatus, Currency
from app.core.exceptions import DuplicateError, ValidationError
from app.database.session import session_scope
from app.models.contract import Contract
from app.models.contract_specification import ContractSpecification
from app.repositories.contract_repository import ContractRepository
from app.repositories.contract_specification_repository import ContractSpecificationRepository
from app.repositories.contragent_repository import ContragentRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.shipment_repository import ShipmentRepository
from app.services.financial_summary_service import ContractFinancialSummary, FinancialSummaryService


class ContractService:
    def create(
        self,
        *,
        contract_number: str,
        contragent_id: int,
        currency: Currency,
        amount: Decimal,
        contract_date: date,
        notes: str | None = None,
    ) -> Contract:
        if amount <= 0:
            raise ValidationError("Shartnoma summasi musbat bo'lishi kerak")

        with session_scope() as session:
            contragent_repo = ContragentRepository(session)
            contract_repo = ContractRepository(session)

            contragent_repo.get_by_id_or_raise(contragent_id)
            if contract_repo.get_by_number(contract_number) is not None:
                raise DuplicateError("Contract", "contract_number", contract_number)

            return contract_repo.add(
                Contract(
                    contract_number=contract_number,
                    contragent_id=contragent_id,
                    currency=currency,
                    amount=amount,
                    contract_date=contract_date,
                    status=ContractStatus.NEW,
                    notes=notes,
                )
            )

    def update(
        self,
        contract_id: int,
        *,
        contract_number: str,
        contragent_id: int,
        currency: Currency,
        amount: Decimal,
        contract_date: date,
        notes: str | None = None,
    ) -> Contract:
        if amount <= 0:
            raise ValidationError("Shartnoma summasi musbat bo'lishi kerak")

        with session_scope() as session:
            contragent_repo = ContragentRepository(session)
            contract_repo = ContractRepository(session)

            contract = contract_repo.get_by_id_or_raise(contract_id)
            contragent_repo.get_by_id_or_raise(contragent_id)

            if contract_number != contract.contract_number:
                existing = contract_repo.get_by_number(contract_number)
                if existing is not None and existing.id != contract_id:
                    raise DuplicateError("Contract", "contract_number", contract_number)

            contract.contract_number = contract_number
            contract.contragent_id = contragent_id
            contract.currency = currency
            contract.amount = amount
            contract.contract_date = contract_date
            contract.notes = notes
            session.flush()
            return contract

    def soft_delete(self, contract_id: int) -> None:
        with session_scope() as session:
            contract_repo = ContractRepository(session)
            shipment_repo = ShipmentRepository(session)
            payment_repo = PaymentRepository(session)

            contract = contract_repo.get_by_id_or_raise(contract_id)
            if shipment_repo.list_by_contract(contract_id) or payment_repo.list_by_contract(contract_id):
                raise ValidationError(
                    "Ortish yoki to'lovlari mavjud shartnomani o'chirib bo'lmaydi"
                )
            contract_repo.soft_delete(contract)

    def cancel(self, contract_id: int) -> Contract:
        with session_scope() as session:
            repo = ContractRepository(session)
            contract = repo.get_by_id_or_raise(contract_id)
            contract.status = ContractStatus.CANCELLED
            session.flush()
            return contract

    def add_specification(
        self,
        contract_id: int,
        *,
        product_id: int,
        planned_kg: Decimal,
        reference_price: Decimal,
    ) -> ContractSpecification:
        if planned_kg <= 0 or reference_price <= 0:
            raise ValidationError("Kg va narx musbat bo'lishi kerak")

        with session_scope() as session:
            contract_repo = ContractRepository(session)
            product_repo = ProductRepository(session)
            spec_repo = ContractSpecificationRepository(session)

            contract_repo.get_by_id_or_raise(contract_id)
            product_repo.get_by_id_or_raise(product_id)
            if spec_repo.get_by_contract_and_product(contract_id, product_id) is not None:
                raise DuplicateError("ContractSpecification", "product_id", product_id)

            amount = (planned_kg * reference_price).quantize(Decimal("0.01"))
            return spec_repo.add(
                ContractSpecification(
                    contract_id=contract_id,
                    product_id=product_id,
                    planned_kg=planned_kg,
                    reference_price=reference_price,
                    amount=amount,
                )
            )

    def list_specifications(self, contract_id: int) -> Sequence[ContractSpecification]:
        with session_scope() as session:
            return ContractSpecificationRepository(session).list_by_contract(contract_id)

    def get(self, contract_id: int) -> Contract:
        with session_scope() as session:
            return ContractRepository(session).get_by_id_or_raise(contract_id)

    def get_by_number(self, contract_number: str) -> Contract | None:
        with session_scope() as session:
            return ContractRepository(session).get_by_number(contract_number)

    def list_by_contragent(self, contragent_id: int) -> Sequence[Contract]:
        with session_scope() as session:
            return ContractRepository(session).list_by_contragent(contragent_id)

    def list_all(self) -> Sequence[Contract]:
        with session_scope() as session:
            return ContractRepository(session).list_all()

    def count(self) -> int:
        with session_scope() as session:
            return ContractRepository(session).count()

    def list_by_status(self, status: ContractStatus) -> Sequence[Contract]:
        with session_scope() as session:
            return ContractRepository(session).list_by_status(status)

    def get_financial_summary(self, contract_id: int) -> ContractFinancialSummary:
        with session_scope() as session:
            contract = ContractRepository(session).get_by_id_or_raise(contract_id)
            return FinancialSummaryService(session).build(contract)

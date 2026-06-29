"""To'lovlar bilan bog'liq biznes qoidalari: yaratish va FIFO orqali avtomatik taqsimlash."""

from collections.abc import Sequence
from datetime import date
from decimal import Decimal

from app.core.enums import PaymentType
from app.core.exceptions import ValidationError
from app.database.session import session_scope
from app.models.payment import Payment
from app.repositories.contract_repository import ContractRepository
from app.repositories.payment_allocation_repository import PaymentAllocationRepository
from app.repositories.payment_repository import PaymentRepository
from app.services.contract_status_service import ContractStatusService
from app.services.fifo_allocation_service import FifoAllocationService


class PaymentService:
    def create_payment(
        self,
        *,
        contract_id: int,
        payment_date: date,
        amount: Decimal,
        payment_type: PaymentType,
        notes: str | None = None,
    ) -> Payment:
        if amount <= 0:
            raise ValidationError("To'lov summasi musbat bo'lishi kerak")

        with session_scope() as session:
            contract_repo = ContractRepository(session)
            payment_repo = PaymentRepository(session)

            contract = contract_repo.get_by_id_or_raise(contract_id)

            payment = payment_repo.add(
                Payment(
                    contract_id=contract_id,
                    payment_date=payment_date,
                    amount=amount,
                    currency=contract.currency,
                    payment_type=payment_type,
                    notes=notes,
                )
            )

            FifoAllocationService(session).reconcile_contract(contract)
            ContractStatusService(session).recalculate(contract)

            return payment

    def update_payment(
        self,
        payment_id: int,
        *,
        payment_date: date,
        amount: Decimal,
        payment_type: PaymentType,
        notes: str | None = None,
    ) -> Payment:
        if amount <= 0:
            raise ValidationError("To'lov summasi musbat bo'lishi kerak")

        with session_scope() as session:
            contract_repo = ContractRepository(session)
            payment_repo = PaymentRepository(session)
            allocation_repo = PaymentAllocationRepository(session)

            payment = payment_repo.get_by_id_or_raise(payment_id)
            contract = contract_repo.get_by_id_or_raise(payment.contract_id)

            allocation_repo.soft_delete_by_payment(payment_id)

            payment.payment_date = payment_date
            payment.amount = amount
            payment.payment_type = payment_type
            payment.notes = notes

            FifoAllocationService(session).reconcile_contract(contract)
            ContractStatusService(session).recalculate(contract)

            return payment

    def soft_delete(self, payment_id: int) -> None:
        with session_scope() as session:
            contract_repo = ContractRepository(session)
            payment_repo = PaymentRepository(session)
            allocation_repo = PaymentAllocationRepository(session)

            payment = payment_repo.get_by_id_or_raise(payment_id)
            contract = contract_repo.get_by_id_or_raise(payment.contract_id)

            allocation_repo.soft_delete_by_payment(payment_id)
            payment_repo.soft_delete(payment)

            FifoAllocationService(session).reconcile_contract(contract)
            ContractStatusService(session).recalculate(contract)

    def get(self, payment_id: int) -> Payment:
        with session_scope() as session:
            return PaymentRepository(session).get_by_id_or_raise(payment_id)

    def list_by_contract(self, contract_id: int) -> Sequence[Payment]:
        with session_scope() as session:
            return PaymentRepository(session).list_by_contract(contract_id)

    def list_all(self) -> Sequence[Payment]:
        with session_scope() as session:
            return PaymentRepository(session).list_all()

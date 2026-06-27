"""model_to_dict / dict_to_model_kwargs round-trip: Decimal, UUID, datetime, date, Enum."""

from datetime import date
from decimal import Decimal

from app.core.enums import ContractStatus, Currency
from app.database.session import session_scope
from app.models import Contract, Contragent
from app.repositories import ContractRepository, ContragentRepository
from app.sync.serializer import dict_to_model_kwargs, model_to_dict


def test_model_to_dict_serializes_special_types_to_json_safe_values() -> None:
    with session_scope() as session:
        contragent = ContragentRepository(session).add(Contragent(name="Serializer Test Kontragent"))
        contract = ContractRepository(session).add(
            Contract(
                contract_number="SER-001",
                contragent_id=contragent.id,
                currency=Currency.USD,
                amount=Decimal("1234.56"),
                contract_date=date(2026, 1, 10),
                status=ContractStatus.NEW,
            )
        )
        contract_id = contract.id

    with session_scope() as session:
        saved = ContractRepository(session).get_by_id_or_raise(contract_id)
        data = model_to_dict(saved)

        assert data["amount"] == "1234.56"
        assert data["currency"] == "USD"
        assert data["status"] == "NEW"
        assert data["contract_date"] == "2026-01-10"
        assert isinstance(data["uuid"], str)
        assert isinstance(data["created_at"], str)


def test_dict_to_model_kwargs_restores_native_python_types() -> None:
    with session_scope() as session:
        contragent = ContragentRepository(session).add(Contragent(name="Round Trip Kontragent"))
        contract = ContractRepository(session).add(
            Contract(
                contract_number="SER-002",
                contragent_id=contragent.id,
                currency=Currency.UZS,
                amount=Decimal("999.99"),
                contract_date=date(2026, 2, 1),
                status=ContractStatus.IN_PROGRESS,
            )
        )
        contract_id = contract.id

    with session_scope() as session:
        saved = ContractRepository(session).get_by_id_or_raise(contract_id)
        data = model_to_dict(saved)

    kwargs = dict_to_model_kwargs(Contract, data)

    assert kwargs["amount"] == Decimal("999.99")
    assert kwargs["currency"] is Currency.UZS
    assert kwargs["status"] is ContractStatus.IN_PROGRESS
    assert kwargs["contract_date"] == date(2026, 2, 1)

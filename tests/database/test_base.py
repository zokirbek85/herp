"""AuditMixin: insert paytida created_at == updated_at, keyingi tahrirda updated_at o'sadi."""

import time

from app.database.session import session_scope
from app.models import Contragent
from app.repositories import ContragentRepository


def test_created_at_equals_updated_at_on_insert() -> None:
    with session_scope() as session:
        contragent = ContragentRepository(session).add(Contragent(name="Audit Insert Test"))
        assert contragent.created_at == contragent.updated_at
        contragent_id = contragent.id

    with session_scope() as session:
        found = ContragentRepository(session).get_by_id_or_raise(contragent_id)
        assert found.created_at == found.updated_at


def test_updated_at_advances_on_modification_but_created_at_stays_fixed() -> None:
    with session_scope() as session:
        contragent = ContragentRepository(session).add(Contragent(name="Audit Update Test"))
        contragent_id = contragent.id
        original_created_at = contragent.created_at

    time.sleep(0.01)

    with session_scope() as session:
        repo = ContragentRepository(session)
        contragent = repo.get_by_id_or_raise(contragent_id)
        contragent.phone = "+998901112233"

    with session_scope() as session:
        found = ContragentRepository(session).get_by_id_or_raise(contragent_id)
        assert found.created_at == original_created_at
        assert found.updated_at > found.created_at

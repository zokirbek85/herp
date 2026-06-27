"""session_scope(): xatolik bo'lganda avtomatik rollback."""

import pytest

from app.database.session import session_scope
from app.models import Contragent
from app.repositories import ContragentRepository


def test_session_scope_rolls_back_on_exception() -> None:
    with pytest.raises(RuntimeError):
        with session_scope() as session:
            ContragentRepository(session).add(Contragent(name="Rollback Test Kontragent"))
            raise RuntimeError("kutilmagan xatolik")

    with session_scope() as session:
        found = ContragentRepository(session).search_by_name("Rollback Test Kontragent")
        assert found == []


def test_session_scope_commits_on_success() -> None:
    with session_scope() as session:
        contragent = ContragentRepository(session).add(Contragent(name="Commit Test Kontragent"))
        contragent_id = contragent.id

    with session_scope() as session:
        found = ContragentRepository(session).get_by_id(contragent_id)
        assert found is not None
        assert found.name == "Commit Test Kontragent"

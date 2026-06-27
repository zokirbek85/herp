"""Kontragentlar ro'yxati sahifasi uchun ViewModel: qidiruv, yaratish, tahrirlash, o'chirish."""

from collections.abc import Sequence

from PySide6.QtCore import Signal

from app.models.contragent import Contragent
from app.services.contragent_service import ContragentService
from app.viewmodels.base_viewmodel import BaseViewModel


class ContragentListViewModel(BaseViewModel):
    contragents_changed = Signal(list)

    def __init__(self, service: ContragentService | None = None) -> None:
        super().__init__()
        self._service = service or ContragentService()
        self._contragents: Sequence[Contragent] = []

    @property
    def contragents(self) -> Sequence[Contragent]:
        return self._contragents

    def load(self, query: str = "") -> None:
        def action() -> None:
            self._contragents = (
                self._service.search(query) if query.strip() else self._service.list(limit=200)
            )
            self.contragents_changed.emit(list(self._contragents))

        self.run_safely(action)

    def create(self, *, name: str, inn: str | None, phone: str | None, address: str | None) -> bool:
        def action() -> None:
            self._service.create(name=name, inn=inn, phone=phone, address=address)
            self.load()

        return self.run_safely(action)

    def update(
        self,
        contragent_id: int,
        *,
        name: str,
        inn: str | None,
        phone: str | None,
        address: str | None,
        contact_person: str | None,
        notes: str | None,
        is_active: bool,
    ) -> bool:
        def action() -> None:
            self._service.update(
                contragent_id,
                name=name,
                inn=inn,
                phone=phone,
                address=address,
                contact_person=contact_person,
                notes=notes,
                is_active=is_active,
            )
            self.load()

        return self.run_safely(action)

    def delete(self, contragent_id: int) -> bool:
        def action() -> None:
            self._service.soft_delete(contragent_id)
            self.load()

        return self.run_safely(action)

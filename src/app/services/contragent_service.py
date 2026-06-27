"""Kontragentlar bilan bog'liq biznes qoidalari: INN noyobligi va faol shartnomali
kontragentni o'chirishni taqiqlash."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from app.core.exceptions import AppError, DuplicateError, ValidationError
from app.database.session import session_scope
from app.models.contragent import Contragent
from app.repositories.contract_repository import ContractRepository
from app.repositories.contragent_repository import ContragentRepository
from app.services.dto import ContragentImportResult, ImportRowError


class ContragentService:
    def create(
        self,
        *,
        name: str,
        inn: str | None = None,
        phone: str | None = None,
        address: str | None = None,
        contact_person: str | None = None,
        notes: str | None = None,
    ) -> Contragent:
        with session_scope() as session:
            repo = ContragentRepository(session)
            if inn and repo.get_by_inn(inn) is not None:
                raise DuplicateError("Contragent", "inn", inn)
            return repo.add(
                Contragent(
                    name=name,
                    inn=inn,
                    phone=phone,
                    address=address,
                    contact_person=contact_person,
                    notes=notes,
                )
            )

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
    ) -> Contragent:
        with session_scope() as session:
            repo = ContragentRepository(session)
            contragent = repo.get_by_id_or_raise(contragent_id)

            if inn and inn != contragent.inn:
                existing = repo.get_by_inn(inn)
                if existing is not None and existing.id != contragent_id:
                    raise DuplicateError("Contragent", "inn", inn)

            contragent.name = name
            contragent.inn = inn
            contragent.phone = phone
            contragent.address = address
            contragent.contact_person = contact_person
            contragent.notes = notes
            contragent.is_active = is_active
            session.flush()
            return contragent

    def soft_delete(self, contragent_id: int) -> None:
        with session_scope() as session:
            contragent_repo = ContragentRepository(session)
            contract_repo = ContractRepository(session)

            contragent = contragent_repo.get_by_id_or_raise(contragent_id)
            if contract_repo.list_by_contragent(contragent_id):
                raise ValidationError(
                    "Faol shartnomalari mavjud kontragentni o'chirib bo'lmaydi"
                )
            contragent_repo.soft_delete(contragent)

    def get(self, contragent_id: int) -> Contragent:
        with session_scope() as session:
            return ContragentRepository(session).get_by_id_or_raise(contragent_id)

    def list(self, *, limit: int = 50, offset: int = 0) -> Sequence[Contragent]:
        with session_scope() as session:
            return ContragentRepository(session).list(limit=limit, offset=offset)

    def search(self, query: str, *, limit: int = 20) -> Sequence[Contragent]:
        with session_scope() as session:
            return ContragentRepository(session).search_by_name(query, limit=limit)

    def bulk_import(self, rows: list[dict[str, Any]]) -> ContragentImportResult:
        """Excel'dan o'qilgan qatorlarni ("Nomi", "INN", "Telefon", "Manzil" ustunlari)
        kontragentlarga aylantiradi. Har bir qator alohida tranzaksiyada qayta ishlanadi —
        bitta qatordagi xatolik (masalan, takror INN) qolganlarining import qilinishiga
        to'sqinlik qilmaydi."""
        created: list[Contragent] = []
        errors: list[ImportRowError] = []

        for excel_row_number, row in enumerate(rows, start=2):
            name = str(row.get("Nomi") or row.get("name") or "").strip()
            if not name:
                errors.append(ImportRowError(excel_row_number, "Nomi bo'sh"))
                continue

            raw_inn = row.get("INN") or row.get("inn")
            inn = str(raw_inn).strip() if raw_inn else None
            raw_phone = row.get("Telefon") or row.get("phone")
            phone = str(raw_phone).strip() if raw_phone else None
            raw_address = row.get("Manzil") or row.get("address")
            address = str(raw_address).strip() if raw_address else None

            try:
                created.append(self.create(name=name, inn=inn, phone=phone, address=address))
            except AppError as exc:
                errors.append(ImportRowError(excel_row_number, str(exc)))

        return ContragentImportResult(created=created, errors=errors)

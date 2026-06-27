"""Barcha repository'lar uchun umumiy CRUD operatsiyalari.

Repository faqat ma'lumotlarga murojaat (query/persist) bilan shug'ullanadi — biznes
qoidalari yoki transaction boshqaruvi bu yerda emas, Service qatlamida bo'ladi.
SQL/ORM kodi loyiha bo'ylab faqat shu qatlamda yoziladi.
"""

import uuid as uuid_pkg
from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    model: type[ModelType]

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, id_: int) -> ModelType | None:
        stmt = select(self.model).where(self.model.id == id_, self.model.deleted_at.is_(None))
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_id_or_raise(self, id_: int) -> ModelType:
        obj = self.get_by_id(id_)
        if obj is None:
            raise NotFoundError(self.model.__name__, id_)
        return obj

    def get_by_uuid(self, value: uuid_pkg.UUID) -> ModelType | None:
        stmt = select(self.model).where(self.model.uuid == value, self.model.deleted_at.is_(None))
        return self.session.execute(stmt).scalar_one_or_none()

    def list(
        self, *, limit: int = 50, offset: int = 0, include_deleted: bool = False
    ) -> Sequence[ModelType]:
        stmt = select(self.model)
        if not include_deleted:
            stmt = stmt.where(self.model.deleted_at.is_(None))
        stmt = stmt.order_by(self.model.id).limit(limit).offset(offset)
        return self.session.execute(stmt).scalars().all()

    def list_all(self, *, include_deleted: bool = False) -> Sequence[ModelType]:
        """Sahifalashsiz to'liq ro'yxat — faqat hisobot/analitika agregatsiyasi uchun
        ishlatiladi (UI ro'yxatlari uchun har doim `list()` bilan pagination qilinsin)."""
        stmt = select(self.model)
        if not include_deleted:
            stmt = stmt.where(self.model.deleted_at.is_(None))
        stmt = stmt.order_by(self.model.id)
        return self.session.execute(stmt).scalars().all()

    def count(self, *, include_deleted: bool = False) -> int:
        stmt = select(func.count()).select_from(self.model)
        if not include_deleted:
            stmt = stmt.where(self.model.deleted_at.is_(None))
        return self.session.execute(stmt).scalar_one()

    def add(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        self.session.flush()
        return obj

    def soft_delete(self, obj: ModelType) -> None:
        obj.deleted_at = datetime.now(timezone.utc)
        self.session.flush()

    def restore(self, obj: ModelType) -> None:
        obj.deleted_at = None
        self.session.flush()

"""Declarative Base va barcha modellar uchun umumiy Audit Mixin."""

import uuid as uuid_pkg
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, Sequence, Uuid, event
from sqlalchemy.orm import DeclarativeBase, Mapped, Mapper, declared_attr, mapped_column


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Barcha ORM modellari shu klassdan meros oladi."""


class AuditMixin:
    """Har bir biznes jadvalida bo'lishi shart bo'lgan audit va sync ustunlari.

    `uuid` sinxronlash paytida yozuvni qurilmalar orasida bir xil identifikatsiya qilish uchun,
    `updated_at` esa sync conflict'larni aniqlash uchun ishlatiladi: import qatlami
    `updated_at == created_at` tengligini "yozuv hech qachon lokal tahrirlanmagan" belgisi
    sifatida ishlatadi (`app/sync/importer.py`ga qarang). Shu sababli ikkisi insert paytida
    bir xil qiymatga ega bo'lishi shart — pastdagi `before_insert` event shuni ta'minlaydi
    (ustun darajasidagi mustaqil `default=_utcnow` chaqiruvlari ikki xil mikrosoniyada
    bajarilib, tengsizlikka olib kelardi).
    """

    @declared_attr
    def id(cls) -> Mapped[int]:  # noqa: N805
        """DuckDB'da SERIAL/IDENTITY qo'llab-quvvatlanmaydi — har bir jadval uchun nomli
        Sequence orqali PK yaratiladi (`autoincrement=False` postgres dialektining
        avtomatik SERIAL'ga aylantirishini oldini oladi; Sequence Postgres'ga ko'chirishda ham ishlaydi)."""
        return mapped_column(
            Integer, Sequence(f"{cls.__tablename__}_id_seq"), primary_key=True, autoincrement=False
        )
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(
        Uuid, unique=True, index=True, default=uuid_pkg.uuid4, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=_utcnow, nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None, index=True)

    # `users.id`ga DB darajasida FK qo'yilmagan: DuckDB FK bilan bog'langan qatorni UPDATE
    # qilishni butunlay bloklaydi (soft-delete/audit yangilanishi ishlamay qoladi). Yaxlitlik
    # Service qatlamida tekshiriladi — `core/exceptions.py` va `services/`ga qarang.
    created_by: Mapped[int | None] = mapped_column(Integer, index=True, default=None)
    updated_by: Mapped[int | None] = mapped_column(Integer, index=True, default=None)


@event.listens_for(Mapper, "before_insert")
def _set_initial_audit_timestamps(mapper: Mapper, connection: object, target: object) -> None:
    """`created_at`/`updated_at`ni insert vaqtida bitta umumiy timestamp'ga tenglashtiradi."""
    if not isinstance(target, AuditMixin):
        return
    now = _utcnow()
    if target.created_at is None:
        target.created_at = now
    if target.updated_at is None:
        target.updated_at = now

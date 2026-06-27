"""`.sync` paketni import qilib, UUID asosida lokal bazaga merge qiladi ("Import/Merge Changes").

Conflict aniqlash qoidasi: agar lokal yozuv yaratilgandan beri hech qachon tahrirlanmagan bo'lsa
(`updated_at == created_at`), kelgan o'zgarish xavfsiz qabul qilinadi — chunki bu qurilmada
hech kim uni o'zgartirmagan. Aks holda, agar ikkala tomonda ham mazmun farq qilsa, bu ikki
qurilmada mustaqil tahrirlash bo'lgani uchun CONFLICT sifatida belgilanadi va foydalanuvchiga
(`resolve_conflict` orqali) tanlash imkoniyati beriladi — avtomatik ustidan yozilmaydi.
"""

import json
import uuid as uuid_pkg
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import SyncDirection, SyncStatus
from app.database.base import Base
from app.database.session import session_scope
from app.models import (
    Contract,
    ContractSpecification,
    Contragent,
    ExchangeRate,
    Payment,
    PaymentAllocation,
    Product,
    Shipment,
    ShipmentItem,
    SyncLog,
    User,
)
from app.sync.exporter import MANIFEST_FILE_NAME, SYNCED_MODELS
from app.sync.serializer import dict_to_model_kwargs, model_to_dict

_MODELS_BY_TABLE: dict[str, type[Base]] = {model.__tablename__: model for model in SYNCED_MODELS}

_IGNORED_COMPARISON_COLUMNS = {"id", "created_at", "updated_at", "created_by", "updated_by"}


@dataclass(frozen=True, slots=True)
class SyncConflict:
    table_name: str
    record_uuid: str
    local_data: dict[str, Any]
    incoming_data: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ImportResult:
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    conflicts: list[SyncConflict] = field(default_factory=list)


def import_changes(package_path: Path, *, device_id: str) -> ImportResult:
    with zipfile.ZipFile(package_path) as archive:
        if MANIFEST_FILE_NAME not in archive.namelist():
            raise ValueError("Sync paketida manifest.json topilmadi")

        inserted = updated = skipped = 0
        conflicts: list[SyncConflict] = []

        with session_scope() as session:
            for table_name, model in _MODELS_BY_TABLE.items():
                entry_name = f"{table_name}.json"
                if entry_name not in archive.namelist():
                    continue

                rows = json.loads(archive.read(entry_name))
                for row in rows:
                    outcome, conflict = _merge_row(session, model, row)
                    if outcome == "inserted":
                        inserted += 1
                    elif outcome == "updated":
                        updated += 1
                    else:
                        skipped += 1
                    if conflict is not None:
                        conflicts.append(conflict)

            session.add(
                SyncLog(
                    device_id=device_id,
                    direction=SyncDirection.IMPORT,
                    package_path=str(package_path),
                    status=SyncStatus.CONFLICT if conflicts else SyncStatus.SUCCESS,
                    executed_at=datetime.now(timezone.utc),
                    conflicts_count=len(conflicts),
                )
            )

        return ImportResult(inserted=inserted, updated=updated, skipped=skipped, conflicts=conflicts)


def resolve_conflict(conflict: SyncConflict, *, keep: str) -> None:
    """Foydalanuvchi tanlovini qo'llaydi: `keep="local"` — hech narsa qilinmaydi,
    `keep="incoming"` — kelgan ma'lumot lokal yozuvga qo'llaniladi."""
    if keep == "local":
        return
    if keep != "incoming":
        raise ValueError("keep faqat 'local' yoki 'incoming' bo'lishi mumkin")

    model = _MODELS_BY_TABLE[conflict.table_name]
    with session_scope() as session:
        local_obj = session.execute(
            select(model).where(model.uuid == uuid_pkg.UUID(conflict.record_uuid))
        ).scalar_one_or_none()
        if local_obj is not None:
            _apply_incoming(local_obj, model, conflict.incoming_data)


def _merge_row(session: Session, model: type[Base], row: dict[str, Any]) -> tuple[str, SyncConflict | None]:
    incoming_uuid = uuid_pkg.UUID(row["uuid"])
    local_obj = session.execute(select(model).where(model.uuid == incoming_uuid)).scalar_one_or_none()

    if local_obj is None:
        session.add(model(**dict_to_model_kwargs(model, row)))
        session.flush()
        return "inserted", None

    incoming_updated_at = datetime.fromisoformat(row["updated_at"])
    if incoming_updated_at == local_obj.updated_at:
        return "skipped", None

    if not _content_differs(local_obj, row):
        return "skipped", None

    local_was_edited_locally = local_obj.updated_at > local_obj.created_at
    if not local_was_edited_locally:
        _apply_incoming(local_obj, model, row)
        return "updated", None

    conflict = SyncConflict(
        table_name=model.__tablename__,
        record_uuid=str(incoming_uuid),
        local_data=model_to_dict(local_obj),
        incoming_data=row,
    )
    return "skipped", conflict


def _content_differs(local_obj: Base, row: dict[str, Any]) -> bool:
    local_dict = model_to_dict(local_obj)
    return any(
        local_dict.get(key) != row.get(key)
        for key in row
        if key not in _IGNORED_COMPARISON_COLUMNS
    )


def _apply_incoming(local_obj: Base, model: type[Base], row: dict[str, Any]) -> None:
    for key, value in dict_to_model_kwargs(model, row).items():
        if key == "id":
            continue
        setattr(local_obj, key, value)

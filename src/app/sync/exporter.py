"""Lokal o'zgarishlarni `.sync` (zip) paketga eksport qilish ("Export Changes")."""

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select

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
    User,
)
from app.sync.serializer import model_to_dict

MANIFEST_FILE_NAME = "manifest.json"

SYNCED_MODELS: list[type[Base]] = [
    User,
    Contragent,
    Product,
    Contract,
    ContractSpecification,
    Shipment,
    ShipmentItem,
    Payment,
    PaymentAllocation,
    ExchangeRate,
]


def export_changes(
    output_path: Path,
    *,
    device_id: str,
    since: datetime | None = None,
) -> Path:
    """`.sync` paket yaratadi. `since` berilmasa — barcha yozuvlar (to'liq nusxa) eksport
    qilinadi; bu birinchi sinxronlash yoki yangi qurilma qo'shilganda ishlatiladi.

    Diqqat: soft-delete qilingan yozuvlar ham eksport qilinadi — o'chirish ham "o'zgarish"
    hisoblanadi va boshqa qurilmalarga tarqalishi shart.
    """
    manifest: dict = {
        "device_id": device_id,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "since": since.isoformat() if since else None,
        "tables": {},
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as archive:
        with session_scope() as session:
            for model in SYNCED_MODELS:
                stmt = select(model)
                if since is not None:
                    stmt = stmt.where(model.updated_at > since)
                rows = session.execute(stmt).scalars().all()

                serialized = [model_to_dict(row) for row in rows]
                manifest["tables"][model.__tablename__] = len(serialized)
                archive.writestr(
                    f"{model.__tablename__}.json", json.dumps(serialized, ensure_ascii=False)
                )

        archive.writestr(MANIFEST_FILE_NAME, json.dumps(manifest, ensure_ascii=False, indent=2))

    return output_path

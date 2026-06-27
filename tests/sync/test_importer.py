"""import_changes(): insert/update/skip/conflict qoidalari va resolve_conflict()."""

import json
import uuid
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.database.session import session_scope
from app.models import Contragent
from app.repositories import ContragentRepository
from app.sync.exporter import MANIFEST_FILE_NAME
from app.sync.importer import import_changes, resolve_conflict
from app.sync.serializer import model_to_dict


def _build_package(path: Path, *, contragent_rows: list[dict]) -> Path:
    manifest = {
        "device_id": "device-b",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "since": None,
        "tables": {"contragents": len(contragent_rows)},
    }
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("contragents.json", json.dumps(contragent_rows, ensure_ascii=False))
        archive.writestr(MANIFEST_FILE_NAME, json.dumps(manifest, ensure_ascii=False))
    return path


def test_import_inserts_unknown_record(tmp_path) -> None:
    new_row = {
        "id": 999_999,
        "uuid": str(uuid.uuid4()),
        "name": "Yangi Kelgan Kontragent",
        "inn": None,
        "phone": None,
        "address": None,
        "contact_person": None,
        "notes": None,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "deleted_at": None,
        "created_by": None,
        "updated_by": None,
    }
    package = _build_package(tmp_path / "insert.sync", contragent_rows=[new_row])

    result = import_changes(package, device_id="device-a")

    assert result.inserted == 1
    assert result.updated == 0
    assert result.conflicts == []

    with session_scope() as session:
        found = ContragentRepository(session).get_by_uuid(uuid.UUID(new_row["uuid"]))
        assert found is not None
        assert found.name == "Yangi Kelgan Kontragent"


def test_import_updates_record_never_edited_locally(tmp_path) -> None:
    with session_scope() as session:
        local = ContragentRepository(session).add(Contragent(name="Tahrirlanmagan Kontragent"))
        local_uuid = local.uuid

    incoming_row = {
        "id": 999_998,
        "uuid": str(local_uuid),
        "name": "Boshqa Qurilmadan Yangilangan",
        "inn": None,
        "phone": None,
        "address": None,
        "contact_person": None,
        "notes": None,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
        "deleted_at": None,
        "created_by": None,
        "updated_by": None,
    }
    package = _build_package(tmp_path / "update.sync", contragent_rows=[incoming_row])

    result = import_changes(package, device_id="device-a")

    assert result.updated == 1
    assert result.conflicts == []

    with session_scope() as session:
        found = ContragentRepository(session).get_by_uuid(local_uuid)
        assert found.name == "Boshqa Qurilmadan Yangilangan"


def test_import_skips_when_content_unchanged(tmp_path) -> None:
    with session_scope() as session:
        local = ContragentRepository(session).add(Contragent(name="O'zgarmagan Kontragent"))
        local_dict = model_to_dict(local)

    incoming_row = dict(local_dict)
    incoming_row["updated_at"] = (
        datetime.fromisoformat(local_dict["updated_at"]) + timedelta(minutes=1)
    ).isoformat()
    package = _build_package(tmp_path / "noop.sync", contragent_rows=[incoming_row])

    result = import_changes(package, device_id="device-a")

    assert result.skipped == 1
    assert result.updated == 0
    assert result.conflicts == []


def _create_conflict(tmp_path):
    with session_scope() as session:
        local = ContragentRepository(session).add(Contragent(name="Conflict Kontragent"))
        local_uuid = local.uuid
        local_id = local.id

    # Lokal qurilmada ham tahrir bo'ladi — `updated_at` `created_at`dan kattalashadi.
    with session_scope() as session:
        repo = ContragentRepository(session)
        local = repo.get_by_id_or_raise(local_id)
        local.phone = "+998900000000"

    incoming_row = {
        "id": 999_997,
        "uuid": str(local_uuid),
        "name": "Boshqa Qurilmadagi Nom",
        "inn": None,
        "phone": None,
        "address": None,
        "contact_person": None,
        "notes": None,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(),
        "deleted_at": None,
        "created_by": None,
        "updated_by": None,
    }
    package = _build_package(tmp_path / "conflict.sync", contragent_rows=[incoming_row])

    result = import_changes(package, device_id="device-a")

    assert result.updated == 0
    assert len(result.conflicts) == 1
    conflict = result.conflicts[0]
    assert conflict.table_name == "contragents"
    assert conflict.record_uuid == str(local_uuid)
    assert conflict.local_data["name"] == "Conflict Kontragent"
    assert conflict.incoming_data["name"] == "Boshqa Qurilmadagi Nom"

    with session_scope() as session:
        # Conflict hal qilinmaguncha lokal qiymat o'zgarmasdan qoladi.
        found = ContragentRepository(session).get_by_uuid(local_uuid)
        assert found.name == "Conflict Kontragent"

    return conflict


def test_import_reports_conflict_when_both_sides_edited(tmp_path) -> None:
    _create_conflict(tmp_path)


def test_resolve_conflict_keep_local_does_nothing(tmp_path) -> None:
    conflict = _create_conflict(tmp_path)

    resolve_conflict(conflict, keep="local")

    with session_scope() as session:
        found = ContragentRepository(session).get_by_uuid(uuid.UUID(conflict.record_uuid))
        assert found.name == "Conflict Kontragent"


def test_resolve_conflict_keep_incoming_applies_remote_data(tmp_path) -> None:
    conflict = _create_conflict(tmp_path)

    resolve_conflict(conflict, keep="incoming")

    with session_scope() as session:
        found = ContragentRepository(session).get_by_uuid(uuid.UUID(conflict.record_uuid))
        assert found.name == "Boshqa Qurilmadagi Nom"

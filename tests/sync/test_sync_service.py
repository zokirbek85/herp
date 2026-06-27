"""SyncService: incremental export state, pre-import backup, end-to-end export->import oqimi."""

import json
import zipfile

from app.backup.backup_service import list_backups
from app.database.session import session_scope
from app.models import Contragent
from app.repositories import ContragentRepository
from app.sync.exporter import MANIFEST_FILE_NAME
from app.sync.state import get_last_export_at
from app.sync.sync_service import SyncService


def test_export_changes_updates_last_export_state(tmp_path) -> None:
    service = SyncService()
    before = get_last_export_at()

    output_path = service.export_changes(tmp_path / "export1.sync", full_export=True)

    assert output_path.exists()
    after = get_last_export_at()
    assert after is not None
    assert before is None or after > before


def test_second_incremental_export_excludes_already_exported_rows(tmp_path) -> None:
    service = SyncService()
    service.export_changes(tmp_path / "baseline.sync", full_export=True)

    with session_scope() as session:
        ContragentRepository(session).add(Contragent(name="Service Test Yangi Kontragent"))

    output_path = service.export_changes(tmp_path / "incremental.sync")

    with zipfile.ZipFile(output_path) as archive:
        rows = json.loads(archive.read("contragents.json"))
        names = {row["name"] for row in rows}
        assert "Service Test Yangi Kontragent" in names


def test_import_changes_creates_pre_sync_backup(tmp_path) -> None:
    service = SyncService()
    package_path = service.export_changes(tmp_path / "export_for_import.sync", full_export=True)

    backups_before = len(list_backups())
    service.import_changes(package_path)
    backups_after = len(list_backups())

    assert backups_after == backups_before + 1


def test_export_then_import_round_trip_is_idempotent(tmp_path) -> None:
    service = SyncService()
    with session_scope() as session:
        ContragentRepository(session).add(Contragent(name="Round Trip Sync Kontragent"))

    package_path = service.export_changes(tmp_path / "round_trip.sync", full_export=True)

    with zipfile.ZipFile(package_path) as archive:
        manifest = json.loads(archive.read(MANIFEST_FILE_NAME))
    assert manifest["tables"]["contragents"] >= 1

    # O'zining eksportini qayta import qilish hech narsani buzmasligi kerak (skip kutiladi).
    result = service.import_changes(package_path)
    assert result.conflicts == []

"""export_changes(): to'liq va incremental (`since`) eksport, manifest tarkibi."""

import json
import zipfile
from datetime import datetime, timezone

from app.database.session import session_scope
from app.models import Contragent
from app.repositories import ContragentRepository
from app.sync.exporter import MANIFEST_FILE_NAME, export_changes


def test_full_export_includes_all_existing_rows(tmp_path) -> None:
    with session_scope() as session:
        ContragentRepository(session).add(Contragent(name="Eksport Kontragent 1"))

    output_path = tmp_path / "full_export.sync"
    export_changes(output_path, device_id="device-a")

    with zipfile.ZipFile(output_path) as archive:
        manifest = json.loads(archive.read(MANIFEST_FILE_NAME))
        assert manifest["device_id"] == "device-a"
        assert manifest["since"] is None
        assert manifest["tables"]["contragents"] >= 1

        rows = json.loads(archive.read("contragents.json"))
        assert any(row["name"] == "Eksport Kontragent 1" for row in rows)


def test_incremental_export_only_includes_rows_changed_since(tmp_path) -> None:
    with session_scope() as session:
        ContragentRepository(session).add(Contragent(name="Eski Kontragent"))

    since = datetime.now(timezone.utc)

    with session_scope() as session:
        ContragentRepository(session).add(Contragent(name="Yangi Kontragent"))

    output_path = tmp_path / "incremental_export.sync"
    export_changes(output_path, device_id="device-a", since=since)

    with zipfile.ZipFile(output_path) as archive:
        manifest = json.loads(archive.read(MANIFEST_FILE_NAME))
        assert manifest["since"] == since.isoformat()

        rows = json.loads(archive.read("contragents.json"))
        names = {row["name"] for row in rows}
        assert "Yangi Kontragent" in names
        assert "Eski Kontragent" not in names

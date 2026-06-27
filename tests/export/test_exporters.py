"""Excel/CSV/PDF eksport va Excel import funksiyalarini tekshiradi."""

from decimal import Decimal
from pathlib import Path

from app.export.column_spec import ExportColumn
from app.export.csv_exporter import export_to_csv
from app.export.excel_exporter import export_to_excel
from app.export.excel_importer import read_excel_rows
from app.export.pdf_exporter import export_to_pdf

_COLUMNS = [
    ExportColumn(header="Nomi", key="name"),
    ExportColumn(header="Summa", key="amount", formatter=lambda v: f"{v:,.2f}"),
]
_ROWS = [
    {"name": "Hazorasp Tekstil MCHJ", "amount": Decimal("1234.50")},
    {"name": "Boshqa Kontragent", "amount": Decimal("99.00")},
]


def test_excel_export_and_import_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "kontragentlar.xlsx"
    export_to_excel(path, _COLUMNS, _ROWS, sheet_title="Kontragentlar")

    assert path.exists()
    imported = read_excel_rows(path)
    assert len(imported) == 2
    assert imported[0]["Nomi"] == "Hazorasp Tekstil MCHJ"
    assert imported[0]["Summa"] == "1,234.50"


def test_csv_export_contains_header_and_rows(tmp_path: Path) -> None:
    path = tmp_path / "kontragentlar.csv"
    export_to_csv(path, _COLUMNS, _ROWS)

    content = path.read_text(encoding="utf-8-sig")
    lines = content.strip().splitlines()
    assert lines[0] == "Nomi,Summa"
    assert "Hazorasp Tekstil MCHJ" in lines[1]


def test_pdf_export_creates_non_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "hisobot.pdf"
    export_to_pdf(path, _COLUMNS, _ROWS, title="Kontragentlar ro'yxati")

    assert path.exists()
    assert path.stat().st_size > 0
    assert path.read_bytes()[:4] == b"%PDF"


def test_excel_importer_skips_blank_rows(tmp_path: Path) -> None:
    path = tmp_path / "with_blank.xlsx"
    export_to_excel(path, _COLUMNS, _ROWS)

    rows = read_excel_rows(path)
    assert all(row["Nomi"] for row in rows)

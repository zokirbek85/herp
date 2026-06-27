"""Har qanday jadvalni CSV formatiga eksport qilish."""

import csv
from pathlib import Path

from app.export.column_spec import ExportColumn


def export_to_csv(path: Path, columns: list[ExportColumn], rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    # utf-8-sig: Excel Kirill/lotin harflarni BOM'siz noto'g'ri ochadi.
    with path.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([column.header for column in columns])
        for row in rows:
            writer.writerow([column.format_value(row) for column in columns])
    return path

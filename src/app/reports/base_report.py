"""Bosma hisobotlar uchun umumiy konteyner — har bir hisobot shablon o'z sarlavhasi va
qatorlarini tayyorlaydi, fayl formatiga oid kod yozmaydi (`export/` qatlamiga delegatsiya)."""

from dataclasses import dataclass
from pathlib import Path

from app.export.column_spec import ExportColumn
from app.export.csv_exporter import export_to_csv
from app.export.excel_exporter import export_to_excel
from app.export.pdf_exporter import export_to_pdf

_EXCEL_SHEET_TITLE_MAX_LEN = 31


@dataclass(frozen=True, slots=True)
class ReportTable:
    title: str
    columns: list[ExportColumn]
    rows: list[dict]

    def to_excel(self, path: Path) -> Path:
        return export_to_excel(path, self.columns, self.rows, sheet_title=self.title[:_EXCEL_SHEET_TITLE_MAX_LEN])

    def to_csv(self, path: Path) -> Path:
        return export_to_csv(path, self.columns, self.rows)

    def to_pdf(self, path: Path, *, company_name: str = "Hazorasp Tekstil MCHJ") -> Path:
        return export_to_pdf(path, self.columns, self.rows, title=self.title, company_name=company_name)

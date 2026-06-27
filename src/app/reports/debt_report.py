"""Debitorlik hisoboti: eng katta qarzdor kontragentlar ro'yxati."""

from app.export.column_spec import ExportColumn
from app.reports.base_report import ReportTable
from app.services.analytics_service import AnalyticsService

_AMOUNT_FORMATTER = "{:,.2f}".format

_COLUMNS = [
    ExportColumn("Kontragent", "name"),
    ExportColumn("INN", "inn"),
    ExportColumn("Qarz", "debt", formatter=_AMOUNT_FORMATTER),
]


def build_top_debtors_report(*, limit: int = 10) -> ReportTable:
    rows = [
        {"name": row.contragent.name, "inn": row.contragent.inn or "", "debt": row.amount}
        for row in AnalyticsService().top_debtors(limit=limit)
    ]
    return ReportTable(title="Eng katta qarzdorlar", columns=_COLUMNS, rows=rows)

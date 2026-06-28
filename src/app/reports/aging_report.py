"""Aging (debitorlik yoshi) hisoboti — eksport uchun."""

from datetime import date

from app.database.session import session_scope
from app.export.column_spec import ExportColumn
from app.reports.base_report import ReportTable
from app.services.aging_service import AgingService

_AMOUNT_FORMATTER = "{:,.2f}".format

_COLUMNS = [
    ExportColumn("Kontragent", "name"),
    ExportColumn("INN", "inn"),
    ExportColumn("0-30 kun", "b0", formatter=_AMOUNT_FORMATTER),
    ExportColumn("31-60 kun", "b1", formatter=_AMOUNT_FORMATTER),
    ExportColumn("61-90 kun", "b2", formatter=_AMOUNT_FORMATTER),
    ExportColumn("91+ kun", "b3", formatter=_AMOUNT_FORMATTER),
    ExportColumn("Jami qarz", "total", formatter=_AMOUNT_FORMATTER),
    ExportColumn("Eng qadimgi (kun)", "oldest"),
]


def build_aging_report(as_of: date | None = None) -> ReportTable:
    with session_scope() as session:
        rows_data = AgingService(session).build(as_of)

    rows = [
        {
            "name": row.contragent_name,
            "inn": row.inn or "",
            "b0": row.buckets[0].amount,
            "b1": row.buckets[1].amount,
            "b2": row.buckets[2].amount,
            "b3": row.buckets[3].amount,
            "total": row.total_debt,
            "oldest": row.oldest_invoice_days,
        }
        for row in rows_data
    ]

    as_of_str = (as_of or date.today()).strftime("%d.%m.%Y")
    return ReportTable(
        title=f"Debitorlik yoshi — {as_of_str} holatiga",
        columns=_COLUMNS,
        rows=rows,
    )

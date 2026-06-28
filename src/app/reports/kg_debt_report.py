"""Mahsulot miqdori (kg) qarzdorlik hisoboti: har bir shartnoma/mahsulot bo'yicha qoldiq kg."""

from app.database.session import session_scope
from app.export.column_spec import ExportColumn
from app.reports.base_report import ReportTable
from app.repositories.contract_repository import ContractRepository
from app.repositories.contragent_repository import ContragentRepository
from app.services.financial_summary_service import FinancialSummaryService

_KG_FORMATTER = "{:,.3f}".format
_PCT_FORMATTER = "{:,.2f}".format

_COLUMNS = [
    ExportColumn("Kontragent", "contragent"),
    ExportColumn("Shartnoma", "contract_number"),
    ExportColumn("Mahsulot", "product"),
    ExportColumn("Rejalashtirilgan (kg)", "planned_kg", formatter=_KG_FORMATTER),
    ExportColumn("Yetkazilgan (kg)", "shipped_kg", formatter=_KG_FORMATTER),
    ExportColumn("Qoldiq (kg)", "remaining_kg", formatter=_KG_FORMATTER),
    ExportColumn("Bajarilish %", "pct", formatter=_PCT_FORMATTER),
]


def build_kg_debt_report() -> ReportTable:
    rows = []
    with session_scope() as session:
        contract_repo = ContractRepository(session)
        contragent_repo = ContragentRepository(session)
        summary_service = FinancialSummaryService(session)

        for contract in contract_repo.list_all():
            summary = summary_service.build(contract)
            if not summary.per_product:
                continue
            contragent = contragent_repo.get_by_id(contract.contragent_id)
            contragent_name = contragent.name if contragent is not None else "Noma'lum"

            for product_summary in summary.per_product:
                if product_summary.remaining_kg <= 0:
                    continue
                rows.append(
                    {
                        "contragent": contragent_name,
                        "contract_number": contract.contract_number,
                        "product": product_summary.product_name,
                        "planned_kg": product_summary.planned_kg,
                        "shipped_kg": product_summary.shipped_kg,
                        "remaining_kg": product_summary.remaining_kg,
                        "pct": product_summary.completion_pct,
                    }
                )

    return ReportTable(title="Mahsulot (kg) qarzdorlik hisoboti", columns=_COLUMNS, rows=rows)

"""Kontragent kesimida hisobot: bitta kontragentning barcha shartnomalari va qarzi."""

from app.export.column_spec import ExportColumn
from app.reports.base_report import ReportTable
from app.services.contract_service import ContractService
from app.services.contragent_service import ContragentService

_AMOUNT_FORMATTER = "{:,.2f}".format

_COLUMNS = [
    ExportColumn("Shartnoma №", "contract_number"),
    ExportColumn("Sana", "contract_date"),
    ExportColumn("Valyuta", "currency"),
    ExportColumn("Summa", "amount", formatter=_AMOUNT_FORMATTER),
    ExportColumn("Status", "status"),
    ExportColumn("Qarz", "debt", formatter=_AMOUNT_FORMATTER),
]


def build_contragent_report(contragent_id: int) -> ReportTable:
    contragent_service = ContragentService()
    contract_service = ContractService()

    contragent = contragent_service.get(contragent_id)
    rows = []
    for contract in contract_service.list_by_contragent(contragent_id):
        summary = contract_service.get_financial_summary(contract.id)
        rows.append(
            {
                "contract_number": contract.contract_number,
                "contract_date": contract.contract_date.strftime("%d.%m.%Y"),
                "currency": contract.currency.value,
                "amount": contract.amount,
                "status": contract.status.value,
                "debt": summary.debt,
            }
        )

    return ReportTable(title=f"{contragent.name} — Shartnomalar", columns=_COLUMNS, rows=rows)

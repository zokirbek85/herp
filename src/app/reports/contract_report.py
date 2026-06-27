"""Shartnoma kesimida hisobot: bitta shartnomaning barcha ortishlari."""

from decimal import Decimal

from app.export.column_spec import ExportColumn
from app.reports.base_report import ReportTable
from app.services.contract_service import ContractService
from app.services.shipment_service import ShipmentService

_AMOUNT_FORMATTER = "{:,.2f}".format

_COLUMNS = [
    ExportColumn("Ortish raqami", "shipment_number"),
    ExportColumn("Sana", "shipment_date"),
    ExportColumn("Invoice", "invoice_number"),
    ExportColumn("TTN", "ttn_number"),
    ExportColumn("Summa", "amount", formatter=_AMOUNT_FORMATTER),
]


def build_contract_report(contract_id: int) -> ReportTable:
    contract_service = ContractService()
    shipment_service = ShipmentService()

    contract = contract_service.get(contract_id)
    rows = []
    for shipment in shipment_service.list_by_contract(contract_id):
        items = shipment_service.list_items(shipment.id)
        total = sum((item.amount for item in items), Decimal("0"))
        rows.append(
            {
                "shipment_number": shipment.shipment_number,
                "shipment_date": shipment.shipment_date.strftime("%d.%m.%Y"),
                "invoice_number": shipment.invoice_number or "",
                "ttn_number": shipment.ttn_number or "",
                "amount": total,
            }
        )

    return ReportTable(
        title=f"Shartnoma {contract.contract_number} — Ortishlar",
        columns=_COLUMNS,
        rows=rows,
    )

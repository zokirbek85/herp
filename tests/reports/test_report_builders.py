"""reports/ shablonlarini va export'ga uzatilishini tekshiradi."""

import uuid
from datetime import date
from decimal import Decimal
from pathlib import Path

from app.core.enums import Currency, PaymentType
from app.reports.contract_report import build_contract_report
from app.reports.contragent_report import build_contragent_report
from app.reports.debt_report import build_top_debtors_report
from app.services.contract_service import ContractService
from app.services.contragent_service import ContragentService
from app.services.dto import ShipmentItemInput
from app.services.payment_service import PaymentService
from app.services.product_service import ProductService
from app.services.shipment_service import ShipmentService


def _build_sample_contract() -> tuple[int, int]:
    contragent = ContragentService().create(name=f"Report Kontragent {uuid.uuid4().hex[:8]}")
    product = ProductService().create(name="Report Mahsulot", sku=f"REPORT-{uuid.uuid4().hex[:8]}")
    contract = ContractService().create(
        contract_number=f"REPORT-{uuid.uuid4().hex[:8]}",
        contragent_id=contragent.id,
        currency=Currency.USD,
        amount=Decimal("1000.00"),
        contract_date=date(2026, 1, 1),
    )
    ShipmentService().create_shipment(
        contract_id=contract.id,
        shipment_number=f"REPORT-SH-{uuid.uuid4().hex[:8]}",
        shipment_date=date(2026, 1, 10),
        invoice_number="INV-REPORT-1",
        ttn_number="TTN-REPORT-1",
        items=[ShipmentItemInput(product_id=product.id, kg=Decimal("100.000"), price=Decimal("5.0000"))],
    )
    PaymentService().create_payment(
        contract_id=contract.id,
        payment_date=date(2026, 1, 15),
        amount=Decimal("200.00"),
        payment_type=PaymentType.ADVANCE,
    )
    return contragent.id, contract.id


def test_contract_report_lists_shipments_and_exports(tmp_path: Path) -> None:
    _contragent_id, contract_id = _build_sample_contract()

    report = build_contract_report(contract_id)
    assert len(report.rows) == 1
    assert report.rows[0]["invoice_number"] == "INV-REPORT-1"
    assert report.rows[0]["amount"] == Decimal("500.00")

    excel_path = report.to_excel(tmp_path / "contract.xlsx")
    pdf_path = report.to_pdf(tmp_path / "contract.pdf")
    csv_path = report.to_csv(tmp_path / "contract.csv")

    assert excel_path.exists()
    assert pdf_path.exists()
    assert csv_path.exists()


def test_contragent_report_shows_debt(tmp_path: Path) -> None:
    contragent_id, contract_id = _build_sample_contract()

    report = build_contragent_report(contragent_id)
    assert len(report.rows) == 1
    assert report.rows[0]["debt"] == Decimal("300.00")

    pdf_path = report.to_pdf(tmp_path / "contragent.pdf")
    assert pdf_path.exists()


def test_debt_report_includes_contragent_with_debt(tmp_path: Path) -> None:
    contragent_id, _contract_id = _build_sample_contract()
    expected_name = ContragentService().get(contragent_id).name

    report = build_top_debtors_report(limit=10_000)
    matching = [row for row in report.rows if row["name"] == expected_name]

    assert len(matching) == 1
    assert matching[0]["debt"] == Decimal("300.00")

    excel_path = report.to_excel(tmp_path / "debt.xlsx")
    assert excel_path.exists()

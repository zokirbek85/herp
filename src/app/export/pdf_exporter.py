"""Har qanday jadvalni PDF formatiga eksport qilish (korxona logosi bilan)."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.export.column_spec import ExportColumn

_HEADER_COLOR = colors.HexColor("#1F4E78")
_ALT_ROW_COLOR = colors.HexColor("#F2F2F2")


def export_to_pdf(
    path: Path,
    columns: list[ExportColumn],
    rows: list[dict],
    *,
    title: str,
    company_name: str = "Hazorasp Tekstil MCHJ",
    logo_path: Path | None = None,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()

    document = SimpleDocTemplate(
        str(path),
        pagesize=landscape(A4),
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    elements = []
    if logo_path is not None and logo_path.exists():
        elements.append(Image(str(logo_path), width=2.5 * cm, height=2.5 * cm))
    elements.append(Paragraph(company_name, styles["Heading2"]))
    elements.append(Paragraph(title, styles["Heading3"]))
    elements.append(Spacer(1, 0.5 * cm))

    table_data = [[column.header for column in columns]]
    table_data.extend(
        [column.format_value(row) for column in columns] for row in rows
    )

    table = Table(table_data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), _HEADER_COLOR),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _ALT_ROW_COLOR]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    elements.append(table)
    document.build(elements)
    return path

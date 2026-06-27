"""ContragentService.bulk_import: Excel'dan ko'plab kontragentlarni import qilish."""

import uuid

from app.services.contragent_service import ContragentService


def test_bulk_import_creates_valid_rows_and_reports_errors() -> None:
    unique_inn = uuid.uuid4().hex[:9]
    rows = [
        {"Nomi": "Import MCHJ 1", "INN": unique_inn, "Telefon": "+998901111111"},
        {"Nomi": "", "INN": "000000000"},
        {"Nomi": "Import MCHJ 2", "INN": unique_inn},  # takror INN
    ]

    result = ContragentService().bulk_import(rows)

    assert len(result.created) == 1
    assert result.created[0].name == "Import MCHJ 1"
    assert len(result.errors) == 2
    assert result.errors[0].row_number == 3
    assert result.errors[1].row_number == 4

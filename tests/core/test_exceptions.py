"""Domain exception klasslari: atributlar va xabar matni."""

import pytest

from app.core.exceptions import AppError, DuplicateError, NotFoundError, ValidationError


def test_not_found_error_exposes_entity_and_identifier() -> None:
    error = NotFoundError("Contract", 42)

    assert error.entity_name == "Contract"
    assert error.identifier == 42
    assert str(error) == "Contract topilmadi: 42"
    assert isinstance(error, AppError)


def test_duplicate_error_exposes_field_and_value() -> None:
    error = DuplicateError("Contragent", "inn", "123456789")

    assert error.entity_name == "Contragent"
    assert error.field == "inn"
    assert error.value == "123456789"
    assert str(error) == "Contragent: 'inn' = '123456789' allaqachon mavjud"
    assert isinstance(error, AppError)


def test_validation_error_is_an_app_error() -> None:
    with pytest.raises(AppError):
        raise ValidationError("Summasi musbat bo'lishi kerak")

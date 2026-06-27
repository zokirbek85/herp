"""Har qanday SQLAlchemy modelini JSON-safe dict'ga ag'darish va orqaga tiklash.

Sinxronlash paketi platformalararo (Windows/macOS) va versiyalararo barqaror bo'lishi uchun
ma'lumotlar python-ga xos turlarda (Decimal, UUID, datetime, Enum) emas, balki oddiy JSON
turlarida (str, int, float, bool, None) saqlanadi.
"""

import uuid as uuid_pkg
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from sqlalchemy import Column, Date, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Numeric, Uuid

from app.database.base import Base


def model_to_dict(obj: Base) -> dict[str, Any]:
    return {column.name: _serialize_value(getattr(obj, column.name)) for column in obj.__table__.columns}


def dict_to_model_kwargs(model_cls: type[Base], data: dict[str, Any]) -> dict[str, Any]:
    """JSON'dan o'qilgan dict qiymatlarini model ustunlari turiga moslab konvertatsiya qiladi."""
    kwargs: dict[str, Any] = {}
    for column in model_cls.__table__.columns:
        if column.name in data:
            kwargs[column.name] = _deserialize_value(data[column.name], column)
    return kwargs


def _serialize_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, uuid_pkg.UUID):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    return value


def _deserialize_value(value: Any, column: Column) -> Any:
    if value is None:
        return None
    sa_type = column.type
    if isinstance(sa_type, DateTime):
        return datetime.fromisoformat(value)
    if isinstance(sa_type, Date):
        return date.fromisoformat(value)
    if isinstance(sa_type, Numeric):
        return Decimal(str(value))
    if isinstance(sa_type, Uuid):
        return uuid_pkg.UUID(value)
    if isinstance(sa_type, SAEnum) and sa_type.enum_class is not None:
        return sa_type.enum_class(value)
    return value

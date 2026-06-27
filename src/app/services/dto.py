"""Service metodlariga uzatiladigan kirish ma'lumotlari uchun dataclass'lar."""

from dataclasses import dataclass, field
from decimal import Decimal

from app.models.contragent import Contragent


@dataclass(frozen=True, slots=True)
class ShipmentItemInput:
    product_id: int
    kg: Decimal
    price: Decimal
    lot_number: str | None = None


@dataclass(frozen=True, slots=True)
class ImportRowError:
    row_number: int
    reason: str


@dataclass(frozen=True, slots=True)
class ContragentImportResult:
    created: list[Contragent] = field(default_factory=list)
    errors: list[ImportRowError] = field(default_factory=list)

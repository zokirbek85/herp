"""Eksport qilinadigan jadval ustunini umumlashtirib tasvirlaydi.

Bir xil `ExportColumn` ro'yxati Excel, CSV va PDF eksportlarining barchasida ishlatiladi —
har bir modul (Kontragentlar, Shartnomalar va h.k.) faqat o'z ustunlari ro'yxatini tayyorlaydi,
fayl formatiga bog'liq kod yozmaydi.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ExportColumn:
    header: str
    key: str
    formatter: Callable[[Any], str] | None = None

    def format_value(self, row: dict[str, Any]) -> str:
        value = row.get(self.key)
        if value is None:
            return ""
        if self.formatter is not None:
            return self.formatter(value)
        return str(value)

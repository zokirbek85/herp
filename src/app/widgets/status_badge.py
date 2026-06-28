"""macOS uslubidagi holat belgisi (status badge)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QWidget

from app.core.enums import ContractStatus

# status_value -> (ko'rsatiladigan matn, fon rangi, matn rangi)
_STYLES: dict[str, tuple[str, str, str]] = {
    ContractStatus.NEW.value: ("Yangi", "#F2F2F7", "#8E8E93"),
    ContractStatus.IN_PROGRESS.value: ("Jarayonda", "#E5F0FF", "#0A7AFF"),
    ContractStatus.COMPLETED.value: ("Yakunlangan", "#E8F9ED", "#34C759"),
    ContractStatus.CANCELLED.value: ("Bekor", "#FFEBEA", "#FF3B30"),
}
_STYLES_DARK: dict[str, tuple[str, str, str]] = {
    ContractStatus.NEW.value: ("Yangi", "#38383A", "#8D8D93"),
    ContractStatus.IN_PROGRESS.value: ("Jarayonda", "#061A40", "#4DA3FF"),
    ContractStatus.COMPLETED.value: ("Yakunlangan", "#0D2E17", "#32D74B"),
    ContractStatus.CANCELLED.value: ("Bekor", "#2E0D0B", "#FF453A"),
}
_FALLBACK = ("Noma'lum", "#F2F2F7", "#8E8E93")


class StatusBadge(QLabel):
    """Rangli status pill badge.

    Ishlatish:
        badge = StatusBadge(ContractStatus.IN_PROGRESS)
        badge = StatusBadge("COMPLETED", dark=True)
    """

    def __init__(
        self,
        status: ContractStatus | str,
        *,
        dark: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._dark = dark
        self.set_status(status)

    def set_status(self, status: ContractStatus | str) -> None:
        key = status.value if isinstance(status, ContractStatus) else str(status)
        table = _STYLES_DARK if self._dark else _STYLES
        label, bg, fg = table.get(key, _FALLBACK)
        self.setText(label)
        self.setStyleSheet(
            f"background-color: {bg};"
            f"color: {fg};"
            f"border-radius: 5px;"
            f"padding: 2px 8px;"
            f"font-size: 11px;"
            f"font-weight: 500;"
        )
        self.setFixedHeight(20)

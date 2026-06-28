"""macOS uslubidagi KPI metrika kartochkasi."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

import qtawesome as qta

# variant -> (qiymat rangi light, qiymat rangi dark, icon nomi)
_VARIANTS: dict[str, tuple[str | None, str | None, str | None]] = {
    "default": (None, None, None),
    "success": ("#34C759", "#32D74B", "fa5s.arrow-up"),
    "danger": ("#FF3B30", "#FF453A", "fa5s.exclamation-circle"),
    "warning": ("#FF9F0A", "#FF9F0A", "fa5s.exclamation-triangle"),
    "info": ("#0A7AFF", "#4DA3FF", "fa5s.info-circle"),
    "muted": ("#8E8E93", "#8D8D93", None),
}


class KpiCard(QFrame):
    """macOS uslubidagi KPI karta.

    Args:
        title: Sarlavha (12px, muted).
        value: Asosiy raqam yoki matn (28px, weight 300).
        variant: "default"|"success"|"danger"|"warning"|"info"|"muted"
        delta: Trend matni, masalan: "↑ 12%"
        subtitle: Qo'shimcha matn, masalan: "5 ta shartnoma"
        icon_name: qtawesome icon nomi yoki None
        dark_mode: Joriy mavzu dark bo'lsa True — rang variantini moslashtiradi.
        clickable: True bo'lsa, karta ustiga bosilganda `clicked` signali chiqadi
            va kursor "qo'l" shakliga o'zgaradi (batafsil ma'lumotga o'tish uchun).
    """

    clicked = Signal()

    def __init__(
        self,
        title: str,
        value: str,
        *,
        variant: str = "default",
        delta: str | None = None,
        subtitle: str | None = None,
        icon_name: str | None = None,
        dark_mode: bool = False,
        clickable: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self._clickable = clickable
        if clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        light_color, dark_color, auto_icon = _VARIANTS.get(variant, _VARIANTS["default"])
        value_color = dark_color if dark_mode else light_color

        title_label = QLabel(title)
        title_label.setStyleSheet(
            "font-size: 12px; font-weight: 400; color: #8E8E93; background: transparent;"
        )

        value_style = (
            "font-size: 28px; font-weight: 300; background: transparent;"
            "letter-spacing: -0.5px;"
        )
        if value_color:
            value_style += f" color: {value_color};"
        self._value_label = QLabel(value)
        self._value_label.setStyleSheet(value_style)

        value_row = QHBoxLayout()
        value_row.setContentsMargins(0, 0, 0, 0)
        value_row.setSpacing(6)

        eff_icon = icon_name or auto_icon
        if eff_icon:
            icon_color = value_color or "#8E8E93"
            icon_label = QLabel()
            icon_label.setPixmap(qta.icon(eff_icon, color=icon_color).pixmap(14, 14))
            icon_label.setStyleSheet("background: transparent;")
            value_row.addWidget(icon_label)
        value_row.addWidget(self._value_label)
        value_row.addStretch()

        self._delta_label: QLabel | None = None
        if delta is not None:
            self._delta_label = QLabel(delta)
            self._delta_label.setStyleSheet(
                "font-size: 11px; color: #34C759; background: transparent;"
            )

        self._subtitle_label: QLabel | None = None
        if subtitle is not None:
            self._subtitle_label = QLabel(subtitle)
            self._subtitle_label.setStyleSheet(
                "font-size: 11px; color: #8E8E93; background: transparent;"
            )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(3)
        layout.addWidget(title_label)
        layout.addLayout(value_row)
        if self._delta_label:
            layout.addWidget(self._delta_label)
        if self._subtitle_label:
            layout.addWidget(self._subtitle_label)

    def set_value(self, value: str) -> None:
        self._value_label.setText(value)

    def set_delta(self, text: str, *, positive: bool = True) -> None:
        if self._delta_label:
            color = "#34C759" if positive else "#FF3B30"
            self._delta_label.setText(text)
            self._delta_label.setStyleSheet(
                f"font-size: 11px; color: {color}; background: transparent;"
            )

    def set_subtitle(self, subtitle: str) -> None:
        if self._subtitle_label:
            self._subtitle_label.setText(subtitle)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

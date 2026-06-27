"""Dashboard/kartochkalarda ishlatiladigan yumaloq KPI karta widget'i."""

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class KpiCard(QFrame):
    def __init__(self, title: str, value: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #9AA0A6; font-size: 12px;")

        self._value_label = QLabel(value)
        self._value_label.setStyleSheet("font-size: 22px; font-weight: 700;")

        layout = QVBoxLayout(self)
        layout.addWidget(title_label)
        layout.addWidget(self._value_label)

    def set_value(self, value: str) -> None:
        self._value_label.setText(value)

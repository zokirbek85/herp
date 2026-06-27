"""Light/Dark mavzu: Microsoft Office + Power BI uslubidagi minimalistik QSS."""

from PySide6.QtWidgets import QApplication

ACCENT = "#0F6CBD"
ACCENT_HOVER = "#115EA3"

_LIGHT_VARS = {
    "bg": "#F5F6F8",
    "surface": "#FFFFFF",
    "border": "#E1E4E8",
    "text": "#1F1F1F",
    "text_muted": "#5B6470",
    "sidebar_bg": "#FFFFFF",
    "sidebar_selected": "#EAF3FC",
    "row_alt": "#FAFBFC",
}

_DARK_VARS = {
    "bg": "#1E1F22",
    "surface": "#26282B",
    "border": "#34363A",
    "text": "#F0F1F3",
    "text_muted": "#9AA0A6",
    "sidebar_bg": "#26282B",
    "sidebar_selected": "#1B3A55",
    "row_alt": "#2C2E32",
}

_QSS_TEMPLATE = """
QWidget {{
    background-color: {bg};
    color: {text};
    font-family: "Segoe UI";
    font-size: 13px;
}}
QMainWindow, QDialog {{
    background-color: {bg};
}}
#Sidebar {{
    background-color: {sidebar_bg};
    border-right: 1px solid {border};
}}
#Sidebar QPushButton {{
    text-align: left;
    padding: 10px 16px;
    border: none;
    border-radius: 6px;
    color: {text};
    background-color: transparent;
}}
#Sidebar QPushButton:hover {{
    background-color: {sidebar_selected};
}}
#Sidebar QPushButton:checked {{
    background-color: {sidebar_selected};
    color: {accent};
    font-weight: 600;
}}
QFrame#Card {{
    background-color: {surface};
    border: 1px solid {border};
    border-radius: 10px;
}}
QPushButton#PrimaryButton {{
    background-color: {accent};
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: 600;
}}
QPushButton#PrimaryButton:hover {{
    background-color: {accent_hover};
}}
QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {{
    background-color: {surface};
    border: 1px solid {border};
    border-radius: 6px;
    padding: 6px 10px;
}}
QTableView {{
    background-color: {surface};
    border: 1px solid {border};
    border-radius: 8px;
    gridline-color: {border};
    alternate-background-color: {row_alt};
}}
QHeaderView::section {{
    background-color: {surface};
    border: none;
    border-bottom: 1px solid {border};
    padding: 6px;
    font-weight: 600;
    color: {text_muted};
}}
QStatusBar {{
    background-color: {surface};
    border-top: 1px solid {border};
    color: {text_muted};
}}
"""


def build_stylesheet(theme: str) -> str:
    variables = _DARK_VARS if theme == "dark" else _LIGHT_VARS
    return _QSS_TEMPLATE.format(accent=ACCENT, accent_hover=ACCENT_HOVER, **variables)


def apply_theme(app: QApplication, theme: str) -> None:
    app.setStyleSheet(build_stylesheet(theme))

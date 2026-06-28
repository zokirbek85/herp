"""macOS Human Interface Guidelines uslubidagi Light/Dark mavzu."""

from PySide6.QtWidgets import QApplication, QDateEdit

# ── Accent (macOS Blue) ───────────────────────────────────────────────
ACCENT = "#0A7AFF"
ACCENT_HOVER = "#0870E8"

# ── Light mode ranglari ───────────────────────────────────────────────
_LIGHT_VARS: dict[str, str] = {
    "window_bg": "#ECECEC",
    "sidebar_bg": "#E2E2E7",
    "content_bg": "#F5F5F5",
    "surface": "#FFFFFF",
    "surface_raised": "#FFFFFF",
    "border": "#D1D1D6",
    "border_subtle": "#E5E5EA",
    "text": "#1C1C1E",
    "text_secondary": "#48484A",
    "text_muted": "#8E8E93",
    "text_placeholder": "#AEAEB2",
    "row_alt": "#F2F2F7",
    "row_hover": "#E5E5EA",
    "sidebar_selected": "#DDEEFF",
    "sidebar_text_sel": "#0A7AFF",
    "success": "#34C759",
    "success_bg": "#E8F9ED",
    "success_text": "#1A7336",
    "warning": "#FF9F0A",
    "warning_bg": "#FFF3E0",
    "warning_text": "#7A4700",
    "danger": "#FF3B30",
    "danger_bg": "#FFEBEA",
    "danger_text": "#8A1A16",
    "info": "#0A7AFF",
    "info_bg": "#E5F0FF",
    "info_text": "#0A4A9E",
    "muted_bg": "#F2F2F7",
    "muted_text": "#8E8E93",
}

# ── Dark mode ranglari ────────────────────────────────────────────────
_DARK_VARS: dict[str, str] = {
    "window_bg": "#1C1C1E",
    "sidebar_bg": "#2C2C2E",
    "content_bg": "#242426",
    "surface": "#2C2C2E",
    "surface_raised": "#3A3A3C",
    "border": "#38383A",
    "border_subtle": "#2C2C2E",
    "text": "#FFFFFF",
    "text_secondary": "#EBEBF5",
    "text_muted": "#8D8D93",
    "text_placeholder": "#636366",
    "row_alt": "#1C1C1E",
    "row_hover": "#3A3A3C",
    "sidebar_selected": "#1A3A5E",
    "sidebar_text_sel": "#4DA3FF",
    "success": "#32D74B",
    "success_bg": "#0D2E17",
    "success_text": "#32D74B",
    "warning": "#FF9F0A",
    "warning_bg": "#2E1A00",
    "warning_text": "#FF9F0A",
    "danger": "#FF453A",
    "danger_bg": "#2E0D0B",
    "danger_text": "#FF453A",
    "info": "#4DA3FF",
    "info_bg": "#061A40",
    "info_text": "#4DA3FF",
    "muted_bg": "#38383A",
    "muted_text": "#636366",
}

# ── QSS Template ─────────────────────────────────────────────────────
_QSS = """
/* ── Global ── */
QWidget {{
    background-color: {window_bg};
    color: {text};
    font-family: -apple-system, "SF Pro Text", "Helvetica Neue", "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}}
QMainWindow, QDialog {{
    background-color: {window_bg};
}}

/* ── Sidebar ── */
#Sidebar {{
    background-color: {sidebar_bg};
    border-right: 1px solid {border};
}}
#SidebarLogo {{
    color: {text};
    font-size: 14px;
    font-weight: 600;
    padding: 18px 14px 10px 16px;
}}
#SidebarGroupLabel {{
    color: {text_muted};
    font-size: 11px;
    font-weight: 600;
    padding: 8px 16px 2px 16px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}}
#Sidebar QPushButton {{
    text-align: left;
    padding: 7px 12px 7px 12px;
    border: none;
    border-radius: 7px;
    color: {text_secondary};
    background-color: transparent;
    font-size: 13px;
    font-weight: 400;
}}
#Sidebar QPushButton:hover {{
    background-color: {row_hover};
    color: {text};
}}
#Sidebar QPushButton:checked {{
    background-color: {sidebar_selected};
    color: {sidebar_text_sel};
    font-weight: 500;
}}

/* ── Toolbar / Content areas ── */
#ContentArea {{
    background-color: {content_bg};
}}
#Toolbar {{
    background-color: {content_bg};
    border-bottom: 1px solid {border_subtle};
    padding: 8px 16px;
}}
#PageTitle {{
    font-size: 17px;
    font-weight: 600;
    color: {text};
}}

/* ── Cards ── */
QFrame#Card {{
    background-color: {surface};
    border: 1px solid {border};
    border-radius: 10px;
    padding: 0px;
}}
QFrame#Card:hover {{
    border-color: {text_placeholder};
}}

/* ── Buttons ── */
QPushButton {{
    background-color: {surface};
    color: {text};
    border: 1px solid {border};
    border-radius: 7px;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: 400;
}}
QPushButton:hover {{
    background-color: {row_hover};
    border-color: {text_placeholder};
}}
QPushButton:pressed {{
    background-color: {border};
}}
QPushButton:disabled {{
    color: {text_muted};
    border-color: {border_subtle};
}}
QPushButton#PrimaryButton {{
    background-color: {accent};
    color: #FFFFFF;
    border: none;
    border-radius: 7px;
    padding: 6px 16px;
    font-weight: 500;
}}
QPushButton#PrimaryButton:hover {{
    background-color: {accent_hover};
}}
QPushButton#PrimaryButton:pressed {{
    background-color: {accent_hover};
}}
QPushButton#DestructiveButton {{
    background-color: {danger_bg};
    color: {danger};
    border: 1px solid {danger};
    border-radius: 7px;
    padding: 6px 14px;
}}
QPushButton#DestructiveButton:hover {{
    background-color: {danger};
    color: #FFFFFF;
}}

/* ── Input fields ── */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {surface};
    color: {text};
    border: 1px solid {border};
    border-radius: 7px;
    padding: 6px 10px;
    selection-background-color: {info_bg};
    selection-color: {text};
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 2px solid {accent};
    padding: 5px 9px;
}}
QLineEdit::placeholder, QTextEdit::placeholder {{
    color: {text_placeholder};
}}

/* ── ComboBox ── */
QComboBox {{
    background-color: {surface};
    color: {text};
    border: 1px solid {border};
    border-radius: 7px;
    padding: 6px 10px;
    min-width: 80px;
}}
QComboBox:focus {{
    border: 2px solid {accent};
    padding: 5px 9px;
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox::down-arrow {{
    image: none;
    width: 10px;
    height: 10px;
}}
QComboBox QAbstractItemView {{
    background-color: {surface_raised};
    border: 1px solid {border};
    border-radius: 10px;
    selection-background-color: {info_bg};
    selection-color: {text};
    padding: 4px;
    outline: none;
}}

/* ── SpinBox / DateEdit ── */
QSpinBox, QDoubleSpinBox, QDateEdit {{
    background-color: {surface};
    color: {text};
    border: 1px solid {border};
    border-radius: 7px;
    padding: 6px 10px;
}}
QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
    border: 2px solid {accent};
}}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    border: none;
    background: transparent;
    width: 16px;
}}

/* ── Tables ── */
QTableWidget, QTableView {{
    background-color: {surface};
    color: {text};
    border: none;
    border-radius: 0px;
    gridline-color: {border_subtle};
    alternate-background-color: {row_alt};
    selection-background-color: {info_bg};
    selection-color: {text};
    outline: none;
}}
QTableWidget::item, QTableView::item {{
    padding: 6px 10px;
    border: none;
}}
QTableWidget::item:hover, QTableView::item:hover {{
    background-color: {row_hover};
}}
QTableWidget::item:selected, QTableView::item:selected {{
    background-color: {sidebar_selected};
    color: {text};
}}
QHeaderView {{
    background-color: {surface};
    border: none;
}}
QHeaderView::section {{
    background-color: {surface};
    color: {text_muted};
    font-size: 12px;
    font-weight: 600;
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid {border};
    border-right: none;
    letter-spacing: 0.02em;
}}
QHeaderView::section:first {{
    border-top-left-radius: 0px;
}}

/* ── Dialogs ── */
QDialog {{
    background-color: {window_bg};
    border-radius: 14px;
}}
QDialogButtonBox QPushButton {{
    min-width: 80px;
}}

/* ── Form ── */
QFormLayout QLabel {{
    color: {text_secondary};
    font-size: 13px;
}}

/* ── ScrollBars — yupqa macOS uslubi ── */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 2px 2px 2px 0;
}}
QScrollBar::handle:vertical {{
    background: {border};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {text_placeholder};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none; height: 0;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 8px;
    margin: 0 0 2px 2px;
}}
QScrollBar::handle:horizontal {{
    background: {border};
    border-radius: 4px;
    min-width: 24px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {text_placeholder};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: none; width: 0;
}}

/* ── Status bar ── */
QStatusBar {{
    background-color: {sidebar_bg};
    border-top: 1px solid {border};
    color: {text_muted};
    font-size: 12px;
}}
QStatusBar QLabel {{
    padding: 0 8px;
}}

/* ── Message boxes ── */
QMessageBox {{
    background-color: {window_bg};
}}
QMessageBox QPushButton {{
    min-width: 80px;
}}

/* ── Tab widget (agar kerak bo'lsa) ── */
QTabWidget::pane {{
    border: 1px solid {border};
    border-radius: 10px;
    background-color: {surface};
    top: -1px;
}}
QTabBar::tab {{
    background: transparent;
    color: {text_muted};
    padding: 6px 16px;
    border: none;
    font-size: 13px;
}}
QTabBar::tab:selected {{
    color: {text};
    font-weight: 500;
    border-bottom: 2px solid {accent};
}}
QTabBar::tab:hover {{
    color: {text};
}}

/* ── Toolbar separator ── */
QToolBar {{
    border: none;
    background: {content_bg};
    spacing: 6px;
    padding: 4px 8px;
}}

/* ── Calendar popup (QDateEdit) ── */
QCalendarWidget {{
    background-color: {surface_raised};
    border: 1px solid {border};
    border-radius: 10px;
}}
QCalendarWidget QWidget#qt_calendar_navigationbar {{
    background-color: {surface_raised};
}}
QCalendarWidget QToolButton {{
    background-color: transparent;
    color: {text};
    border: none;
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 13px;
}}
QCalendarWidget QToolButton:hover {{
    background-color: {row_hover};
}}
QCalendarWidget QSpinBox {{
    background-color: {surface};
    color: {text};
    border: 1px solid {border};
    border-radius: 5px;
    padding: 2px 4px;
    min-height: 20px;
}}
QCalendarWidget QAbstractItemView {{
    background-color: {surface_raised};
    color: {text};
    selection-background-color: {accent};
    selection-color: #FFFFFF;
    outline: none;
}}
QCalendarWidget QHeaderView::section {{
    background-color: {surface_raised};
    color: {text_muted};
    border: none;
    padding: 4px;
    font-size: 11px;
    font-weight: 600;
}}
"""


def build_stylesheet(theme: str) -> str:
    """Light yoki Dark QSS stilini qaytaradi."""
    variables = _DARK_VARS if theme == "dark" else _LIGHT_VARS
    return _QSS.format(accent=ACCENT, accent_hover=ACCENT_HOVER, **variables)


def style_calendar_popup(date_edit: QDateEdit) -> None:
    """`QDateEdit` kalendar popup'ini to'g'ri o'lchamda ko'rsatilishini ta'minlaydi.

    QSS qo'llangandan keyin `QCalendarWidget`ning ichki kun jadvali uchun avtomatik
    hisoblangan balandlik haqiqiy render qilinadigan satrlardan kichikroq bo'lib qolishi
    mumkin — natijada oxirgi haftalar popup chegarasidan tashqariga "toshib" chiqadi.
    Minimal o'lcham qo'yib bu muammoning oldi olinadi.
    """
    calendar = date_edit.calendarWidget()
    if calendar is not None:
        calendar.setMinimumSize(300, 260)


def apply_theme(app: QApplication, theme: str) -> None:
    app.setStyleSheet(build_stylesheet(theme))


def get_color(key: str, theme: str = "light") -> str:
    """Bitta rang qiymatini qaytaradi — widget ichida ishlatish uchun."""
    variables = _DARK_VARS if theme == "dark" else _LIGHT_VARS
    return variables.get(key, "#000000")

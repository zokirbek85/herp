"""Ilova ishga tushishida ko'rsatiladigan splash screen (DB migration shu vaqtda bajariladi)."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QSplashScreen

from app.config.theme import ACCENT


def build_splash_screen(app_name: str, app_version: str) -> QSplashScreen:
    pixmap = QPixmap(480, 280)
    pixmap.fill(QColor("#FFFFFF"))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QColor(ACCENT))
    title_font = painter.font()
    title_font.setPointSize(22)
    title_font.setBold(True)
    painter.setFont(title_font)
    painter.drawText(pixmap.rect().adjusted(0, -20, 0, 0), Qt.AlignmentFlag.AlignCenter, app_name)

    subtitle_font = painter.font()
    subtitle_font.setPointSize(11)
    subtitle_font.setBold(False)
    painter.setFont(subtitle_font)
    painter.setPen(QColor("#5B6470"))
    painter.drawText(pixmap.rect().adjusted(0, 40, 0, 0), Qt.AlignmentFlag.AlignCenter, f"v{app_version}")
    painter.end()

    splash = QSplashScreen(pixmap)
    splash.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
    return splash

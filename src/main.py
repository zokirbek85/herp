"""Hazorasp Sales Management — ilova kirish nuqtasi."""

import sys

from loguru import logger
from PySide6.QtWidgets import QApplication

from app.config.preferences import load_theme
from app.config.settings import get_settings
from app.config.theme import apply_theme
from app.database.migrations import run_upgrade_to_head
from app.utils.paths import get_log_dir
from app.views.main_window import MainWindow
from app.views.splash_screen import build_splash_screen


def _configure_logging() -> None:
    logger.remove()
    logger.add(get_log_dir() / "app.log", rotation="5 MB", retention=5, encoding="utf-8")


def main() -> int:
    _configure_logging()
    settings = get_settings()

    app = QApplication(sys.argv)
    theme = load_theme(settings.theme)
    apply_theme(app, theme)

    splash = build_splash_screen(settings.app_name, settings.app_version)
    splash.show()
    app.processEvents()

    run_upgrade_to_head()

    window = MainWindow(initial_theme=theme)
    window.show()
    splash.finish(window)

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

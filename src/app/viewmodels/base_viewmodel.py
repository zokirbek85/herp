"""Barcha ViewModel'lar uchun umumiy signal kontrakti.

ViewModel View'ni bilmaydi (signal orqali xabar beradi), Service/Repository'ni esa to'g'ridan-to'g'ri
chaqiradi — bu MVVM qatlamlanishi UI testlarini Qt'siz ham yozish imkonini beradi.
"""

from collections.abc import Callable

from PySide6.QtCore import QObject, Signal


class BaseViewModel(QObject):
    busy_changed = Signal(bool)
    error_occurred = Signal(str)

    def run_safely(self, action: Callable[[], None]) -> bool:
        """`AppError`larni ushlab `error_occurred` signaliga aylantiradi.

        UI qatlami business-exception turlarini bilishi shart emas — faqat foydalanuvchiga
        ko'rsatiladigan tayyor matnni oladi.
        """
        from app.core.exceptions import AppError

        self.busy_changed.emit(True)
        try:
            action()
            return True
        except AppError as exc:
            self.error_occurred.emit(str(exc))
            return False
        finally:
            self.busy_changed.emit(False)

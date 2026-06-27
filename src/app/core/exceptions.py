"""Domain darajasidagi custom exception'lar. Repository/Service qatlamlari shu hierarchiyadan foydalanadi."""


class AppError(Exception):
    """Barcha domain xatoliklari uchun bazaviy klass."""


class NotFoundError(AppError):
    """So'ralgan yozuv topilmadi."""

    def __init__(self, entity_name: str, identifier: object) -> None:
        self.entity_name = entity_name
        self.identifier = identifier
        super().__init__(f"{entity_name} topilmadi: {identifier!r}")


class DuplicateError(AppError):
    """Unique constraint buzilishi (masalan, takror INN yoki shartnoma raqami)."""

    def __init__(self, entity_name: str, field: str, value: object) -> None:
        self.entity_name = entity_name
        self.field = field
        self.value = value
        super().__init__(f"{entity_name}: '{field}' = {value!r} allaqachon mavjud")


class ValidationError(AppError):
    """Biznes qoidasi buzilishi (masalan, manfiy summa, noto'g'ri valyuta)."""


class InsufficientFundsError(AppError):
    """FIFO to'lov taqsimotida mablag' yetarli emas."""


class SyncConflictError(AppError):
    """Sinxronlash paytida hal qilinmagan conflict aniqlandi."""

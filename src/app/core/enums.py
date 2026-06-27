"""Domain darajasidagi enum turlari. Hech qanday tashqi kutubxonaga bog'liq emas."""

from enum import StrEnum


class Currency(StrEnum):
    USD = "USD"
    UZS = "UZS"


class ContractStatus(StrEnum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class PaymentType(StrEnum):
    ADVANCE = "ADVANCE"
    REGULAR = "REGULAR"
    OVERPAYMENT = "OVERPAYMENT"


class UserRole(StrEnum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"


class SyncDirection(StrEnum):
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"


class SyncStatus(StrEnum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CONFLICT = "CONFLICT"

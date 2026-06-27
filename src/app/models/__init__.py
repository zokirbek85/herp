"""Barcha ORM modellarini markazlashtirib eksport qiladi.

Bu import Alembic autogenerate uchun va relationship'lardagi forward-reference
string'larni (masalan "Contract") to'g'ri resolve qilish uchun zarur — barcha
model klasslari `Base.metadata`ga ro'yxatdan o'tishi kerak.
"""

from app.database.base import Base
from app.models.contract import Contract
from app.models.contract_specification import ContractSpecification
from app.models.contragent import Contragent
from app.models.exchange_rate import ExchangeRate
from app.models.payment import Payment
from app.models.payment_allocation import PaymentAllocation
from app.models.product import Product
from app.models.shipment import Shipment
from app.models.shipment_item import ShipmentItem
from app.models.sync_log import SyncLog
from app.models.user import User

__all__ = [
    "Base",
    "Contract",
    "ContractSpecification",
    "Contragent",
    "ExchangeRate",
    "Payment",
    "PaymentAllocation",
    "Product",
    "Shipment",
    "ShipmentItem",
    "SyncLog",
    "User",
]

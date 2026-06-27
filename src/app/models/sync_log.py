from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import SyncDirection, SyncStatus
from app.database.base import AuditMixin, Base


class SyncLog(Base, AuditMixin):
    __tablename__ = "sync_logs"

    device_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    direction: Mapped[SyncDirection] = mapped_column(
        Enum(SyncDirection, native_enum=False, length=10), nullable=False
    )
    package_path: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[SyncStatus] = mapped_column(Enum(SyncStatus, native_enum=False, length=10), nullable=False)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    conflicts_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<SyncLog id={self.id} direction={self.direction} status={self.status}>"

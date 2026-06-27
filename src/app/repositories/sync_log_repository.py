from collections.abc import Sequence

from sqlalchemy import select

from app.models.sync_log import SyncLog
from app.repositories.base_repository import BaseRepository


class SyncLogRepository(BaseRepository[SyncLog]):
    model = SyncLog

    def list_recent(self, *, limit: int = 50) -> Sequence[SyncLog]:
        stmt = select(SyncLog).order_by(SyncLog.executed_at.desc()).limit(limit)
        return self.session.execute(stmt).scalars().all()

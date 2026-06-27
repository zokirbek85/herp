"""Session factory va Unit-of-Work uchun context manager.

Transaction boundary Service qatlamida boshqariladi: bir Service metodi bitta `session_scope()`
ichida bir nechta Repository chaqiruvini bog'laydi va oxirida commit/rollback qiladi.
"""

from collections.abc import Generator
from contextlib import contextmanager

from loguru import logger
from sqlalchemy.orm import Session, sessionmaker

from app.database.engine import get_engine

SessionFactory = sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Bitta transaction'ni o'z ichiga olgan Session beradi. Xatolik bo'lsa avtomatik rollback qiladi."""
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        logger.exception("Transaction rollback qilindi")
        raise
    finally:
        session.close()

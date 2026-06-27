"""SQLAlchemy engine yaratish. Butun ilova bo'ylab yagona Engine instansiyasi ishlatiladi."""

from functools import lru_cache

from sqlalchemy import Engine, create_engine

from app.config.settings import get_settings


@lru_cache
def get_engine() -> Engine:
    """Lazy-singleton Engine. DuckDB fayliga ulanadi, internet/server talab qilinmaydi."""
    settings = get_settings()
    return create_engine(settings.database_url, echo=settings.echo_sql, future=True)

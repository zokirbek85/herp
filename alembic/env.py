import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from app.config.settings import get_settings  # noqa: E402
from app.database.migrations import DuckDBImpl  # noqa: E402, F401
from app.models import Base  # noqa: E402

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", get_settings().database_url)

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def process_revision_directives(context, revision, directives) -> None:
    """Har bir yangi jadval uchun PK Sequence'ni avtomatik qo'shadi.

    DuckDB SERIAL/IDENTITY'ni qo'llab-quvvatlamaydi (app.database.base.AuditMixin'ga qarang),
    lekin Alembic autogenerate standalone Sequence'larni o'z-o'zidan chiqarmaydi. Shu sababli
    har bir `CreateTableOp`dan oldin mos Sequence yaratish, `DropTableOp`dan keyin esa
    o'chirish operatsiyasi qo'lda in'ektsiya qilinadi — bu kelajakdagi barcha
    `alembic revision --autogenerate` chaqiruvlarida avtomatik ishlaydi.
    """
    from alembic.operations import ops

    script = directives[0]

    if script.upgrade_ops:
        new_ops = []
        for op_ in script.upgrade_ops.ops:
            if isinstance(op_, ops.CreateTableOp):
                new_ops.append(ops.ExecuteSQLOp(f"CREATE SEQUENCE {op_.table_name}_id_seq"))
            new_ops.append(op_)
        script.upgrade_ops.ops = new_ops

    if script.downgrade_ops:
        new_ops = []
        for op_ in script.downgrade_ops.ops:
            new_ops.append(op_)
            if isinstance(op_, ops.DropTableOp):
                new_ops.append(
                    ops.ExecuteSQLOp(f"DROP SEQUENCE IF EXISTS {op_.table_name}_id_seq")
                )
        script.downgrade_ops.ops = new_ops


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

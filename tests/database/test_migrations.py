"""run_upgrade_to_head(): bir nechta marta chaqirilishi xatosiz o'tishi kerak (idempotent)."""

from app.database.migrations import run_upgrade_to_head


def test_run_upgrade_to_head_is_idempotent() -> None:
    run_upgrade_to_head()
    run_upgrade_to_head()

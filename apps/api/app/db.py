"""Database connection helpers and migration runner."""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# alembic.ini lives at the package root (apps/api/), one level above this file's
# directory (apps/api/app/).
_ALEMBIC_INI = Path(__file__).parent.parent / "alembic.ini"


def run_migrations() -> None:
    """Run pending Alembic migrations.  No-op when DATABASE_URL is not set."""
    from app.config import settings

    if settings.database_url is None:
        logger.debug("DATABASE_URL not set — skipping migrations (JsonStore mode)")
        return

    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config(str(_ALEMBIC_INI))
    logger.info("Running Alembic migrations…")
    command.upgrade(alembic_cfg, "head")
    logger.info("Migrations complete.")

"""ARQ queue utilities.

The pool is created lazily on first use so the API can start without Redis
when running in JsonStore / local dev mode without Docker.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_pool = None


async def get_pool():  # type: ignore[return]
    """Return (and lazily create) the shared ARQ Redis pool."""
    global _pool
    if _pool is None:
        from arq.connections import RedisSettings, create_pool

        from app.config import settings

        _pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    return _pool


async def enqueue_cv_job(job_id: str) -> None:
    """Enqueue a CV processing job.  Logs a warning and skips on failure."""
    try:
        pool = await get_pool()
        await pool.enqueue_job("process_video", job_id)
        logger.info("Enqueued cv job %s", job_id)
    except Exception as exc:
        logger.warning("Could not enqueue cv job %s: %s", job_id, exc)


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.aclose()
        _pool = None

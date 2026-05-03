import asyncio
import logging

import httpx
from fastapi import APIRouter

from app.config import settings
from app.services.store import store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["health"])


async def _check_postgres() -> str:
    if settings.database_url is None:
        return "skipped (no DATABASE_URL)"
    try:
        import psycopg2

        def _ping() -> None:
            conn = psycopg2.connect(settings.psycopg2_url)
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
            finally:
                conn.close()

        await asyncio.to_thread(_ping)
        return "ok"
    except Exception as exc:
        logger.warning("Postgres health check failed: %s", exc)
        return f"error: {exc}"


async def _check_redis() -> str:
    try:
        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.redis_url, socket_connect_timeout=3)
        await r.ping()
        await r.aclose()
        return "ok"
    except Exception as exc:
        logger.warning("Redis health check failed: %s", exc)
        return f"error: {exc}"


async def _check_minio() -> str:
    try:
        import boto3
        from botocore.config import Config as BotocoreConfig

        scheme = "https" if settings.minio_secure else "http"

        def _ping() -> None:
            s3 = boto3.client(
                "s3",
                endpoint_url=f"{scheme}://{settings.minio_endpoint}",
                aws_access_key_id=settings.minio_access_key,
                aws_secret_access_key=settings.minio_secret_key,
                config=BotocoreConfig(signature_version="s3v4", connect_timeout=3, read_timeout=3),
                region_name="us-east-1",
            )
            s3.list_buckets()

        await asyncio.to_thread(_ping)
        return "ok"
    except Exception as exc:
        logger.warning("MinIO health check failed: %s", exc)
        return f"error: {exc}"


async def _check_ollama() -> str:
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{settings.ollama_host}/api/tags")
            resp.raise_for_status()
        return "ok"
    except Exception as exc:
        logger.warning("Ollama health check failed: %s", exc)
        return f"error: {exc}"


@router.get("/health")
async def health() -> dict[str, object]:
    postgres, redis, minio, ollama = await asyncio.gather(
        _check_postgres(),
        _check_redis(),
        _check_minio(),
        _check_ollama(),
    )
    deps: dict[str, str] = {
        "postgres": postgres,
        "redis": redis,
        "minio": minio,
        "ollama": ollama,
    }
    all_ok = all(v in ("ok", "skipped (no DATABASE_URL)") for v in deps.values())
    return {
        "status": "ok" if all_ok else "degraded",
        "version": "0.1.0-mvp",
        "storage_mode": store.storage_mode,
        "dependencies": deps,
    }

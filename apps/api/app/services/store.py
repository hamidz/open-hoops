from __future__ import annotations

import io
import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

import asyncio

from fastapi import HTTPException, UploadFile, status

from app.config import settings
from app.models import AnalyticsSummary, Job

logger = logging.getLogger(__name__)


class StorageBackend(Protocol):
    storage_mode: str

    def save_job(self, job: Job) -> None: ...

    def get_job(self, job_id: str) -> Job | None: ...

    def list_jobs(self) -> list[Job]: ...

    def delete_job(self, job_id: str) -> None: ...

    def save_analytics(self, summary: AnalyticsSummary) -> str: ...

    def get_analytics(self, job_id: str) -> AnalyticsSummary | None: ...

    async def save_upload(self, video: UploadFile, job_id: str, suffix: str) -> tuple[int, str]: ...

    def save_frame_zero(self, job_id: str, content: bytes) -> str: ...

    @staticmethod
    def now() -> datetime: ...

    @staticmethod
    def as_jsonable(value: Any) -> Any: ...


class JsonStore:
    storage_mode = "local_json"
    _chunk_size = 1024 * 1024

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or settings.open_hoops_data_dir
        self.jobs_dir = self.base_dir / "jobs"
        self.videos_dir = self.base_dir / "videos"
        self.artifacts_dir = self.base_dir / "artifacts"
        for directory in (self.jobs_dir, self.videos_dir, self.artifacts_dir):
            directory.mkdir(parents=True, exist_ok=True)

    def job_path(self, job_id: str) -> Path:
        return self.jobs_dir / f"{job_id}.json"

    def analytics_path(self, job_id: str) -> Path:
        return self.artifacts_dir / job_id / "analytics_summary.json"

    def analytics_url(self, job_id: str) -> str:
        return f"file://{self.analytics_path(job_id)}"

    def _write_atomic(self, path: Path, text: str) -> None:
        """Write *text* to *path* atomically (write to .tmp then rename)."""
        tmp = path.with_suffix(".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)

    def save_job(self, job: Job) -> None:
        self._write_atomic(self.job_path(job.job_id), job.model_dump_json(indent=2))

    def get_job(self, job_id: str) -> Job | None:
        path = self.job_path(job_id)
        if not path.exists():
            return None
        return Job.model_validate_json(path.read_text(encoding="utf-8"))

    def list_jobs(self) -> list[Job]:
        jobs: list[Job] = []
        for path in self.jobs_dir.glob("*.json"):
            try:
                jobs.append(Job.model_validate_json(path.read_text(encoding="utf-8")))
            except Exception as exc:
                logger.warning("Skipping corrupt job file %s: %s", path.name, exc)
        return sorted(jobs, key=lambda job: job.created_at, reverse=True)

    def delete_job(self, job_id: str) -> None:
        self.job_path(job_id).unlink(missing_ok=True)
        for directory in (self.videos_dir / job_id, self.artifacts_dir / job_id):
            if directory.exists():
                shutil.rmtree(directory)

    def save_analytics(self, summary: AnalyticsSummary) -> str:
        path = self.analytics_path(summary.job_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._write_atomic(path, summary.model_dump_json(indent=2))
        return self.analytics_url(summary.job_id)

    async def save_upload(self, video: UploadFile, job_id: str, suffix: str) -> tuple[int, str]:
        video_dir = self.videos_dir / job_id
        video_dir.mkdir(parents=True, exist_ok=True)
        video_path = video_dir / f"video{suffix}"
        file_size = 0
        with video_path.open("wb") as fp:
            while True:
                chunk = await video.read(self._chunk_size)
                if not chunk:
                    break
                file_size += len(chunk)
                if file_size > settings.max_upload_size_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail={
                            "error": "file_too_large",
                            "detail": "Video exceeds the configured upload limit.",
                        },
                    )
                fp.write(chunk)
        return file_size, f"file://{video_path}"

    def save_frame_zero(self, job_id: str, content: bytes) -> str:
        artifact_dir = self.artifacts_dir / job_id
        artifact_dir.mkdir(parents=True, exist_ok=True)
        frame_path = artifact_dir / "frame_0.jpg"
        frame_path.write_bytes(content)
        return f"file://{frame_path}"

    def get_analytics(self, job_id: str) -> AnalyticsSummary | None:
        path = self.analytics_path(job_id)
        if not path.exists():
            return None
        return AnalyticsSummary.model_validate_json(path.read_text(encoding="utf-8"))

    @staticmethod
    def now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def as_jsonable(value: Any) -> Any:
        return json.loads(json.dumps(value, default=str))


class DatabaseStore:
    """Postgres + MinIO backed store used when DATABASE_URL is set."""

    storage_mode = "database"
    _videos_bucket = "videos"
    _artifacts_bucket = "artifacts"
    _telemetry_bucket = "telemetry"
    _chunk_size = 1024 * 1024  # 1 MiB

    # ---------------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------------

    def _connect(self):  # type: ignore[return]
        import psycopg2
        import psycopg2.extras

        db_url = settings.psycopg2_url
        assert db_url is not None, "DATABASE_URL must be set to use DatabaseStore"
        conn = psycopg2.connect(db_url, cursor_factory=psycopg2.extras.RealDictCursor)
        conn.autocommit = False
        return conn

    def _s3(self):  # type: ignore[return]
        import boto3
        from botocore.config import Config as BotocoreConfig

        scheme = "https" if settings.minio_secure else "http"
        return boto3.client(
            "s3",
            endpoint_url=f"{scheme}://{settings.minio_endpoint}",
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
            config=BotocoreConfig(signature_version="s3v4"),
            region_name="us-east-1",
        )

    @staticmethod
    def _row_to_job(row: Any) -> Job:
        return Job(
            schema_version=row["schema_version"],
            job_id=row["job_id"],
            status=row["status"],
            progress_pct=row["progress_pct"],
            label=row["label"],
            sport=row["sport"],
            original_filename=row["original_filename"],
            file_size_bytes=row["file_size_bytes"],
            video_url=row["video_url"],
            frame_zero_url=row["frame_zero_url"],
            calibration_json=row["calibration_json"],
            telemetry_url=row["telemetry_url"],
            analytics_summary_url=row["analytics_summary_url"],
            report_url=row["report_url"],
            error_message=row["error_message"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _delete_prefix(self, bucket: str, prefix: str) -> None:
        """Best-effort deletion of all MinIO objects under *prefix*."""
        s3 = self._s3()
        try:
            paginator = s3.get_paginator("list_objects_v2")
            keys = [
                {"Key": obj["Key"]}
                for page in paginator.paginate(Bucket=bucket, Prefix=prefix)
                for obj in page.get("Contents", [])
            ]
            if keys:
                s3.delete_objects(Bucket=bucket, Delete={"Objects": keys})
        except Exception as exc:
            logger.warning("MinIO cleanup failed for %s/%s: %s", bucket, prefix, exc)

    # ---------------------------------------------------------------------------
    # StorageBackend protocol implementation
    # ---------------------------------------------------------------------------

    def save_job(self, job: Job) -> None:
        import psycopg2.extras

        conn = self._connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO jobs (
                            job_id, schema_version, status, progress_pct, label, sport,
                            original_filename, file_size_bytes, video_url, frame_zero_url,
                            calibration_json, telemetry_url, analytics_summary_url,
                            report_url, error_message, created_at, updated_at
                        ) VALUES (
                            %(job_id)s, %(schema_version)s, %(status)s, %(progress_pct)s,
                            %(label)s, %(sport)s, %(original_filename)s, %(file_size_bytes)s,
                            %(video_url)s, %(frame_zero_url)s, %(calibration_json)s,
                            %(telemetry_url)s, %(analytics_summary_url)s, %(report_url)s,
                            %(error_message)s, %(created_at)s, %(updated_at)s
                        )
                        ON CONFLICT (job_id) DO UPDATE SET
                            status                = EXCLUDED.status,
                            progress_pct          = EXCLUDED.progress_pct,
                            label                 = EXCLUDED.label,
                            frame_zero_url        = EXCLUDED.frame_zero_url,
                            calibration_json      = EXCLUDED.calibration_json,
                            telemetry_url         = EXCLUDED.telemetry_url,
                            analytics_summary_url = EXCLUDED.analytics_summary_url,
                            report_url            = EXCLUDED.report_url,
                            error_message         = EXCLUDED.error_message,
                            updated_at            = EXCLUDED.updated_at
                        """,
                        {
                            "job_id": job.job_id,
                            "schema_version": job.schema_version,
                            "status": job.status,
                            "progress_pct": job.progress_pct,
                            "label": job.label,
                            "sport": job.sport,
                            "original_filename": job.original_filename,
                            "file_size_bytes": job.file_size_bytes,
                            "video_url": job.video_url,
                            "frame_zero_url": job.frame_zero_url,
                            "calibration_json": psycopg2.extras.Json(job.calibration_json)
                            if job.calibration_json is not None
                            else None,
                            "telemetry_url": job.telemetry_url,
                            "analytics_summary_url": job.analytics_summary_url,
                            "report_url": job.report_url,
                            "error_message": job.error_message,
                            "created_at": job.created_at,
                            "updated_at": job.updated_at,
                        },
                    )
        finally:
            conn.close()

    def get_job(self, job_id: str) -> Job | None:
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM jobs WHERE job_id = %s", (job_id,))
                row = cur.fetchone()
                return self._row_to_job(row) if row else None
        finally:
            conn.close()

    def list_jobs(self) -> list[Job]:
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM jobs ORDER BY created_at DESC")
                return [self._row_to_job(row) for row in cur.fetchall()]
        finally:
            conn.close()

    def delete_job(self, job_id: str) -> None:
        self._delete_prefix(self._videos_bucket, f"{job_id}/")
        self._delete_prefix(self._artifacts_bucket, f"{job_id}/")
        self._delete_prefix(self._telemetry_bucket, f"{job_id}/")
        conn = self._connect()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM jobs WHERE job_id = %s", (job_id,))
        finally:
            conn.close()

    def save_analytics(self, summary: AnalyticsSummary) -> str:
        key = f"{summary.job_id}/analytics_summary.json"
        self._s3().put_object(
            Bucket=self._artifacts_bucket,
            Key=key,
            Body=summary.model_dump_json(indent=2).encode("utf-8"),
            ContentType="application/json",
        )
        return f"s3://{self._artifacts_bucket}/{key}"

    def get_analytics(self, job_id: str) -> AnalyticsSummary | None:
        key = f"{job_id}/analytics_summary.json"
        try:
            response = self._s3().get_object(Bucket=self._artifacts_bucket, Key=key)
            return AnalyticsSummary.model_validate_json(response["Body"].read())
        except Exception as exc:
            logger.warning("Could not fetch analytics for %s: %s", job_id, exc)
            return None

    async def save_upload(self, video: UploadFile, job_id: str, suffix: str) -> tuple[int, str]:
        buf = io.BytesIO()
        file_size = 0
        while True:
            chunk = await video.read(self._chunk_size)
            if not chunk:
                break
            file_size += len(chunk)
            if file_size > settings.max_upload_size_bytes:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail={
                        "error": "file_too_large",
                        "detail": "Video exceeds the configured upload limit.",
                    },
                )
            buf.write(chunk)
        buf.seek(0)
        key = f"{job_id}/video{suffix}"
        await asyncio.to_thread(
            self._s3().upload_fileobj,
            buf,
            self._videos_bucket,
            key,
            {"ContentType": "video/mp4"},
        )
        return file_size, f"s3://{self._videos_bucket}/{key}"

    def save_frame_zero(self, job_id: str, content: bytes) -> str:
        key = f"{job_id}/frame_0.jpg"
        self._s3().put_object(
            Bucket=self._artifacts_bucket,
            Key=key,
            Body=content,
            ContentType="image/jpeg",
        )
        return f"s3://{self._artifacts_bucket}/{key}"

    @staticmethod
    def now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def as_jsonable(value: Any) -> Any:
        return json.loads(json.dumps(value, default=str))


def _make_store() -> StorageBackend:
    if settings.database_url is not None:
        logger.info("DATABASE_URL is set — using DatabaseStore (Postgres + MinIO)")
        return DatabaseStore()
    logger.info("DATABASE_URL not set — using JsonStore (local filesystem)")
    return JsonStore()


store: StorageBackend = _make_store()

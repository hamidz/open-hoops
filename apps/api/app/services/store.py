from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

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
            except Exception:
                logger.warning("Skipping corrupt job file: %s", path.name)
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
                        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
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


store: StorageBackend = JsonStore()

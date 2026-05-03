from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from app.config import settings
from app.models import AnalyticsSummary, Job


class StorageBackend(Protocol):
    storage_mode: str

    def save_job(self, job: Job) -> None: ...

    def get_job(self, job_id: str) -> Job | None: ...

    def list_jobs(self) -> list[Job]: ...

    def delete_job(self, job_id: str) -> None: ...

    def save_analytics(self, summary: AnalyticsSummary) -> str: ...

    def get_analytics(self, job_id: str) -> AnalyticsSummary | None: ...

    def save_video(self, job_id: str, suffix: str, content: bytes) -> str: ...

    def save_frame_zero(self, job_id: str, content: bytes) -> str: ...

    @staticmethod
    def now() -> datetime: ...

    @staticmethod
    def as_jsonable(value: Any) -> Any: ...


class JsonStore:
    storage_mode = "local_json"

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

    def save_job(self, job: Job) -> None:
        self.job_path(job.job_id).write_text(job.model_dump_json(indent=2), encoding="utf-8")

    def get_job(self, job_id: str) -> Job | None:
        path = self.job_path(job_id)
        if not path.exists():
            return None
        return Job.model_validate_json(path.read_text(encoding="utf-8"))

    def list_jobs(self) -> list[Job]:
        jobs = [
            Job.model_validate_json(path.read_text(encoding="utf-8"))
            for path in self.jobs_dir.glob("*.json")
        ]
        return sorted(jobs, key=lambda job: job.created_at, reverse=True)

    def delete_job(self, job_id: str) -> None:
        self.job_path(job_id).unlink(missing_ok=True)
        for directory in (self.videos_dir / job_id, self.artifacts_dir / job_id):
            if directory.exists():
                shutil.rmtree(directory)

    def save_analytics(self, summary: AnalyticsSummary) -> str:
        path = self.analytics_path(summary.job_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(summary.model_dump_json(indent=2), encoding="utf-8")
        return self.analytics_url(summary.job_id)

    def save_video(self, job_id: str, suffix: str, content: bytes) -> str:
        video_dir = self.videos_dir / job_id
        video_dir.mkdir(parents=True, exist_ok=True)
        video_path = video_dir / f"video{suffix}"
        video_path.write_bytes(content)
        return f"file://{video_path}"

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

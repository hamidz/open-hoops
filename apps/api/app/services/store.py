from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import settings
from app.models import AnalyticsSummary, Job


class JsonStore:
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
                for child in directory.rglob("*"):
                    if child.is_file():
                        child.unlink()
                for child in sorted(directory.rglob("*"), reverse=True):
                    if child.is_dir():
                        child.rmdir()
                directory.rmdir()

    def save_analytics(self, summary: AnalyticsSummary) -> None:
        path = self.analytics_path(summary.job_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(summary.model_dump_json(indent=2), encoding="utf-8")

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


store = JsonStore()

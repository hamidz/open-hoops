from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class JobStatus(StrEnum):
    queued = "queued"
    processing = "processing"
    calibration_needed = "calibration_needed"
    complete = "complete"
    failed = "failed"


class Job(BaseModel):
    schema_version: str = "1.0"
    job_id: str
    status: JobStatus
    progress_pct: int = Field(ge=0, le=100)
    label: str | None = None
    sport: str = "basketball"
    original_filename: str
    file_size_bytes: int = Field(ge=0)
    video_url: str
    frame_zero_url: str | None = None
    calibration_json: dict[str, Any] | None = None
    telemetry_url: str | None = None
    analytics_summary_url: str | None = None
    report_url: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

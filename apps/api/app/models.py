from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

JobStatus = Literal["queued", "processing", "calibration_needed", "complete", "failed"]


class ErrorResponse(BaseModel):
    error: str
    detail: str


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


class UploadResponse(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime


class ZoneDistribution(BaseModel):
    paint_pct: float
    midrange_pct: float
    three_point_pct: float


class PlayerAnalytics(BaseModel):
    track_id: int
    label: str | None = None
    team: str
    total_distance_m: float
    avg_speed_ms: float
    max_speed_ms: float
    court_coverage_pct: float
    zone_distribution: ZoneDistribution


class AnalyticsSummary(BaseModel):
    schema_version: str = "1.0"
    job_id: str
    computed_at: datetime
    annotations_applied: bool = False
    duration_seconds: int
    total_sampled_frames: int
    avg_detections_per_frame: float
    ball_tracking_coverage_pct: float
    team_spacing_avg_m: float
    players: list[PlayerAnalytics]

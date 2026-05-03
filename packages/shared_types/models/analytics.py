from datetime import datetime

from pydantic import BaseModel, Field


class ZoneDistribution(BaseModel):
    paint_pct: float = Field(ge=0, le=100)
    midrange_pct: float = Field(ge=0, le=100)
    three_point_pct: float = Field(ge=0, le=100)


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

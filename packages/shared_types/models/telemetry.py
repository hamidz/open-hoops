from pydantic import BaseModel


class Detection(BaseModel):
    track_id: int
    object_class: str
    bbox_px: tuple[int, int, int, int]
    confidence: float
    court_xy_m: tuple[float, float] | None = None
    team: str | None = None
    label: str | None = None


class TelemetryFrame(BaseModel):
    frame_index: int
    timestamp_ms: int
    detections: list[Detection]


class TelemetryDocument(BaseModel):
    schema_version: str = "1.0"
    job_id: str
    sport: str = "basketball"
    frames: list[TelemetryFrame]

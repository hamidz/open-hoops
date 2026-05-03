"""
Calibration router — Phase 06.

Endpoints:
  POST   /api/v1/jobs/{job_id}/calibrate    Submit calibration point pairs
  GET    /api/v1/jobs/{job_id}/calibrate    Retrieve current calibration
  DELETE /api/v1/jobs/{job_id}/calibrate    Clear calibration (reset to calibration_needed)
  GET    /api/v1/calibration/reference      Return the 9 standard reference court points
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.homography import (
    REFERENCE_POINTS,
    CalibrationError,
    calibration_to_json,
    compute_homography,
)
from app.services.store import store

router = APIRouter(prefix="/api/v1", tags=["calibration"])


# ── Request / response models ─────────────────────────────────────────────────

class PointPair(BaseModel):
    point_id: str = Field(..., description="Stable reference point identifier (e.g. 'court_tl')")
    image_x: float = Field(..., description="Pixel x in frame_zero image")
    image_y: float = Field(..., description="Pixel y in frame_zero image")


class CalibrateRequest(BaseModel):
    points: list[PointPair] = Field(
        ...,
        min_length=4,
        description="At least 4 image→court point correspondences",
    )


class CalibrateResponse(BaseModel):
    job_id: str
    status: str
    points_used: int
    homography_matrix: list[list[float]]


class ReferencePointsResponse(BaseModel):
    points: dict[str, tuple[float, float]]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_job_or_404(job_id: str):  # noqa: ANN202
    job = store.get_job(job_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found", "detail": "Job not found."},
        )
    return job


def _validate_point_ids(point_ids: list[str]) -> None:
    unknown = [pid for pid in point_ids if pid not in REFERENCE_POINTS]
    if unknown:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "unknown_point_ids",
                "detail": f"Unknown point IDs: {unknown}. Valid IDs: {list(REFERENCE_POINTS)}",
            },
        )


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/calibration/reference", response_model=ReferencePointsResponse)
def get_reference_points() -> ReferencePointsResponse:
    """Return the 9 standard NBA court calibration reference points (feet)."""
    return ReferencePointsResponse(points=REFERENCE_POINTS)


@router.post("/jobs/{job_id}/calibrate", response_model=CalibrateResponse)
def calibrate_job(job_id: str, body: CalibrateRequest) -> CalibrateResponse:
    """
    Submit pixel→court calibration point pairs and compute the homography matrix.

    The matrix is persisted in calibration_json and the job status is advanced
    from 'calibration_needed' → 'queued' (ready for CV processing).
    """
    job = _get_job_or_404(job_id)

    if job.status not in ("calibration_needed", "queued", "failed"):
        raise HTTPException(
            status_code=409,
            detail={
                "error": "invalid_state",
                "detail": f"Calibration cannot be applied to a job with status '{job.status}'.",
            },
        )

    point_ids = [p.point_id for p in body.points]
    _validate_point_ids(point_ids)

    image_points = [(p.image_x, p.image_y) for p in body.points]
    court_points = [REFERENCE_POINTS[p.point_id] for p in body.points]

    try:
        H = compute_homography(image_points, court_points)
    except CalibrationError as exc:
        raise HTTPException(
            status_code=422,
            detail={"error": "calibration_failed", "detail": str(exc)},
        ) from exc

    job.calibration_json = calibration_to_json(H, image_points, court_points, point_ids)
    if job.status == "calibration_needed":
        job.status = "queued"
        job.progress_pct = 0
    job.updated_at = store.now()
    store.save_job(job)

    return CalibrateResponse(
        job_id=job_id,
        status=job.status,
        points_used=len(body.points),
        homography_matrix=H.tolist(),
    )


@router.get("/jobs/{job_id}/calibrate")
def get_calibration(job_id: str) -> dict:
    """Return the stored calibration data for a job."""
    job = _get_job_or_404(job_id)
    if job.calibration_json is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found", "detail": "No calibration data for this job."},
        )
    return {"job_id": job_id, "calibration": job.calibration_json}


@router.delete("/jobs/{job_id}/calibrate", status_code=status.HTTP_204_NO_CONTENT)
def delete_calibration(job_id: str):
    """Clear calibration data and reset job to calibration_needed."""
    job = _get_job_or_404(job_id)
    job.calibration_json = None
    job.status = "calibration_needed"
    job.updated_at = store.now()
    store.save_job(job)

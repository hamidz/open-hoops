import re
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Query, Response, UploadFile, status

from app.models import AnalyticsSummary, Job, UploadResponse
from app.services.analytics import generate_first_workflow_stats
from app.services.store import store
from app.services.uploads import create_upload_job

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])
RETRY_STARTED_PROGRESS = 50
_LIST_JOBS_MAX = 200
_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)


def _validate_job_id(job_id: str) -> None:
    if not _UUID_RE.match(job_id):
        raise HTTPException(
            status_code=400, detail={"error": "invalid_id", "detail": "job_id must be a UUID."}
        )


def _job_or_404(job_id: str) -> Job:
    _validate_job_id(job_id)
    job = store.get_job(job_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found", "detail": "Job not found."},
        )
    return job


@router.get("", response_model=list[Job])
def list_jobs(
    limit: Annotated[int, Query(ge=1, le=_LIST_JOBS_MAX)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Job]:
    return store.list_jobs()[offset : offset + limit]


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_job(
    video: Annotated[UploadFile, File()],
    label: Annotated[str | None, Form()] = None,
    sport: Annotated[str, Form()] = "basketball",
) -> UploadResponse:
    job = await create_upload_job(video, label, sport)
    return UploadResponse(job_id=job.job_id, status=job.status, created_at=job.created_at)


@router.get("/{job_id}", response_model=Job)
def get_job(job_id: str) -> Job:
    return _job_or_404(job_id)


@router.get("/{job_id}/analytics", response_model=AnalyticsSummary)
def get_analytics(job_id: str) -> AnalyticsSummary:
    _job_or_404(job_id)
    summary = store.get_analytics(job_id)
    if summary is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found", "detail": "Analytics not found."},
        )
    return summary


@router.post("/{job_id}/retry", response_model=Job)
def retry_job(job_id: str) -> Job:
    job = _job_or_404(job_id)
    if job.status != "failed":
        raise HTTPException(
            status_code=409,
            detail={"error": "invalid_state", "detail": "Only failed jobs can be retried."},
        )
    job.status = "processing"
    job.progress_pct = RETRY_STARTED_PROGRESS
    job.error_message = None
    summary = generate_first_workflow_stats(job.job_id, job.file_size_bytes)
    store.save_analytics(summary)
    job.status = "complete"
    job.progress_pct = 100
    job.analytics_summary_url = f"file://{store.analytics_path(job.job_id)}"
    job.updated_at = store.now()
    store.save_job(job)
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: str) -> Response:
    _job_or_404(job_id)
    store.delete_job(job_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.config import settings
from app.models import Job
from app.services.analytics import generate_first_workflow_stats
from app.services.store import store

ALLOWED_EXTENSIONS = {".mp4", ".mov"}


def validate_upload(filename: str, size: int) -> None:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail={"error": "unsupported_media_type", "detail": "Upload an .mp4 or .mov video."},
        )
    if size > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error": "file_too_large",
                "detail": "Video exceeds the configured upload limit.",
            },
        )


async def create_upload_job(video: UploadFile, label: str | None, sport: str) -> Job:
    original_filename = video.filename or "upload.mp4"
    content = await video.read()
    validate_upload(original_filename, len(content))

    job_id = str(uuid4())
    suffix = Path(original_filename).suffix.lower()
    created_at = store.now()
    video_dir = store.videos_dir / job_id
    video_dir.mkdir(parents=True, exist_ok=True)
    video_path = video_dir / f"video{suffix}"
    video_path.write_bytes(content)

    artifact_dir = store.artifacts_dir / job_id
    artifact_dir.mkdir(parents=True, exist_ok=True)
    frame_path = artifact_dir / "frame_0.txt"
    frame_path.write_text(
        "Frame-zero placeholder: calibration image extraction is implemented in Phase 06.\n",
        encoding="utf-8",
    )

    summary = generate_first_workflow_stats(job_id, len(content))
    store.save_analytics(summary)

    job = Job(
        job_id=job_id,
        status="complete",
        progress_pct=100,
        label=label or Path(original_filename).stem,
        sport=sport or "basketball",
        original_filename=original_filename,
        file_size_bytes=len(content),
        video_url=f"file://{video_path}",
        frame_zero_url=f"file://{frame_path}",
        analytics_summary_url=f"file://{store.analytics_path(job_id)}",
        created_at=created_at,
        updated_at=store.now(),
    )
    store.save_job(job)
    return job

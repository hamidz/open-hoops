from __future__ import annotations

from base64 import b64decode
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.config import settings
from app.models import Job
from app.services.analytics import generate_first_workflow_stats
from app.services.store import store

ALLOWED_EXTENSIONS = {".mp4", ".mov"}
# Minimal valid 1x1 JPEG until Phase 06 extracts a real frame-zero image.
PLACEHOLDER_JPEG = b64decode(
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////2wBDAf//////////////////////////////////////////////////////////////////////////////////////wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAX/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIQAxAAAAH/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAEFAqf/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oACAEDAQE/ASP/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oACAECAQE/ASP/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAY/Al//xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAE/IV//2gAMAwEAAgADAAAAEP/EABQRAQAAAAAAAAAAAAAAAAAAABD/2gAIAQMBAT8QP//EABQRAQAAAAAAAAAAAAAAAAAAABD/2gAIAQIBAT8QP//EABQQAQAAAAAAAAAAAAAAAAAAABD/2gAIAQEAAT8QP//Z"
)


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

    # Validate extension before reading a single byte (size=0 skips the size check).
    validate_upload(original_filename, 0)

    job_id = str(uuid4())
    suffix = Path(original_filename).suffix.lower()
    created_at = store.now()
    try:
        file_size, video_url = await store.save_upload(video, job_id, suffix)
        frame_zero_url = store.save_frame_zero(job_id, PLACEHOLDER_JPEG)
        summary = generate_first_workflow_stats(job_id, file_size)
        analytics_summary_url = store.save_analytics(summary)

        job = Job(
            job_id=job_id,
            status="complete",
            progress_pct=100,
            label=label if label is not None else Path(original_filename).stem,
            sport=sport,
            original_filename=original_filename,
            file_size_bytes=file_size,
            video_url=video_url,
            frame_zero_url=frame_zero_url,
            analytics_summary_url=analytics_summary_url,
            created_at=created_at,
            updated_at=store.now(),
        )
        store.save_job(job)
    except Exception:
        # Clean up any partially-created directories so failed uploads don't leave debris.
        store.delete_job(job_id)
        raise
    return job

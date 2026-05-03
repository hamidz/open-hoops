#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from app.models import Job  # noqa: E402
from app.services.analytics import generate_first_workflow_stats  # noqa: E402
from app.services.store import store  # noqa: E402


def main() -> None:
    job_id = "00000000-0000-4000-8000-000000000001"
    now = store.now()
    summary = generate_first_workflow_stats(job_id, 2_000_000)
    store.save_analytics(summary)
    job = Job(
        job_id=job_id,
        status="complete",
        progress_pct=100,
        label="Mock 5v5 scrimmage",
        sport="basketball",
        original_filename="mock_scrimmage.mp4",
        file_size_bytes=2_000_000,
        video_url="mock://videos/mock_scrimmage.mp4",
        analytics_summary_url=f"file://{store.analytics_path(job_id)}",
        created_at=now,
        updated_at=now,
    )
    store.save_job(job)
    print(f"Seeded mock job {job_id}")


if __name__ == "__main__":
    main()

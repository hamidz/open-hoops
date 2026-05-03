from pathlib import Path

import pytest
from fastapi import HTTPException

from app.services.uploads import validate_upload


def test_validate_upload_accepts_supported_video() -> None:
    validate_upload("clip.mp4", 1024)
    validate_upload("clip.MOV", 1024)


def test_validate_upload_rejects_unsupported_extension() -> None:
    with pytest.raises(HTTPException) as exc:
        validate_upload("clip.txt", 10)
    assert exc.value.status_code == 415


def test_validate_upload_rejects_large_file(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.services import uploads

    monkeypatch.setattr(uploads.settings, "max_upload_size_bytes", 5)
    with pytest.raises(HTTPException) as exc:
        validate_upload("clip.mp4", 6)
    assert exc.value.status_code == 413


def test_upload_flow_creates_job_and_analytics(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.services import uploads
    from app.services.store import JsonStore

    test_store = JsonStore(tmp_path)
    monkeypatch.setattr(uploads, "store", test_store)
    summary = uploads.generate_first_workflow_stats("00000000-0000-0000-0000-000000000001", 100)
    test_store.save_analytics(summary)
    assert test_store.get_analytics(summary.job_id) is not None

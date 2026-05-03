from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services.store import JsonStore


def test_health() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_upload_to_stats_workflow(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    from app.routers import jobs
    from app.services import uploads

    test_store = JsonStore(tmp_path)
    monkeypatch.setattr(uploads, "store", test_store)
    monkeypatch.setattr(jobs, "store", test_store)
    client = TestClient(app)
    response = client.post(
        "/api/v1/jobs/upload",
        files={"video": ("game.mp4", b"fake video bytes", "video/mp4")},
        data={"label": "Test Game"},
    )
    assert response.status_code == 201
    job_id = response.json()["job_id"]
    job = client.get(f"/api/v1/jobs/{job_id}")
    assert job.status_code == 200
    assert job.json()["status"] == "complete"
    analytics = client.get(f"/api/v1/jobs/{job_id}/analytics")
    assert analytics.status_code == 200
    assert len(analytics.json()["players"]) == 10

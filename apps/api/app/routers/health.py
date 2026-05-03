from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "version": "0.1.0-mvp",
        "storage_mode": "local_json",
        "workflow_mode": "mock-first",
        "dependencies": {
            "api": "ok",
            "storage": "local_json",
        },
    }

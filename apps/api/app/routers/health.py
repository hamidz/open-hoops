from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "services": {
            "api": "ok",
            "storage": "local",
            "analytics": "mock-first-workflow",
        },
    }

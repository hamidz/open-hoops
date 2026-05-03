import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import Response

from app.config import settings
from app.routers import calibration, health, jobs


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Run Alembic migrations before accepting traffic (no-op when DATABASE_URL unset).
    from app.db import run_migrations

    await asyncio.to_thread(run_migrations)
    yield
    # Graceful shutdown: close the ARQ Redis pool if it was opened.
    from app.services.queue import close_pool

    await close_pool()


app = FastAPI(title="Open Hoops API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health.router)
app.include_router(jobs.router)
app.include_router(calibration.router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> Response:
    if isinstance(exc, StarletteHTTPException):
        return await http_exception_handler(request, exc)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "detail": "Unexpected server error."},
    )

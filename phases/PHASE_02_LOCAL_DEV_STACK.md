# Phase 02 — Local Dev Stack

> **Goal:** Build and validate the full local Docker Compose development environment. All services start, connect to each other, and pass a basic health check.

---

## Status: 🔲 Pending

---

## Prerequisites

- Phase 01 complete (monorepo structure scaffolded).

---

## Agent Instructions

Read `ARCHITECTURE.md` for service definitions and `docs/STACK.md` for technology choices before starting.

Your job is to implement `infra/docker-compose.yml` and all service Dockerfiles such that a single `docker compose up` starts the full stack. Do not implement business logic — just working, connected infrastructure.

---

## Services To Configure

| Service | Image | Port | Notes |
|---|---|---|---|
| `postgres` | `postgres:16` | 5432 | DB for job records |
| `redis` | `redis:7-alpine` | 6379 | Job queue |
| `minio` | `minio/minio` | 9000 (API), 9001 (console) | Object storage |
| `ollama` | `ollama/ollama` | 11434 | Local LLM |
| `api` | `./apps/api` | 8000 | FastAPI backend |
| `web` | `./apps/web` | 3000 | Next.js frontend |
| `cv_worker` | `./services/cv_worker` | — | Background worker |
| `analytics_worker` | `./services/analytics_worker` | — | Background worker |
| `llm_service` | `./services/llm_service` | — | LLM report generator |

---

## Tasks

### Docker Compose

- [ ] Write `infra/docker-compose.yml` with all services above.
- [ ] Define a shared `app-network` bridge network.
- [ ] Define named volumes: `postgres_data`, `redis_data`, `minio_data`, `ollama_data`.
- [ ] Configure all service `depends_on` relationships correctly.
- [ ] Add health checks for `postgres`, `redis`, `minio`.

### Environment Variables

- [ ] Write `infra/.env.example` with all required variables:
  - `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
  - `REDIS_URL`
  - `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`, `MINIO_ENDPOINT`
  - `OLLAMA_HOST`
  - `API_URL` (for frontend)
- [ ] Confirm `.env` is in `.gitignore`.

### PostgreSQL

- [ ] Create initial DB schema migration (Alembic):
  - `jobs` table: `job_id` (UUID PK), `status`, `video_url`, `created_at`, `updated_at`
  - Additional columns: `calibration_json`, `telemetry_url`, `analytics_url`, `report_url`
- [ ] Alembic `env.py` reads `DATABASE_URL` from environment.

### MinIO

- [ ] Add MinIO startup script or init container to create default buckets:
  - `videos`
  - `telemetry`
  - `artifacts`

### API Health Check

- [ ] Implement `GET /health` endpoint in FastAPI that checks connectivity to:
  - PostgreSQL
  - Redis
  - MinIO

### Task Queue

- [ ] Decide and implement: ARQ or Celery (see ADR note in `docs/ADR.md`).
- [ ] Worker services read jobs from Redis queue.
- [ ] Implement a `noop` job type that workers can process as a connectivity test.

### Validation

- [ ] `docker compose up` starts all services without error.
- [ ] `curl http://localhost:8000/health` returns `200 OK` with all services healthy.
- [ ] MinIO console accessible at `http://localhost:9001`.
- [ ] Ollama responds to `curl http://localhost:11434/api/tags`.

---

## Outputs

- `infra/docker-compose.yml` — complete and valid.
- `infra/.env.example` — all variables documented.
- `apps/api/app/routers/health.py` — health check endpoint.
- Alembic migration for initial `jobs` table.
- MinIO bucket init script.
- All services reachable and healthy.

---

## Definition of Done

- [ ] `docker compose up --build` succeeds with no exit errors.
- [ ] `GET /health` returns HTTP 200 with all checks passing.
- [ ] All tasks above checked off.
- [ ] Phase status updated in `AGENTIC_EXECUTION_PLAN.md`.

---

## Completion Note

> _Agent: add completion date and summary here when done._

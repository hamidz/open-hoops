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

- [ ] `infra/docker-compose.yml` already created — review against Phase 02 requirements.
- [ ] All services include `healthcheck` definitions _(already included in template)_.
- [ ] All services include `deploy.resources.limits` memory caps _(already included — see `ARCHITECTURE.md` Section 2.8)_.
- [ ] Named volumes use `name:` prefix: `open_hoops_postgres_data`, etc. _(already in template)_.
- [ ] `minio-init` container creates `videos`, `telemetry`, and `artifacts` buckets _(already in template)_.

### Environment Variables

- [x] Root `.env.example` documents all required variables _(created)_.
- [ ] Confirm `.env` is in `.gitignore`.

### PostgreSQL

- [ ] Create initial DB schema migration (Alembic):
  - `jobs` table: `job_id` (UUID PK), `status`, `video_url`, `created_at`, `updated_at`
  - Additional columns: `calibration_json`, `telemetry_url`, `analytics_summary_url`, `report_url`, `progress_pct`
- [ ] Alembic `env.py` reads `DATABASE_URL` from environment.

### Redis Persistence

- [x] Redis RDB persistence configured in `docker-compose.yml` (`save 900 1 300 10 60 10000`) _(already in template)_.
- [ ] Test: stop Redis, restart it, confirm queued ARQ jobs survive restart.

### MinIO

- [x] `minio-init` container handles bucket creation _(already in docker-compose.yml)_.

### API Health Check

- [ ] Implement `GET /api/v1/health` endpoint in FastAPI that checks PostgreSQL, Redis, MinIO, and Ollama.

### Task Queue (ARQ — Decided, ADR-012)

- [ ] **ARQ is the task queue.** Celery is not used.
- [ ] Install ARQ in each worker service: `pip install arq`
- [ ] Each worker service (`cv_worker`, `analytics_worker`, `llm_service`) defines an ARQ `WorkerSettings` class
- [ ] Workers register job handlers as async functions: `async def process_video(ctx, job_id: str) -> None:`
- [ ] API enqueues jobs using `arq.connections.create_pool(RedisSettings.from_url(REDIS_URL))`
- [ ] Implement a `noop` job type that workers can process as a connectivity test: `async def noop(ctx) -> None: pass`
- [ ] ARQ worker healthcheck: `redis-cli -n 1 llen arq:queue:main | grep -v "^0"`

### Validation

- [ ] `docker compose -f infra/docker-compose.yml up --build` starts all services without error.
- [ ] `curl http://localhost:8000/api/v1/health` returns `200 OK` with all services healthy.
- [ ] `./scripts/check_health.sh` passes all 7 checks.
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

- [ ] `docker compose -f infra/docker-compose.yml up --build` succeeds with no exit errors.
- [ ] `GET /api/v1/health` returns HTTP 200 with all checks passing.
- [ ] All tasks above checked off.
- [ ] Phase status updated in `AGENTIC_EXECUTION_PLAN.md`.

---

## Completion Note

> _Agent: add completion date and summary here when done._

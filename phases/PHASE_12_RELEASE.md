# Phase 12 — Self-Hosted Release

> **Goal:** Package the complete platform for a reproducible self-hosted release. A new user should be able to clone the repo, run one command, and have the full platform running.

---

## Status: 🔲 Pending

---

## Prerequisites

- All previous phases complete (or MVP-complete subset: Phases 01–10).

---

## Agent Instructions

Read `ARCHITECTURE.md` for the service list and directory structure.

Your job is to produce a clean, documented, production-ready Docker Compose release. Focus on: ease of first-run, clear documentation, and reproducibility. Do not introduce new features in this phase.

---

## Tasks

### Docker Compose (Production Profile)

- [ ] Create `infra/docker-compose.prod.yml`:
  - Same services as dev, but with:
    - `restart: unless-stopped` for all services.
    - Resource limits (memory, CPU) per service.
    - Pinned image versions (no `latest` tags).
    - No hot-reload or dev-mode flags.
    - Production Dockerfile builds (multi-stage, non-root user).

- [ ] Create `infra/docker-compose.yml` (dev) vs `docker-compose.prod.yml` (prod) clearly separated.

### Production Dockerfiles

For each service, create a production Dockerfile:

- [ ] `apps/api/Dockerfile` — multi-stage build, non-root user, no dev dependencies.
- [ ] `apps/web/Dockerfile` — Next.js standalone build, minimal image.
- [ ] `services/cv_worker/Dockerfile` — includes YOLO model download step.
- [ ] `services/analytics_worker/Dockerfile`
- [ ] `services/llm_service/Dockerfile`

### Environment Setup

- [ ] `infra/.env.example` — complete, annotated, safe defaults.
- [ ] `scripts/setup.sh` — interactive setup script:
  - Copies `.env.example` to `.env`.
  - Prompts for essential values (MinIO credentials, Ollama model).
  - Pulls Ollama model if not present.
  - Creates MinIO buckets.
  - Runs initial DB migration.

### Model Downloads

- [ ] `scripts/download_models.sh`:
  - Downloads default YOLO model weight (`yolov8n.pt`) to `models/` directory.
  - Pulls default Ollama model (configurable, default: `llama3`).
  - Verifies checksums where available.

### Quickstart Documentation

- [ ] Update root `README.md` with a Quickstart section:
  ```
  ## Quickstart
  
  1. Clone the repo
  2. Run: ./scripts/setup.sh
  3. Run: docker compose -f infra/docker-compose.prod.yml up -d
  4. Open: http://localhost:3000
  ```
- [ ] Create `docs/QUICKSTART.md`:
  - Prerequisites (Docker, Docker Compose, disk space, RAM).
  - Step-by-step setup with expected output.
  - First-run walkthrough: upload a video, calibrate, process, view results.
  - Troubleshooting section (common errors and fixes).

### Sample Data

- [ ] Add synthetic sample video or mock data to `data/sample/`:
  - If real video not available: a script that generates a synthetic test case.
  - `data/sample/README.md` explaining what the sample data represents.

### Health and Monitoring

- [ ] `GET /health` endpoint returns version info alongside health checks.
- [ ] Add version label to all Docker images (build arg from git tag).
- [ ] `scripts/check_health.sh` — runs health check and reports all service statuses.

### Release Checklist (pre-release gate)

- [ ] All unit tests pass: `make test`.
- [ ] All linters pass: `make lint`.
- [ ] `docker compose -f infra/docker-compose.prod.yml up --build` succeeds.
- [ ] `./scripts/check_health.sh` reports all services healthy.
- [ ] `docs/QUICKSTART.md` reviewed and accurate.
- [ ] `INPUTS_NEEDED.md` status is `CONFIRMED`.
- [ ] All phase docs have completion notes.
- [ ] `AGENTIC_EXECUTION_PLAN.md` phase index fully updated.
- [ ] `docs/ADR.md` updated with any deferred decisions now resolved.
- [ ] Git tag created: `v0.1.0-mvp`.

### Security Review

Before release, verify:

- [ ] `.env` is in `.gitignore` (never committed).
- [ ] No hardcoded credentials in any source file.
- [ ] MinIO access keys are randomly generated in setup script.
- [ ] API does not expose raw MinIO credentials to frontend.
- [ ] Docker images run as non-root users.
- [ ] No debug endpoints (e.g., `/debug`, `/admin`) exposed in production build.

---

## Outputs

- `infra/docker-compose.prod.yml`
- Production Dockerfiles for all services.
- `scripts/setup.sh`
- `scripts/download_models.sh`
- `scripts/check_health.sh`
- `docs/QUICKSTART.md`
- `data/sample/` with synthetic test data.
- `v0.1.0-mvp` git tag.

---

## Definition of Done

- [ ] `./scripts/setup.sh && docker compose -f infra/docker-compose.prod.yml up -d` runs end-to-end on a clean machine.
- [ ] Quickstart guide is accurate and complete.
- [ ] All release checklist items above are checked.
- [ ] Phase status updated in `AGENTIC_EXECUTION_PLAN.md`.
- [ ] `v0.1.0-mvp` tag pushed.

---

## Completion Note

> _Agent: add completion date and summary here when done._

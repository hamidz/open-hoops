# Phase 01 — Repo Boilerplate

> **Goal:** Create the full monorepo directory structure, configuration files, and tooling setup. No business logic is written in this phase.

---

## Status: 🔲 Pending

---

## Prerequisites

- Phase 00 complete (`INPUTS_NEEDED.md` confirmed).

---

## Agent Instructions

Read `ARCHITECTURE.md` for the intended directory structure before starting.

Your job in this phase is to scaffold the monorepo structure and configure all developer tooling. Do not implement any business logic.

---

## Tasks

### Repository Structure

- [ ] Create `apps/web/` — Next.js app scaffold (`npx create-next-app`)
- [ ] Create `apps/api/` — FastAPI project structure
- [ ] Create `services/cv_worker/` — Python package structure
- [ ] Create `services/analytics_worker/` — Python package structure
- [ ] Create `services/llm_service/` — Python package structure
- [ ] Create `packages/shared_types/` — Shared Pydantic models (Python) and TypeScript types
- [ ] Create `infra/` — Docker Compose and environment config
- [ ] Create `data/sample/` — Placeholder for sample test data
- [ ] Create `scripts/` — Utility scripts directory

### Configuration Files (Root)

- [ ] `.gitignore` — covers Python, Node, Docker, `.env` files, model weights
- [ ] `.env.example` — root-level environment variable template
- [ ] `docker-compose.yml` — full local dev stack (see Phase 02)

### Python Services Configuration

For each Python service (`apps/api`, `services/cv_worker`, `services/analytics_worker`, `services/llm_service`):

- [ ] `pyproject.toml` with `ruff`, `mypy`, `pytest` configured
- [ ] `requirements.txt` or `requirements-dev.txt`
- [ ] `Dockerfile`
- [ ] `.env.example`
- [ ] `README.md` describing the service

### Frontend Configuration (`apps/web`)

- [ ] Next.js 14+ with TypeScript
- [ ] Tailwind CSS configured
- [ ] ESLint + Prettier configured
- [ ] `Dockerfile`
- [ ] `.env.example` with `NEXT_PUBLIC_API_URL`

### Shared Types (`packages/shared_types`)

- [ ] Pydantic models for: `Job`, `Detection`, `Track`, `AnalyticsSummary`
- [ ] Generated TypeScript type equivalents (see `docs/ADR.md` ADR-010; never hand-edit generated files)

### Developer Tooling

- [ ] `pre-commit` config (`.pre-commit-config.yaml`) with ruff and prettier hooks
- [ ] Root `Makefile` with common commands:
  - `make dev` — start Docker Compose stack
  - `make test` — run all tests
  - `make lint` — run all linters
  - `make build` — build all Docker images

### Documentation

- [ ] `apps/web/README.md`
- [ ] `apps/api/README.md`
- [ ] Each service `README.md` — purpose, how to run locally, environment variables

---

## Directory Structure Target

```
open-hoops/
├── apps/
│   ├── web/
│   │   ├── src/
│   │   │   ├── app/          # Next.js app router
│   │   │   ├── components/
│   │   │   └── lib/
│   │   ├── public/
│   │   ├── Dockerfile
│   │   ├── .env.example
│   │   └── package.json
│   └── api/
│       ├── app/
│       │   ├── main.py
│       │   ├── routers/
│       │   ├── models/
│       │   └── services/
│       ├── tests/
│       ├── Dockerfile
│       ├── .env.example
│       └── pyproject.toml
├── services/
│   ├── cv_worker/
│   ├── analytics_worker/
│   └── llm_service/
├── packages/
│   └── shared_types/
├── infra/
│   ├── docker-compose.yml
│   └── .env.example
├── data/
│   └── sample/
├── scripts/
├── docs/
├── phases/
├── .gitignore
├── .pre-commit-config.yaml
├── Makefile
└── README.md
```

---

## Outputs

- Complete scaffolded monorepo directory structure.
- All configuration files present and valid.
- `make dev`, `make lint`, `make test` all run without errors (even if test suites are empty stubs).

---

## Definition of Done

- [ ] All tasks above checked off.
- [ ] `make lint` passes on all services.
- [ ] `docker compose config` validates without errors.
- [ ] Phase status updated in `AGENTIC_EXECUTION_PLAN.md`.

---

## Completion Note

> _Agent: add completion date and summary here when done._

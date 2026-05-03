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
- [ ] Create `infra/` — Docker Compose and environment config _(templates already exist in repo)_
- [ ] Create `data/sample/` — Placeholder for sample test data _(README already exists)_
- [ ] Create `scripts/` — Utility scripts directory _(setup.sh and check_health.sh already exist)_

### Configuration Files (Root)

- [ ] `.gitignore` — covers Python, Node, Docker, `.env` files, model weights, `__pycache__`, `.next/`
- [x] `.env.example` — root-level environment variable template _(created)_
- [ ] `docker-compose.yml` link/alias → see `infra/docker-compose.yml` _(already created)_

### Monorepo Tooling (New — ADR-015)

- [ ] Add `turbo` as root devDependency: `npm install turbo --save-dev -w`
- [ ] Create root `package.json` with workspaces: `["apps/*", "packages/*"]`
- [ ] Create `turbo.json` with task pipeline:
  ```json
  {
    "$schema": "https://turbo.build/schema.json",
    "tasks": {
      "build": { "dependsOn": ["^build"], "outputs": [".next/**", "dist/**"] },
      "lint": { "outputs": [] },
      "test": { "outputs": ["coverage/**"] },
      "generate-types": { "outputs": ["packages/shared_types/types/**"] }
    }
  }
  ```

### Python Services Configuration

For each Python service (`apps/api`, `services/cv_worker`, `services/analytics_worker`, `services/llm_service`):

- [ ] `pyproject.toml` with `ruff`, `mypy`, `pytest`, `hypothesis` configured
- [ ] `requirements.txt` or `requirements-dev.txt`
- [ ] `Dockerfile`
- [ ] `README.md` describing the service

### Frontend Configuration (`apps/web`)

- [ ] Next.js 14+ with TypeScript (`--app --typescript --tailwind --eslint --src-dir`)
- [ ] Tailwind CSS configured with design system tokens from `docs/DESIGN_SYSTEM.md`
- [ ] shadcn/ui initialized: `npx shadcn-ui@latest init` — use `dark` base, `court-900` background
- [ ] Install base shadcn/ui components: `button card badge dialog sheet tabs select progress toast skeleton slider table tooltip scroll-area`
- [ ] Install TanStack Query: `npm install @tanstack/react-query`
- [ ] Install Zustand: `npm install zustand`
- [ ] Install Lucide React: `npm install lucide-react`
- [ ] Create `src/app/providers.tsx` with `QueryClientProvider` and React Query config
- [ ] Set `<html className="dark">` in root layout — dark mode is the default
- [ ] Install Inter Variable + JetBrains Mono fonts (Google Fonts, `next/font`)
- [ ] ESLint + Prettier configured
- [ ] `Dockerfile`

### Shared Types (`packages/shared_types`)

- [ ] Pydantic models for: `Job`, `Detection`, `Track`, `TelemetryDocument`, `AnalyticsSummary`, `AnnotationDocument`, `CoachingReport`
- [ ] `generate_types.py` script using `pydantic-to-typescript` or equivalent
- [ ] Generated TypeScript type equivalents (see `docs/ADR.md` ADR-010; never hand-edit generated files)

### Developer Tooling

- [ ] `pre-commit` config (`.pre-commit-config.yaml`) with ruff, prettier, and type-sync hooks
- [ ] `Makefile` targets all functional _(Makefile already created — verify all commands work)_

### CI/CD (New — Phase 01 scope)

- [x] `.github/workflows/ci.yml` created with: lint → test → type-sync check → compose validation jobs
- [ ] Verify CI passes on the Phase 01 scaffolding branch
- [ ] CI `continue-on-error: true` flags removed as each phase completes

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
- [ ] `make test` passes (stubs allowed with `continue-on-error`).
- [ ] `docker compose -f infra/docker-compose.yml config` validates without errors.
- [ ] `docker compose -f infra/docker-compose.yml -f infra/docker-compose.gpu.yml config` validates.
- [ ] `turbo run build` completes (may be empty output for scaffolding).
- [ ] CI pipeline passes on the `phase/01-repo-boilerplate` branch.
- [ ] Phase status updated in `AGENTIC_EXECUTION_PLAN.md`.

---

## Completion Note

> _Agent: add completion date and summary here when done._

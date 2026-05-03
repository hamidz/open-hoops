# Contributing to Open Hoops

> Open Hoops is an open-source, local-first basketball analytics platform.
> This guide explains how to set up the development environment, run tests, and contribute.

---

## Before You Start

1. Read [PROJECT_PLAN.md](./PROJECT_PLAN.md) — understand what we're building and why.
2. Read [ARCHITECTURE.md](./ARCHITECTURE.md) — understand how the system fits together.
3. Read [AGENTIC_EXECUTION_PLAN.md](./AGENTIC_EXECUTION_PLAN.md) — understand the phase-based workflow.
4. Check [INPUTS_NEEDED.md](./INPUTS_NEEDED.md) — understand confirmed constraints before touching CV or analytics code.

---

## Development Environment

### Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Docker | 24+ | Running the local dev stack |
| Docker Compose | v2+ | Service orchestration |
| Python | 3.11+ | Backend services |
| Node.js | 20+ | Next.js frontend |
| Git | 2.40+ | Version control |

**Optional (for GPU acceleration):**
- NVIDIA GPU with CUDA 11.8+
- `nvidia-container-toolkit` — [Install guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

### Quick Setup

```bash
# 1. Clone the repository
git clone https://github.com/hamidz/open-hoops.git
cd open-hoops

# 2. Run the interactive setup script (copies .env, pulls models, creates MinIO buckets)
./scripts/setup.sh

# 3. Start the full dev stack
docker compose -f infra/docker-compose.yml up -d

# 4. Verify all services are healthy
./scripts/check_health.sh
# Or: curl http://localhost:8000/health
```

### Running Without Docker (for active development)

If you're working on a specific service and want faster iteration:

```bash
# Python services — create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r apps/api/requirements-dev.txt

# Frontend
cd apps/web
npm install
npm run dev  # http://localhost:3000

# API
cd apps/api
uvicorn app.main:app --reload --port 8000

# CV Worker
cd services/cv_worker
python worker.py
```

> The full stack (PostgreSQL, Redis, MinIO, Ollama) still needs to run via Docker Compose even when developing individual services without Docker.

---

## Running Tests

```bash
# All tests (via Makefile)
make test

# Python tests only
pytest apps/api/tests/ -v
pytest services/cv_worker/tests/ -v
pytest services/analytics_worker/tests/ -v

# Frontend tests
cd apps/web && npm test

# With coverage
pytest apps/api/tests/ --cov=app --cov-report=term-missing
```

---

## Linting

```bash
# All linters (via Makefile)
make lint

# Python linting (ruff)
ruff check apps/api/ services/
ruff format --check apps/api/ services/

# Python type checking (mypy)
mypy apps/api/app/ services/cv_worker/ services/analytics_worker/

# TypeScript linting
cd apps/web && npm run lint
```

### Pre-commit Hooks

Install pre-commit hooks so linting runs automatically before every commit:

```bash
pip install pre-commit
pre-commit install
```

---

## Type Generation

TypeScript types are auto-generated from Pydantic models. After changing any Pydantic model in `packages/shared_types/models/`, run:

```bash
make generate-types
```

Never hand-edit files in `packages/shared_types/types/`. See `docs/ADR.md` ADR-010 for the rationale.

---

## Branch Naming

| Branch pattern | Purpose |
|---|---|
| `main` | Stable, reviewed, owner-confirmed work |
| `phase/XX-short-name` | Phase implementation (agent branch) |
| `fix/short-description` | Bug fixes between phases |
| `docs/short-description` | Documentation-only updates |
| `chore/short-description` | Config, tooling, and dependency updates |

---

## Pull Request Guidelines

1. **One phase per PR.** Don't bundle multiple phases into a single PR.
2. **All tests must pass** before opening a PR: `make test && make lint`.
3. **Update the phase doc** — tick off completed tasks in `phases/PHASE_XX_*.md`.
4. **Reference the phase** in your PR title: `Phase 05: CV Engine MVP`.
5. **Do not modify code from previous phases** unless the current phase requires it. If a change is needed, note it explicitly.

---

## Markdown as Source of Truth

If you encounter a conflict between Markdown documentation and existing code, the Markdown wins. Raise the discrepancy in your PR description before resolving it.

See [AGENTIC_EXECUTION_PLAN.md](./AGENTIC_EXECUTION_PLAN.md) for the full agent operating contract.

---

## Reporting Issues

Open a GitHub Issue for:

- Bugs in implemented phases.
- Gaps or ambiguities in phase documentation.
- Suggestions for post-MVP features.

Before opening an issue, check that Phase 00 is complete and all inputs in `INPUTS_NEEDED.md` are confirmed — many "bugs" in early phases are actually unconfirmed assumptions.

---

## Project Structure

```
open-hoops/
├── apps/
│   ├── web/                  # Next.js frontend
│   └── api/                  # FastAPI backend
├── services/
│   ├── cv_worker/            # OpenCV + YOLO CV pipeline
│   ├── analytics_worker/     # Metrics computation
│   └── llm_service/          # Ollama report generation
├── packages/
│   └── shared_types/         # Shared Pydantic + TypeScript types
├── infra/                    # Docker Compose + env config
├── docs/                     # Project documentation
├── phases/                   # Per-phase execution plans
├── data/sample/              # Synthetic test data
└── scripts/                  # Setup and utility scripts
```

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed service descriptions and data flows.

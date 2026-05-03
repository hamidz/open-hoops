# Technology Stack — Open Hoops

> Chosen technologies with rationale. Agents should default to these choices unless a phase doc specifies otherwise.

---

## Frontend — `apps/web`

### Next.js 14+

- **Why:** Full-stack React framework with excellent file-based routing, API routes, and streaming support.
- **Alternatives considered:** Vite + React (no SSR needed, viable), SvelteKit (smaller ecosystem for this use case).
- **Decision:** Next.js — best combination of ecosystem, developer experience, and future flexibility.

### TypeScript

- **Why:** Type safety across the frontend reduces integration bugs with the API layer. Shared types possible via `packages/shared_types`.

### Tailwind CSS

- **Why:** Utility-first CSS is fast to iterate, no style conflicts, works well with component libraries.
- **Custom config:** A `tailwind.config.ts` with design token extensions is required. See `docs/DESIGN_SYSTEM.md`.

### shadcn/ui

- **Why:** Unstyled, accessible component primitives built on Radix UI, fully customizable with Tailwind. Works natively with Next.js App Router. Generates component source into `src/components/ui/` — no black-box library dependency.
- **Alternatives considered:** Chakra UI (runtime CSS-in-JS, heavier), MUI (opinionated styles, fights Tailwind), headlessUI (less complete than Radix).
- **Decision:** shadcn/ui — best-in-class for Tailwind + Next.js + accessibility. Add components via `npx shadcn-ui@latest add <component>`.

### Lucide Icons

- **Why:** Consistent icon set used natively by shadcn/ui. Tree-shakeable, TypeScript-typed, MIT licensed.

### TanStack Query (React Query v5)

- **Why:** Server state management for all async data: job polling, telemetry, analytics, heatmaps. Handles polling intervals (`refetchInterval`), stale-while-revalidate, background refetch, and automatic retry — all required patterns for a job-status-heavy UI.
- **Replaces:** Ad-hoc `useEffect` + `useState` polling which is fragile and doesn't handle focus-refetch or stale data correctly.
- **Decision:** Required. Initialize in `src/app/providers.tsx` with `QueryClient`.

### Zustand

- **Why:** Lightweight client-side state management for UI-only state: calibration points in progress, active dashboard tab, selected player filter, heatmap opacity. Not needed for server state (TanStack Query handles that).
- **Alternatives considered:** Redux (overkill), Jotai (similar weight, less ergonomic), Context API (performance issues with frequent updates like calibration point dragging).
- **Decision:** Zustand for local UI state. TanStack Query for all server state.

### D3.js / Plotly.js (Court Visualizations)

- **Why:** Court heatmaps and telemetry overlays require custom SVG rendering. D3 gives full control over court geometry. Plotly.js is used for time-series charts.
- **Court SVG:** Custom-built SVG court template with NBA/FIBA dimensions as base layer. See `docs/DESIGN_SYSTEM.md` for visual spec.

### Axios

- **Why:** Simpler API client than native `fetch` for multipart file upload and progress tracking.

---

## Monorepo Tooling

### Turborepo

- **Why:** Parallel task execution across the monorepo (`apps/`, `packages/`), intelligent caching of build outputs, dependency-aware task graph. `make build` without Turborepo is a fragile shell script; with Turborepo it's a single `turbo run build`.
- **Decision:** `turbo.json` defines the task pipeline in Phase 01. Root `package.json` includes `turbo` as a dev dependency. Turborepo is responsible only for TypeScript/Node.js tasks — Python services are managed by `make`.

---

## Backend API — `apps/api`

### FastAPI

- **Why:** Python-native, async-first, automatic OpenAPI docs, Pydantic integration, fastest Python web framework.
- **Alternatives considered:** Django REST Framework (heavier), Flask (no async, minimal structure).
- **Decision:** FastAPI — best fit for a Python-heavy ML project.

### Python 3.11+

- **Why:** Performance improvements over 3.9/3.10, better error messages, standard for current ML libraries.

### Pydantic v2

- **Why:** Data validation and serialization. Used for request/response models and shared telemetry schemas.

### SQLAlchemy 2.x + Alembic

- **Why:** ORM for PostgreSQL. Alembic for schema migrations. Async driver (`asyncpg`) for non-blocking DB calls.

### Celery or ARQ (Decided: **ARQ** — Phase 02)

- **Why ARQ:** Async-native (built on asyncio), Redis-native job queue, lightweight, no broker/backend split, simpler worker lifecycle than Celery. The API is fully async (FastAPI + asyncpg) — ARQ integrates cleanly without a synchronous compatibility layer.
- **Decision:** ARQ is the task queue. Celery is not used. This is locked in ADR-012.
- **Worker pattern:** Each worker service (`cv_worker`, `analytics_worker`, `llm_service`) runs an ARQ `Worker` process with defined function-based job handlers.

---

## Computer Vision — `services/cv_worker`

### OpenCV

- **Why:** De facto standard for video frame extraction, image preprocessing, and homography transforms.

### Ultralytics YOLO (YOLOv8 / YOLOv11)

- **Why:** Best-in-class real-time object detection with excellent Python API. Pre-trained on COCO (includes `person` and `sports ball` classes).
- **Default model:** `yolov8m` (medium) with ROCm GPU; `yolov8n` (nano) if CPU-only. The confirmed AMD R9700 AI with 32 GB VRAM can run medium models in real-time.
- **Fine-tuning:** Not required for MVP. COCO person detection is sufficient.
- **GPU acceleration:** AMD ROCm via PyTorch ROCm build in WSL2 (see `ARCHITECTURE.md` Section 9).

### ByteTrack

- **Why:** State-of-the-art multi-object tracker, robust to occlusions, included in Ultralytics. Produces stable `track_id` per player.
- **Alternatives:** BoT-SORT (slightly more accurate, more complex). Default to ByteTrack unless Phase 05 testing shows otherwise.

### NumPy

- **Why:** Homography computation, bounding box math, telemetry array operations.

---

## Analytics — `services/analytics_worker`

### Pandas

- **Why:** Telemetry data is tabular (frame × track). Pandas is the standard tool for time-series aggregation, rolling windows, and group-by metrics.

### SciPy / scikit-learn (optional)

- **Why:** Gaussian KDE for heatmap density estimation. K-means for zone clustering if needed.

---

## Local LLM — `services/llm_service`

### Ollama

- **Why:** The simplest way to run local LLMs (Llama, Mistral, Qwen) with an OpenAI-compatible API. Runs on CPU or GPU, no cloud dependency.

### Llama 3 8B / Mistral 7B

- **Why:** Best balance of quality and performance on consumer hardware. Fits in 8–16 GB RAM (quantized).
- **Default:** `llama3` via Ollama. Switchable via environment variable.

### Jinja2

- **Why:** Prompt templating. Structured prompts for analytics summaries reduce hallucination risk.

---

## Infrastructure

### PostgreSQL 16

- **Why:** Robust, open-source relational DB. Excellent JSON support for telemetry metadata.

### Redis 7

- **Why:** Fast in-memory queue for job dispatch. Also used for caching job status.

### MinIO

- **Why:** S3-compatible local object storage. Stores video files, telemetry JSONs, heatmap PNGs. Identical API to AWS S3 for future cloud migration.

### Docker + Docker Compose

- **Why:** Reproducible local environment. Single `docker compose up` starts all services. No cloud required.

---

## Development Tooling

| Tool | Purpose |
|---|---|
| `ruff` | Python linting + formatting (replaces flake8 + black) |
| `mypy` | Python type checking |
| `pytest` | Python unit and integration tests |
| `hypothesis` | Property-based testing for analytics math (distance, speed, zone assignment, KDE) |
| `ESLint` + `Prettier` | TypeScript/JS linting and formatting |
| `Vitest` or `Jest` | Frontend unit tests |
| `Playwright` | Frontend E2E tests + visual regression (court SVG, heatmaps) from Phase 03 |
| `pre-commit` | Git hooks for lint/format on commit |
| `turborepo` | Monorepo task runner (parallel builds, caching) |

---

## Not In Stack (By Decision)

| Tool | Why Excluded |
|---|---|
| AWS / GCP / Azure | Local-first principle; no cloud vendor lock-in |
| Kafka | Overkill for single-node processing queue |
| Kubernetes | Out of scope for local self-hosted target |
| Pinecone / Weaviate | No vector search needed for MVP |
| LangChain | Unnecessary abstraction for simple prompt → Ollama flow |

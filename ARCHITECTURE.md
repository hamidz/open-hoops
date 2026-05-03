# Architecture — Open Hoops

> System architecture reference for the Open Hoops basketball analytics platform.
> Agents must read this file before implementing any phase.
>
> **Implementation note:** this document describes the target local-first architecture. The current first-workflow MVP still persists jobs and analytics to local JSON/filesystem storage in the API while PostgreSQL + MinIO remain the next storage phase, not the current runtime path.

---

## 1. High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Browser Client                        │
│              Next.js + Tailwind + D3/SVG/Plotly              │
└────────────────────────────┬─────────────────────────────────┘
                             │ HTTP / REST
┌────────────────────────────▼─────────────────────────────────┐
│                       API Gateway                            │
│                    FastAPI (Python)                          │
│         /api/jobs   /api/videos   /api/analytics             │
└──────┬──────────────────┬──────────────────┬─────────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────┐  ┌──────────────┐  ┌───────────────────┐
│  Job Queue  │  │  File Store  │  │  Analytics Store  │
│   (Redis)   │  │   (MinIO)    │  │  (PostgreSQL)     │
└──────┬──────┘  └──────────────┘  └───────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                     CV Worker Service                        │
│              Python + OpenCV + YOLO + Tracker                │
│   Frame extraction → Detection → Tracking → Telemetry       │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Analytics Worker Service                    │
│              Python — Telemetry → Metrics → Summaries        │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                   LLM Report Service                         │
│              Ollama (local) — Summary → Report               │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Service Responsibilities

### 2.1 Frontend (`apps/web`)

- Video upload UI
- Manual court calibration tool (point-click interface)
- Job status dashboard
- Heatmap and telemetry visualizations (court SVG overlay)
- Analytics summaries display
- LLM coaching report display

**Tech:** Next.js 14+, TypeScript, Tailwind CSS, D3 or Plotly.js, Axios

### 2.2 API Gateway (`apps/api`)

- Accepts video uploads
- Creates and manages job records
- Serves telemetry, analytics, and report data to frontend
- Delegates processing to worker queue

**Tech:** FastAPI, Python 3.11+, Pydantic, SQLAlchemy, Celery (or ARQ)

### 2.3 CV Worker (`services/cv_worker`)

- Pulls jobs from queue
- Extracts frames from video
- Runs player/ball detection (YOLO)
- Runs multi-object tracking (ByteTrack or BoT-SORT)
- Applies homography to map detections → court coordinates
- Exports telemetry JSON

**Tech:** Python, OpenCV, Ultralytics YOLO, ByteTrack, NumPy

### 2.4 Analytics Worker (`services/analytics_worker`)

- Reads telemetry output
- Computes per-player and per-team metrics
- Generates zone summaries, spacing metrics, movement density
- Produces analytics summary JSON

**Tech:** Python, Pandas, NumPy

### 2.5 LLM Report Service (`services/llm_service`)

- Reads analytics summary
- Constructs structured prompt
- Calls local Ollama API
- Returns coaching report text

**Tech:** Python, `ollama` Python client or HTTP, Jinja2 for prompt templates

### 2.6 Infrastructure

| Service | Role | Default |
|---|---|---|
| PostgreSQL | Job records, analytics data | `postgres:16` |
| Redis | Job queue, caching | `redis:7-alpine` |
| MinIO | Video and artifact file storage | `minio/minio` |
| Ollama | Local LLM inference | `ollama/ollama` |

### 2.7 CORS Configuration

The FastAPI API must configure CORS to allow requests from the Next.js dev server. This is required even in local operation.

```
Allowed origins (dev):  http://localhost:3000
Allowed origins (prod): configured via ALLOWED_ORIGINS env var
Allowed methods:        GET, POST, PUT, DELETE, OPTIONS
Allow credentials:      false (MVP is auth-free)
```

CORS is configured via `fastapi.middleware.cors.CORSMiddleware`. The `ALLOWED_ORIGINS` env var is a comma-separated list, defaulting to `http://localhost:3000` for development.

### 2.8 Docker Compose Resource Limits

To prevent any single service from exhausting system resources, all Docker Compose services must define memory limits. Recommended defaults for the confirmed 64 GB RAM dev machine:

| Service | Memory Limit | Notes |
|---|---|---|
| `postgres` | 1 GB | Typical for local dev |
| `redis` | 512 MB | Queue + cache |
| `minio` | 2 GB | File storage service |
| `ollama` | 24 GB | LLM inference (AMD ROCm) |
| `api` | 1 GB | FastAPI + Pydantic |
| `web` | 1 GB | Next.js dev server |
| `cv_worker` | 8 GB | YOLO + ByteTrack frames |
| `analytics_worker` | 2 GB | Pandas/NumPy |
| `llm_service` | 512 MB | Prompt construction only |

These are defined in `infra/docker-compose.yml` under each service's `deploy.resources.limits` key.

### 2.9 Redis Persistence

Redis is used for the job queue (ARQ). If Redis restarts without persistence, queued jobs are lost. Configure Redis with **RDB snapshot persistence**:

```
save 900 1       # Save if at least 1 key changed in 900 seconds
save 300 10      # Save if at least 10 keys changed in 300 seconds
save 60 10000    # Save if at least 10000 keys changed in 60 seconds
```

The `redis_data` named volume persists the RDB snapshot across container restarts.

---

## 3. Directory Structure (Intended)

```
open-hoops/
├── apps/
│   ├── web/                  # Next.js frontend
│   └── api/                  # FastAPI backend
├── services/
│   ├── cv_worker/            # OpenCV + YOLO worker
│   ├── analytics_worker/     # Metrics computation
│   └── llm_service/          # Ollama report generation
├── packages/
│   └── shared_types/         # Shared Pydantic/TypeScript types
├── infra/
│   ├── docker-compose.yml    # Local dev stack
│   └── docker-compose.prod.yml
├── docs/                     # Project documentation
├── phases/                   # Per-phase execution plans
├── data/
│   └── sample/               # Sample test data (non-sensitive)
├── scripts/                  # Utility scripts
├── README.md
├── PROJECT_PLAN.md
├── ARCHITECTURE.md
├── AGENTIC_EXECUTION_PLAN.md
└── INPUTS_NEEDED.md
```

---

## 4. Data Flow

### 4.1 Video Processing Flow

```
User uploads video
      ↓
API creates Job record (status: queued)
      ↓
Video stored in MinIO
      ↓
Job enqueued in Redis
      ↓
CV Worker picks up job
      ↓
Frames extracted → YOLO detection → Tracker → Homography
      ↓
Telemetry JSON saved to MinIO + PostgreSQL
      ↓
Analytics Worker picks up telemetry
      ↓
Metrics computed → Analytics summary saved
      ↓
LLM Service generates coaching report
      ↓
Job record updated (status: complete)
      ↓
Frontend polls job status → displays results
```

### 4.2 Court Calibration Flow

```
User opens calibration UI for a job
      ↓
Frontend displays first frame of video
      ↓
User clicks 4+ known court points
      ↓
API saves calibration points
      ↓
CV Worker computes homography matrix
      ↓
Homography stored with job record
      ↓
All subsequent detections mapped to court coordinates
```

---

## 5. Key Data Schemas

This section summarizes the most important shapes for architecture discussion. The canonical schema reference is [`docs/DATA_SCHEMAS.md`](./docs/DATA_SCHEMAS.md); implementation and tests must follow that file if examples differ.

### 5.1 Job Record

```json
{
  "job_id": "uuid",
  "status": "queued | processing | calibration_needed | complete | failed",
  "progress_pct": 0,
  "video_url": "minio://...",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "calibration": { ... },
  "telemetry_url": "minio://...",
  "analytics_summary_url": "minio://...",
  "report_url": "minio://...",
  "error_message": null
}
```

`progress_pct` is an integer 0–100 updated by the CV worker every 100 frames during processing. The frontend polls this alongside `status` to display a progress bar. `error_message` stores the failure reason when `status` is `failed`.

### 5.2 Detection (per frame)

```json
{
  "frame_index": 0,
  "timestamp_ms": 0,
  "detections": [
    {
      "track_id": 1,
      "object_class": "person | ball",
      "bbox_px": [x1, y1, x2, y2],
      "confidence": 0.92,
      "court_xy_m": [x_meters, y_meters],
      "team": null,
      "label": null
    }
  ]
}
```

### 5.3 Analytics Summary

```json
{
  "job_id": "uuid",
  "duration_seconds": 600,
  "players": [
    {
      "track_id": 1,
      "label": "Player A",
      "team": "home",
      "total_distance_m": 2340.5,
      "avg_speed_ms": 3.9,
      "court_coverage_pct": 42.1,
      "zone_distribution": { "paint": 0.3, "mid_range": 0.2, "three_point": 0.5 }
    }
  ],
  "team_spacing_avg_m": 4.8
}
```

---

## 6. Sensor Extensibility

While the MVP is video-only, the architecture is designed to be sensor-agnostic at the analytics layer:

- The **telemetry schema** (`frame`, `timestamp_ms`, `track_id`, `court_xy`) is the shared interface.
- Any sensor that can produce court-coordinate tracks (GPS, UWB, RFID) can feed the analytics and LLM layers directly.
- The CV Worker is one implementation of a telemetry producer. Others can be added later without changing the analytics layer.

---

## 7. Security Principles

- No cloud services are required. All data stays local.
- MinIO credentials are local-only (defined in `.env`, never committed).
- The API should not expose raw video URLs publicly — all access via signed URLs or proxy.
- Ollama runs fully locally — no data sent to external LLM providers.
- `.env` files are gitignored. A `.env.example` is provided for each service.
- See [`docs/SECURITY_PRIVACY.md`](./docs/SECURITY_PRIVACY.md) for the full threat model, privacy checklist, and data-handling requirements.

---

## 8. Open Architecture Decisions

These decisions are intentionally deferred to the relevant phase:

| Decision | Phase |
|---|---|
| Celery vs ARQ for task queue | Phase 02 |
| ByteTrack vs BoT-SORT default | Phase 05 |
| YOLOv8n vs YOLOv8m default weight | Phase 05 |
| PostgreSQL schema migrations tool (Alembic vs raw) | Phase 01 |

Decisions already accepted in `docs/ADR.md` include local-first operation, manual court calibration for MVP, generated TypeScript types from Pydantic models, and single-POST uploads for MVP.

---

## 9. GPU Support Notes

The CV worker supports optional GPU acceleration. Hardware is detected at runtime:

- **AMD ROCm (confirmed primary):** PyTorch ROCm build required. Only available on Linux (WSL2 on Windows). The `docker-compose.gpu.yml` override targets ROCm — see below.
- **NVIDIA CUDA:** Ultralytics YOLO will use CUDA automatically if `torch` detects a GPU and `nvidia-container-toolkit` is installed on the Docker host.
- **Apple MPS:** Detected automatically on macOS (development only — not supported in Docker).
- **CPU fallback:** Always available and required. Target: ≥ 5 frames/sec on CPU.

### AMD ROCm Configuration (Confirmed Hardware Path)

The confirmed development GPU is an **AMD Radeon RX 9700 AI (RDNA3 architecture, 32 GB VRAM)**. AMD GPUs require ROCm, which is Linux-only. On Windows, this requires **WSL2**.

To enable ROCm GPU pass-through in Docker Compose, use the `docker-compose.gpu.yml` override:

```yaml
cv_worker:
  image: rocm/pytorch:latest  # ROCm-enabled PyTorch base
  devices:
    - /dev/kfd
    - /dev/dri
  group_add:
    - video
    - render
  environment:
    - HSA_OVERRIDE_GFX_VERSION=11.0.0  # RDNA3 gfx1100 override if needed
```

**Requirements:**
- WSL2 with Ubuntu 22.04+ running inside Windows
- AMD GPU driver (AMDGPU) loaded in the WSL2 kernel
- ROCm 5.7+ installed in WSL2 host

```bash
# In WSL2: verify ROCm sees the GPU
rocm-smi --showproductname
```

See `docs/QUICKSTART.md` for the full WSL2 + ROCm setup walkthrough.

### Docker GPU Configuration (NVIDIA — Alternative)

For NVIDIA GPU users (not the confirmed hardware):

```yaml
cv_worker:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

This requires `nvidia-container-toolkit` installed on the Docker host.

GPU is **optional** for MVP. The `docker-compose.yml` defaults to CPU-only. The `docker-compose.gpu.yml` override provides the ROCm path for AMD hardware.

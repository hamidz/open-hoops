# Architecture — Open Hoops

> System architecture reference for the Open Hoops basketball analytics platform.
> Agents must read this file before implementing any phase.

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
| Redis | Job queue, caching | `redis:7` |
| MinIO | Video and artifact file storage | `minio/minio` |
| Ollama | Local LLM inference | `ollama/ollama` |

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

### 5.1 Job Record

```json
{
  "job_id": "uuid",
  "status": "queued | processing | calibration_needed | complete | failed",
  "video_url": "minio://...",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "calibration": { ... },
  "telemetry_url": "minio://...",
  "analytics_summary_url": "minio://...",
  "report_url": "minio://..."
}
```

### 5.2 Detection (per frame)

```json
{
  "frame": 0,
  "timestamp_ms": 0,
  "detections": [
    {
      "track_id": 1,
      "class": "person | ball",
      "bbox_px": [x1, y1, x2, y2],
      "confidence": 0.92,
      "court_xy": [x_meters, y_meters]
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

---

## 8. Open Architecture Decisions

These decisions are intentionally deferred to the relevant phase:

| Decision | Phase |
|---|---|
| Celery vs ARQ for task queue | Phase 02 |
| ByteTrack vs BoT-SORT default | Phase 05 |
| YOLOv8n vs YOLOv8m default weight | Phase 05 |
| Court line auto-detection vs always manual | Phase 06 |
| PostgreSQL schema migrations tool (Alembic vs raw) | Phase 01 |

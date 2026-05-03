# API Contract — Open Hoops

> Planning-stage REST API contract for the MVP. Implementation must keep this document and generated OpenAPI output aligned.

---

## 1. Conventions

- Base path: `/api/v1` (versioned from day one — see ADR-013).
- Payloads are JSON unless an endpoint explicitly uses multipart upload or returns an image/download URL.
- IDs are UUID strings.
- Timestamps are ISO 8601 UTC strings.
- Stored document schemas are defined in `docs/DATA_SCHEMAS.md`.
- API implementations should expose OpenAPI docs through FastAPI and keep this contract synchronized.

---

## 2. Status Codes

| Code | Meaning |
|---|---|
| 200 | Successful read or mutation with response body |
| 201 | Resource created |
| 202 | Async work accepted / queued |
| 204 | Successful deletion with no response body |
| 400 | Invalid request or validation failure |
| 404 | Resource not found |
| 409 | Invalid state transition |
| 413 | Upload exceeds maximum configured size |
| 415 | Unsupported media type |
| 500 | Unexpected server error |
| 503 | Dependency unavailable |

---

## 3. Error Response Shape

```json
{
  "error": "short_machine_readable_code",
  "detail": "Human-readable explanation",
  "request_id": "optional-correlation-id"
}
```

Frontend code must display `detail` or a friendlier mapped message, never raw stack traces.

---

## 4. Health

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/health` | Service health, dependency status, and version info |

Response:

```json
{
  "status": "ok",
  "version": "0.1.0-mvp",
  "dependencies": {
    "postgres": "ok",
    "redis": "ok",
    "minio": "ok",
    "ollama": "ok"
  }
}
```

---

## 5. Jobs and Uploads

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/jobs/upload` | Upload video, create job, enqueue processing |
| GET | `/api/v1/jobs` | List jobs, newest first, paginated |
| GET | `/api/v1/jobs/{job_id}` | Get full job record |
| POST | `/api/v1/jobs/{job_id}/retry` | Requeue a failed job |
| DELETE | `/api/v1/jobs/{job_id}` | Delete job and related artifacts |

### `POST /api/v1/jobs/upload`

Multipart form fields:

| Field | Required | Notes |
|---|---|---|
| `video` | Yes | `.mp4` or `.mov` |
| `label` | No | User display label |
| `sport` | No | Defaults to `basketball` |

Success response (`201`):

```json
{
  "job_id": "uuid",
  "status": "queued",
  "created_at": "ISO8601"
}
```

State notes:

- First-workflow MVP behavior: until the CV worker is fully implemented, accepted uploads are stored locally and completed with deterministic generated analytics so users can validate the end-to-end UI.
- Upload validation failure returns `400`, `413`, or `415`.
- MinIO upload failure returns no job record.
- Redis enqueue failure creates the job as `failed` with `error_message` populated.

---

## 6. Calibration

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/jobs/{job_id}/calibration/frame` | Return signed/proxied URL for frame-zero JPEG |
| GET | `/api/v1/jobs/{job_id}/calibration` | Return saved calibration state |
| POST | `/api/v1/jobs/{job_id}/calibration` | Save points, compute homography, update job |
| DELETE | `/api/v1/jobs/{job_id}/calibration` | Reset calibration |

`POST /api/jobs/{job_id}/calibration` request:

```json
{
  "points": [
    { "pixel": [452, 312], "court": [0, 0] },
    { "pixel": [1201, 308], "court": [0, 15.24] },
    { "pixel": [1198, 721], "court": [28.65, 15.24] },
    { "pixel": [449, 725], "court": [28.65, 0] }
  ]
}
```

Success response:

```json
{
  "job_id": "uuid",
  "calibration": {
    "schema_version": "1.0",
    "points": [],
    "homography_matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
    "reprojection_error_px": 6.2,
    "court_dimensions_m": [28.65, 15.24],
    "calibrated_at": "ISO8601"
  },
  "status": "queued"
}
```

---

## 7. Telemetry and Debug Artifacts

### Telemetry Size Strategy

> ⚠️ **Telemetry files can be very large.** A 2-hour game at 30fps sampled every 3rd frame produces ~150 MB of JSON. Direct endpoint response is not feasible for large jobs.

**All telemetry endpoints default to returning a signed download URL, not inline JSON.** The client downloads the file directly from MinIO using the signed URL. This is not optional — it is the default behavior.

Signed URL expiry for telemetry downloads: **24 hours** (configurable via `SIGNED_URL_EXPIRY_TELEMETRY_HOURS`).

For frame-level queries (single frame detections), inline JSON is acceptable.

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/jobs/{job_id}/telemetry` | Return signed download URL for full telemetry JSON |
| GET | `/api/v1/jobs/{job_id}/telemetry/metadata` | Return video metadata only (inline JSON) |
| GET | `/api/v1/jobs/{job_id}/telemetry/frame/{frame_index}` | Return detections for one sampled frame (inline JSON) |
| GET | `/api/v1/jobs/{job_id}/debug/frames` | List available debug frame URLs |
| GET | `/api/v1/jobs/{job_id}/debug/frames/{frame_index}` | Return signed debug frame image URL |

All telemetry responses return:

```json
{
  "download_url": "http://localhost:9000/telemetry/{job_id}/telemetry.json?...",
  "expires_at": "ISO8601",
  "file_size_bytes": 157286400
}
```

---

## 8. Analytics

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/jobs/{job_id}/analytics` | Return full analytics summary (inline JSON — ~50 KB max) |
| GET | `/api/v1/jobs/{job_id}/analytics/players/{track_id}` | Return one player's metrics |
| GET | `/api/v1/jobs/{job_id}/analytics/teams` | Return team metrics |
| POST | `/api/v1/jobs/{job_id}/analytics/recompute` | Queue analytics recomputation |

`POST /analytics/recompute` returns `202` when accepted.

---

## 9. Heatmaps

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/jobs/{job_id}/heatmaps` | List player/team heatmaps |
| GET | `/api/v1/jobs/{job_id}/heatmaps/{track_id}` | Return player heatmap grid JSON |
| GET | `/api/v1/jobs/{job_id}/heatmaps/{track_id}/image` | Return player heatmap PNG URL (signed, 5 min expiry) |
| GET | `/api/v1/jobs/{job_id}/heatmaps/team/{team}` | Return team heatmap grid JSON |

Optional query parameters:

| Parameter | Notes |
|---|---|
| `start_frame` | Inclusive sampled frame index |
| `end_frame` | Inclusive sampled frame index |
| `grid_size` | Optional grid resolution; implementation may cap maximum |

---

## 10. Annotations

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/jobs/{job_id}/annotations` | Return all annotations |
| PUT | `/api/v1/jobs/{job_id}/annotations/players/{track_id}` | Upsert player label/team/flag |
| POST | `/api/v1/jobs/{job_id}/annotations/shots` | Add shot annotation |
| DELETE | `/api/v1/jobs/{job_id}/annotations/shots/{shot_id}` | Delete shot annotation |
| PUT | `/api/v1/jobs/{job_id}/annotations/team-colors` | Update team colors |
| POST | `/api/v1/jobs/{job_id}/annotations/recompute` | Queue analytics recomputation using annotations |

Player upsert request:

```json
{
  "label": "Jordan #23",
  "team": "home",
  "flagged": false,
  "flag_reason": null
}
```

Shot annotation creation returns the created shot with a generated `shot_id`.

---

## 11. Reports

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/jobs/{job_id}/report/generate` | Queue local LLM report generation |
| GET | `/api/v1/jobs/{job_id}/report` | Return generated report |
| DELETE | `/api/v1/jobs/{job_id}/report` | Delete report so it can be regenerated |

`POST /report/generate` returns:

```json
{
  "status": "queued"
}
```

---

## 12. State Transitions

```text
uploaded → queued → calibration_needed → queued → processing → complete
                       │                     │             │
                       └──────── failed ◄────┴─────────────┘
```

Rules:

- A newly uploaded job starts as `queued` only if it can be enqueued.
- If CV requires calibration and none exists, status becomes `calibration_needed`.
- Saving calibration from `calibration_needed` returns the job to `queued`.
- `retry` is valid only from `failed`.
- `delete` is blocked while `processing` unless a future cancellation feature is implemented.

---

## 13. Signed URL Expiry Policy

| Artifact Type | Expiry | Rationale |
|---|---|---|
| Frame-zero JPEG (calibration) | 30 minutes | User is actively on calibration page |
| Debug frame images | 30 minutes | Short interactive session |
| Heatmap PNG | 1 hour | Download/view session |
| Telemetry JSON download | 24 hours | Large file, may take time to download |
| Analytics summary | 1 hour | Dashboard viewing session |
| Coaching report | 1 hour | Reading session |

Signed URL expiry durations are configurable via environment variables (e.g., `SIGNED_URL_EXPIRY_FRAME_MINUTES=30`). Never log signed URLs.

---

## 14. CORS Policy

The FastAPI app must configure CORS for local development. Configured via `CORSMiddleware`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # default: ["http://localhost:3000"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=False,  # no auth cookies in MVP
)
```

`ALLOWED_ORIGINS` is an env var. Default: `http://localhost:3000`. Must not be `*` even in development.

---

## 15. Future Auth Note

MVP is local-first and single-user. If cloud or multi-user support is added later, this contract must be revised before implementation to include authentication, authorization, ownership checks, and audit logging. API versioning (`/api/v1/`) ensures a clean break to `/api/v2/` for this change.

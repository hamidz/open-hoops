# API Contract — Open Hoops

> Planning-stage REST API contract for the MVP. Implementation must keep this document and generated OpenAPI output aligned.

---

## 1. Conventions

- Base path: `/api`.
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
| GET | `/health` | Service health, dependency status, and version info |

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
| POST | `/api/jobs/upload` | Upload video, create job, enqueue processing |
| GET | `/api/jobs` | List jobs, newest first, paginated |
| GET | `/api/jobs/{job_id}` | Get full job record |
| POST | `/api/jobs/{job_id}/retry` | Requeue a failed job |
| DELETE | `/api/jobs/{job_id}` | Delete job and related artifacts |

### `POST /api/jobs/upload`

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

- Upload validation failure returns `400`, `413`, or `415`.
- MinIO upload failure returns no job record.
- Redis enqueue failure creates the job as `failed` with `error_message` populated.

---

## 6. Calibration

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/jobs/{job_id}/calibration/frame` | Return signed/proxied URL for frame-zero JPEG |
| GET | `/api/jobs/{job_id}/calibration` | Return saved calibration state |
| POST | `/api/jobs/{job_id}/calibration` | Save points, compute homography, update job |
| DELETE | `/api/jobs/{job_id}/calibration` | Reset calibration |

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

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/jobs/{job_id}/telemetry` | Return telemetry JSON or signed download URL |
| GET | `/api/jobs/{job_id}/telemetry/metadata` | Return video metadata only |
| GET | `/api/jobs/{job_id}/telemetry/frame/{frame_index}` | Return detections for one sampled frame |
| GET | `/api/jobs/{job_id}/debug/frames` | List available debug frame URLs |
| GET | `/api/jobs/{job_id}/debug/frames/{frame_index}` | Return signed/proxied debug frame image URL |

Large telemetry responses may return:

```json
{
  "download_url": "signed-or-proxied-url",
  "expires_at": "ISO8601"
}
```

---

## 8. Analytics

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/jobs/{job_id}/analytics` | Return full analytics summary |
| GET | `/api/jobs/{job_id}/analytics/players/{track_id}` | Return one player's metrics |
| GET | `/api/jobs/{job_id}/analytics/teams` | Return team metrics |
| POST | `/api/jobs/{job_id}/analytics/recompute` | Queue analytics recomputation |

`POST /analytics/recompute` returns `202` when accepted.

---

## 9. Heatmaps

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/jobs/{job_id}/heatmaps` | List player/team heatmaps |
| GET | `/api/jobs/{job_id}/heatmaps/{track_id}` | Return player heatmap grid JSON |
| GET | `/api/jobs/{job_id}/heatmaps/{track_id}/image` | Return player heatmap PNG URL |
| GET | `/api/jobs/{job_id}/heatmaps/team/{team}` | Return team heatmap grid JSON |

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
| GET | `/api/jobs/{job_id}/annotations` | Return all annotations |
| PUT | `/api/jobs/{job_id}/annotations/players/{track_id}` | Upsert player label/team/flag |
| POST | `/api/jobs/{job_id}/annotations/shots` | Add shot annotation |
| DELETE | `/api/jobs/{job_id}/annotations/shots/{shot_id}` | Delete shot annotation |
| PUT | `/api/jobs/{job_id}/annotations/team-colors` | Update team colors |
| POST | `/api/jobs/{job_id}/annotations/recompute` | Queue analytics recomputation using annotations |

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
| POST | `/api/jobs/{job_id}/report/generate` | Queue local LLM report generation |
| GET | `/api/jobs/{job_id}/report` | Return generated report |
| DELETE | `/api/jobs/{job_id}/report` | Delete report so it can be regenerated |

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

## 13. Future Auth Note

MVP is local-first and single-user. If cloud or multi-user support is added later, this contract must be revised before implementation to include authentication, authorization, ownership checks, and audit logging.

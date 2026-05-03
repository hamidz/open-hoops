# Phase 07 — Telemetry Export

> **Goal:** Finalize the telemetry output schema, ensure the telemetry JSON from the CV worker is valid and complete, and expose it via the API for download and dashboard consumption.

---

## Status: 🔲 Pending

---

## Prerequisites

- Phase 05 complete (CV worker producing telemetry).
- Phase 06 complete (calibration applied to telemetry).

---

## Agent Instructions

Read `ARCHITECTURE.md` for the full telemetry and detection schemas before starting.

Your job is to solidify the telemetry data contract. After this phase, the telemetry schema must be treated as stable — downstream analytics (Phase 09) and visualizations (Phase 08) depend on it.

---

## Telemetry Schema (Finalized)

### `telemetry.json`

```json
{
  "schema_version": "1.0",
  "job_id": "uuid",
  "sport": "basketball",
  "video_metadata": {
    "original_filename": "game_2025_01_15.mp4",
    "fps": 30,
    "total_frames": 54000,
    "duration_seconds": 1800,
    "resolution_px": [1920, 1080],
    "sampled_every_n_frames": 3
  },
  "calibration": {
    "applied": true,
    "court_dimensions_m": [28.65, 15.24],
    "reprojection_error_px": 6.2
  },
  "frames": [
    {
      "frame_index": 0,
      "timestamp_ms": 0,
      "detections": [
        {
          "track_id": 1,
          "object_class": "person",
          "bbox_px": [100, 200, 150, 350],
          "confidence": 0.91,
          "court_xy_m": [4.2, 7.8],
          "team": null,
          "label": null
        }
      ]
    }
  ]
}
```

### `video_metadata.json` (fast-access subset)

```json
{
  "job_id": "uuid",
  "fps": 30,
  "total_frames": 54000,
  "duration_seconds": 1800,
  "resolution_px": [1920, 1080],
  "sampled_every_n_frames": 3,
  "total_sampled_frames": 18000
}
```

### `debug_artifacts/frame_{N}.jpg`

- Sampled debug frames with bounding boxes and track IDs overlaid.
- Write every 300th sampled frame (configurable).
- Store in MinIO `artifacts/{job_id}/debug/`.

---

## Tasks

### Schema Validation

- [ ] Define Pydantic models in `packages/shared_types/models/telemetry.py`:
  - `Detection`
  - `TelemetryFrame`
  - `VideoMetadata`
  - `CalibrationMeta`
  - `TelemetryDocument`
- [ ] CV worker must validate output against these models before writing to MinIO.
- [ ] Add `schema_version` field (start at `"1.0"`).

### API Endpoints

- [ ] `GET /api/jobs/{job_id}/telemetry` — stream or return telemetry JSON:
  - For small videos (< 50 MB JSON): return directly.
  - For large videos: return a pre-signed MinIO download URL.
- [ ] `GET /api/jobs/{job_id}/telemetry/metadata` — return `video_metadata.json` only (fast, lightweight).
- [ ] `GET /api/jobs/{job_id}/telemetry/frame/{frame_index}` — return detections for a single frame (for dashboard scrubber).

### Debug Artifacts

- [ ] CV worker writes debug JPEG frames with overlaid bounding boxes every N frames.
- [ ] `GET /api/jobs/{job_id}/debug/frames` — list available debug frame URLs.
- [ ] `GET /api/jobs/{job_id}/debug/frames/{frame_index}` — return a specific debug frame image URL.

### TypeScript Types

- [ ] Generate or manually write TypeScript equivalents of the Pydantic models in `packages/shared_types/types/telemetry.ts`.

### Tests

- [ ] Unit test: Pydantic schema validation for valid and invalid telemetry documents.
- [ ] Unit test: API endpoint returns correct telemetry for a known job.
- [ ] Integration test: full CV pipeline → telemetry API response round-trip.

---

## Outputs

- `packages/shared_types/models/telemetry.py` — Pydantic telemetry models.
- `packages/shared_types/types/telemetry.ts` — TypeScript equivalents.
- `apps/api/app/routers/telemetry.py` — telemetry API endpoints.
- Debug artifacts in MinIO for a test job.

---

## Definition of Done

- [ ] Telemetry schema finalized and documented in this file.
- [ ] Pydantic models defined and passing validation tests.
- [ ] TypeScript types match Pydantic models.
- [ ] All telemetry API endpoints working and tested.
- [ ] Phase status updated in `AGENTIC_EXECUTION_PLAN.md`.

---

## Completion Note

> _Agent: add completion date and summary here when done._

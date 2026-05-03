# Data Schemas — Open Hoops

> Canonical reference for all data schemas used across the platform.
> This document is the single source of truth. Phase docs and service code must conform to these schemas.
> All schemas carry a `schema_version` field. See the versioning policy at the bottom.

## MVP Storage Mode (Current)

The current runnable MVP persists data with **local JSON documents plus local filesystem artifacts** under `OPEN_HOOPS_DATA_DIR`.

- **Implemented now:** `job.json` records in `jobs/` and `analytics_summary.json` records in `artifacts/{job_id}/`
- **Planned document types:** `telemetry.json`, `annotations.json`, and `coaching_report.json`
- **Next storage step:** move job metadata/state to local PostgreSQL and large artifacts to MinIO once real worker pipelines, richer querying, and annotation/recompute flows land

PostgreSQL and MinIO remain the intended target architecture, but they are not yet the active persistence path in the API runtime.

---

## 1. Job Record

Stored as `jobs/{job_id}.json` in the current MVP. Planned to move to the `jobs` PostgreSQL table in a later phase. Returned by `GET /api/jobs/{job_id}`.

```json
{
  "schema_version": "1.0",
  "job_id": "uuid",
  "status": "queued | processing | calibration_needed | complete | failed",
  "progress_pct": 0,
  "label": "Optional user label",
  "sport": "basketball",
  "original_filename": "game_2025_01_15.mp4",
  "file_size_bytes": 2147483648,
  "video_url": "minio://videos/{job_id}/video.mp4",
  "frame_zero_url": "minio://artifacts/{job_id}/frame_0.jpg",
  "calibration_json": null,
  "telemetry_url": "minio://telemetry/{job_id}/telemetry.json",
  "analytics_summary_url": "minio://artifacts/{job_id}/analytics_summary.json",
  "report_url": "minio://artifacts/{job_id}/coaching_report.json",
  "error_message": null,
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

**Field notes:**
- `schema_version`: increment when the stored job document shape changes.
- `progress_pct`: 0–100 integer. Updated by the CV worker every 100 frames during `processing`.
- `calibration_json`: serialized homography matrix + calibration points. `null` until Phase 06 calibration is complete.
- `error_message`: populated only when `status` is `failed`. Human-readable failure reason.
- `frame_zero_url`: set at upload time (Phase 04), before CV processing begins.
- Current MVP implementations may return `file://` URLs for local artifacts instead of `minio://` URLs.

---

## 2. Calibration Record (embedded in Job)

Stored in the `calibration_json` field of the Job record.

```json
{
  "schema_version": "1.0",
  "points": [
    { "pixel": [452, 312], "court": [0, 0] },
    { "pixel": [1201, 308], "court": [0, 15.24] },
    { "pixel": [1198, 721], "court": [28.65, 15.24] },
    { "pixel": [449, 725], "court": [28.65, 0] }
  ],
  "homography_matrix": [[...], [...], [...]],
  "reprojection_error_px": 6.2,
  "court_dimensions_m": [28.65, 15.24],
  "calibrated_at": "ISO8601"
}
```

---

## 3. Telemetry Document (`telemetry.json`)

Planned document. Stored in MinIO at `telemetry/{job_id}/telemetry.json` once the CV pipeline writes real telemetry output.

Defined by: `packages/shared_types/models/telemetry.py` (Pydantic) and `packages/shared_types/types/telemetry.ts` (TypeScript, auto-generated).

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
    "sampled_every_n_frames": 3,
    "total_sampled_frames": 18000
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
          "object_class": "person | ball",
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

**Field notes:**
- `court_xy_m`: `[x_meters, y_meters]` from the near-left corner origin. `null` if calibration was not applied.
- `team` and `label`: always `null` in raw telemetry. Populated at the analytics layer by reading annotations (Phase 11).
- `calibration.applied`: `false` if the CV worker ran without a valid homography matrix.

---

## 4. Analytics Summary (`analytics_summary.json`)

Stored as `artifacts/{job_id}/analytics_summary.json` in the current MVP and planned to move to MinIO-backed artifact storage in a later phase.

Defined by: `packages/shared_types/models/analytics.py`.

```json
{
  "schema_version": "1.0",
  "job_id": "uuid",
  "computed_at": "ISO8601",
  "annotations_applied": false,
  "duration_seconds": 600,
  "total_sampled_frames": 6000,
  "avg_detections_per_frame": 9.2,
  "ball_tracking_coverage_pct": 68.5,
  "players": [
    {
      "track_id": 1,
      "label": null,
      "team": "home",
      "total_distance_m": 2340.5,
      "avg_speed_ms": 3.9,
      "max_speed_ms": 8.2,
      "court_coverage_pct": 42.1,
      "frames_tracked": 5800,
      "tracking_coverage_pct": 96.7,
      "zone_distribution": {
        "left_paint": 0.28,
        "left_mid_range": 0.12,
        "left_three": 0.18,
        "left_corner_three": 0.02,
        "right_paint": 0.05,
        "right_mid_range": 0.15,
        "right_three": 0.18,
        "right_corner_three": 0.02,
        "center": 0.00
      }
    }
  ],
  "teams": {
    "home": {
      "avg_spacing_m": 4.8,
      "min_spacing_m": 1.2,
      "court_coverage_pct": 78.3
    },
    "away": {
      "avg_spacing_m": 4.2,
      "min_spacing_m": 0.9,
      "court_coverage_pct": 74.1
    }
  }
}
```

**Field notes:**
- `annotations_applied`: `true` if this summary was computed after Phase 11 annotations were saved.
- `team` in player record: `null` until the user assigns teams via the annotation panel (Phase 11). **Do not infer teams from track_id.** ByteTrack assigns track_ids incrementally as objects first appear and they will not reliably alternate between teams. Team assignment requires either jersey color clustering (Phase 05) or manual annotation (Phase 11). Defaulting to track_id parity would produce incorrect and misleading analytics.
- Zone distribution values sum to 1.0 per player.

---

## 5. Annotation Document (`annotations.json`)

Planned document. Stored in MinIO at `artifacts/{job_id}/annotations.json` and mirrored to PostgreSQL `annotations` table once Phase 11 lands.

Defined by: `packages/shared_types/models/annotation.py`.

```json
{
  "schema_version": "1.0",
  "job_id": "uuid",
  "updated_at": "ISO8601",
  "team_colors": {
    "home_color": "#1d4ed8",
    "away_color": "#dc2626"
  },
  "player_annotations": [
    {
      "track_id": 3,
      "label": "Jordan #23",
      "team": "home",
      "flagged": false,
      "flag_reason": null
    }
  ],
  "shot_annotations": [
    {
      "shot_id": "uuid",
      "frame_index": 4500,
      "track_id": 3,
      "court_xy_m": [25.1, 7.2],
      "made": true,
      "shot_type": "3pt"
    }
  ]
}
```

**Field notes:**
- `flagged: true` causes the analytics worker to exclude that `track_id` from all metrics.
- `shot_annotations` are used by the analytics worker to produce per-player shot stats in Phase 11+.

---

## 6. Coaching Report (`coaching_report.json`)

Planned document. Stored in MinIO at `artifacts/{job_id}/coaching_report.json` once Phase 10 lands.

```json
{
  "schema_version": "1.0",
  "job_id": "uuid",
  "model": "llama3",
  "generated_at": "ISO8601",
  "report_text": "...",
  "analytics_summary_version": "1.0",
  "prompt_template_version": "1.0",
  "annotations_applied": false
}
```

---

## 7. Court Zone Definitions (NBA Full Court)

Origin: near-left corner `[0, 0]`. Court dimensions: `28.65 m × 15.24 m`.

```
Zone Name           | x range (m)       | y range (m)       | Notes
--------------------|-------------------|-------------------|---------------------------
left_paint          | 0 – 5.79          | 1.83 – 13.41      | Lane / key, near basket
left_mid_range      | 5.79 – ~7.24 arc  | (inside 3pt arc)  | Between paint and 3pt line
left_three          | beyond 3pt arc    | (outside arc)     | Excludes corner three
left_corner_three   | 0 – 0.90          | 0 – 0.90 or       | NBA corner, y < 0.9 or y > 14.34
                    |                   | 14.34 – 15.24     |
right_paint         | 22.86 – 28.65     | 1.83 – 13.41      | Mirror of left_paint
right_mid_range     | ~21.41 arc – 22.86| (inside 3pt arc)  | Mirror of left_mid_range
right_three         | beyond 3pt arc    | (outside arc)     | Mirror of left_three
right_corner_three  | 27.75 – 28.65     | 0 – 0.90 or       | Mirror of left_corner_three
                    |                   | 14.34 – 15.24     |
center              | 12.0 – 16.65      | 5.49 – 9.75       | Center circle area
```

Three-point arc radius: **7.24 m** from the basket. Basket positions: `[1.575, 7.62]` (near) and `[27.075, 7.62]` (far).

---

## 8. Schema Versioning Policy

- **Minor version bump (1.0 → 1.1):** additive change (new optional field). Old clients can ignore the new field. No re-processing required.
- **Major version bump (1.x → 2.0):** breaking change (field rename, type change, removal). Existing jobs processed under v1.x are not automatically migrated. A migration script must be provided.
- **Version field:** all documents that are stored as files (telemetry, calibration, analytics summary, annotations, coaching report) include `"schema_version"`. The Job record in PostgreSQL is migrated via Alembic.
- **TypeScript types** are auto-generated from Pydantic models (see `docs/ADR.md` ADR-010). Run `make generate-types` after any schema change.

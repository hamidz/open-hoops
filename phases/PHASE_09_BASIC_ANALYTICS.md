# Phase 09 — Basic Analytics

> **Goal:** Implement the analytics worker that reads telemetry and produces per-player and per-team metrics. Expose these via API and display them in the dashboard.

---

## Status: 🔲 Pending

---

## Prerequisites

- Phase 07 complete (telemetry schema finalized).
- Phase 08 in progress or complete (analytics feed the heatmaps too).

---

## Agent Instructions

Read `ARCHITECTURE.md` for the analytics summary schema.
Read `docs/STACK.md` for the analytics library choices (Pandas, NumPy).

Your job is to implement `services/analytics_worker`. This worker reads telemetry and produces the analytics summary JSON that feeds both the dashboard and the LLM report (Phase 10).

---

## Analytics Metrics (MVP)

### Per-Player Metrics

| Metric | Description | Formula |
|---|---|---|
| `total_distance_m` | Total distance traveled across all sampled frames | Sum of Euclidean distances between consecutive `court_xy_m` positions |
| `avg_speed_ms` | Average movement speed | `total_distance_m / duration_seconds` |
| `max_speed_ms` | Peak instantaneous speed | Max speed over any 1-second window |
| `court_coverage_pct` | Percentage of court area visited | Count cells in a 0.5m grid that the player passed through / total cells |
| `zone_distribution` | Fraction of time spent in each court zone | See zone definitions below |
| `time_in_paint_pct` | % of time spent in the paint area | Subset of zone_distribution |
| `frames_tracked` | Number of frames the player was detected | Count of detections with this track_id |
| `tracking_coverage_pct` | Frames tracked / total sampled frames | Indicator of detection reliability |

### Per-Team Metrics

| Metric | Description |
|---|---|
| `avg_spacing_m` | Average pairwise distance between all 5 players on the team |
| `min_spacing_m` | Minimum pairwise distance (crowding indicator) |
| `court_coverage_pct` | Team-level court coverage (union of individual coverages) |

### Game-Level Metrics

| Metric | Description |
|---|---|
| `duration_seconds` | Total video duration analyzed |
| `total_sampled_frames` | Total frames with detections |
| `avg_detections_per_frame` | Average number of objects detected per frame |
| `ball_tracking_coverage_pct` | % of frames where the ball was detected |

---

## Court Zone Definitions (NBA)

```
Full court (28.65 m × 15.24 m), origin at near-left corner:

Left-side zones (x: 0–14.325):
  - left_paint:        x < 5.79, 1.83 < y < 13.41
  - left_mid_range:    5.79 < x < left_3pt_arc boundary
  - left_three:        beyond left_3pt_arc (7.24 m from basket)
  - left_corner_three: x < 0.9, y < 0.9 OR y > 14.34

Right-side zones (x: 14.325–28.65): mirror of left

Center:
  - center:            x: 12–16, y: 5.5–9.7 (approximate)
```

The analytics worker should include a utility function:
`classify_zone(court_x, court_y) → zone_label`

---

## Tasks

### Analytics Worker

- [ ] Implement `services/analytics_worker/worker.py`:
  - Picks up analytics jobs from a dedicated Redis queue (or same queue with different task type).
  - Downloads telemetry JSON from MinIO.
  - Runs analytics pipeline.
  - Writes analytics summary JSON to MinIO.
  - Updates job record.

### Analytics Pipeline

- [ ] `services/analytics_worker/pipeline/loader.py`:
  - Load telemetry JSON into a Pandas DataFrame.
  - Explode `detections` array into rows.
  - Filter to `object_class = "person"` for player analytics.

- [ ] `services/analytics_worker/pipeline/movement.py`:
  - Compute per-player distance, speed, court coverage.

- [ ] `services/analytics_worker/pipeline/zones.py`:
  - Classify each detection into a court zone.
  - Compute zone distribution per player.

- [ ] `services/analytics_worker/pipeline/spacing.py`:
  - Compute pairwise player distances per frame.
  - Requires team assignment (use mock teams if annotation not done: odd track_ids = home, even = away).

- [ ] `services/analytics_worker/pipeline/summary.py`:
  - Assemble all metrics into the analytics summary schema.
  - Validate with Pydantic model.
  - Write to MinIO `artifacts/{job_id}/analytics_summary.json`.

### Analytics Summary Schema (Finalized)

This phase must use the canonical analytics schema in `docs/DATA_SCHEMAS.md`.

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

### API Endpoints

- [ ] `GET /api/jobs/{job_id}/analytics` — return full analytics summary JSON.
- [ ] `GET /api/jobs/{job_id}/analytics/players/{track_id}` — return metrics for a single player.
- [ ] `GET /api/jobs/{job_id}/analytics/teams` — return team-level metrics.

### Frontend — Analytics Display

- [ ] Update Players tab in dashboard to use real analytics summary.
- [ ] Add zone distribution stacked bar chart per player.
- [ ] Add team spacing chart (line chart over time, if time-series spacing is computed).
- [ ] Add overall game stats panel (duration, ball tracking %, avg detections).

### Tests

- [ ] Unit test: distance computation from known coordinates.
- [ ] Unit test: zone classification for all 6 zone types.
- [ ] Unit test: spacing calculation for known player positions.
- [ ] Unit test: analytics summary schema validation.
- [ ] Integration test: full analytics pipeline on mock telemetry.

---

## Outputs

- `services/analytics_worker/` — complete analytics worker.
- `packages/shared_types/models/analytics.py` — Pydantic analytics summary model.
- `apps/api/app/routers/analytics.py` — analytics API endpoints.
- Analytics summary JSON in MinIO for a test job.

---

## Definition of Done

- [ ] Analytics worker processes a completed CV job end-to-end.
- [ ] Analytics summary JSON written to MinIO and matches schema.
- [ ] All per-player metrics computed correctly.
- [ ] Dashboard shows real analytics for a processed job.
- [ ] All unit and integration tests pass.
- [ ] Phase status updated in `AGENTIC_EXECUTION_PLAN.md`.

---

## Completion Note

> _Agent: add completion date and summary here when done._

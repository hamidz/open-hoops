# Phase 08 — Heatmaps and Visualizations

> **Goal:** Render player movement heatmaps, court position overlays, and timeline-based telemetry visualizations in the dashboard using real telemetry data.

---

## Status: 🔲 Pending

---

## Prerequisites

- Phase 03 complete (dashboard with CourtSVG and mock data).
- Phase 07 complete (telemetry schema finalized and API working).

---

## Agent Instructions

Read `ARCHITECTURE.md` for the telemetry schema. Read Phase 03 completion notes for the existing CourtSVG component.

Your job is to replace mock visualizations with real telemetry-driven renderings and add heatmap generation (both frontend and backend).

---

## Heatmap Types

### 1. Movement Heatmap (Court Presence Density)

- Show where a player (or all players) spent time on the court.
- Color scale: cool (low density) → warm (high density).
- Source: all `court_xy_m` positions for a given `track_id`.

### 2. Team Heatmap

- Aggregate movement heatmap for all players on one team.
- Toggle: Home | Away | Both.

### 3. Shot Location Map (Post-MVP)

- Placeholder for Phase 11 (when shot events are annotated).

---

## Tasks

### Backend — Heatmap Generation (`services/analytics_worker`)

- [ ] Implement `services/analytics_worker/heatmaps.py`:
  - Input: all `court_xy_m` positions for a given `track_id` (or team).
  - Method: 2D Gaussian Kernel Density Estimation (KDE) using `scipy.stats.gaussian_kde`.
  - Output: 2D grid array normalized to [0, 1], plus court dimension metadata.
  - Export as: JSON grid (for frontend rendering) and PNG (for download/report).
- [ ] Write heatmap PNG and JSON to MinIO `artifacts/{job_id}/heatmaps/`.

### API Endpoints

- [ ] `GET /api/jobs/{job_id}/heatmaps` — list available heatmaps (by player and team).
- [ ] `GET /api/jobs/{job_id}/heatmaps/{track_id}` — return heatmap grid JSON for a player.
- [ ] `GET /api/jobs/{job_id}/heatmaps/{track_id}/image` — return pre-signed PNG URL.
- [ ] `GET /api/jobs/{job_id}/heatmaps/team/{team}` — return team heatmap.

### Frontend — Heatmap Overlay

- [ ] `CourtHeatmap.tsx` component:
  - Renders a heatmap grid on top of `CourtSVG` using an HTML5 Canvas overlay or SVG gradient fill.
  - Color scale: blue (cold) → green → yellow → red (hot).
  - Accepts heatmap grid JSON as prop.
- [ ] Heatmap opacity slider (0–100%).
- [ ] Player selector: show heatmap for individual player or team.

### Frontend — Frame Scrubber

- [ ] Replace Phase 03 placeholder scrubber with a functional time-based scrubber:
  - Slider range: 0 to `total_sampled_frames`.
  - On change: fetch `GET /api/jobs/{job_id}/telemetry/frame/{frame_index}`.
  - Update player dot positions on court in real time.
- [ ] Display current timestamp (mm:ss) alongside frame index.

### Frontend — Player Trail

- [ ] For a selected player, draw their movement path over the last N seconds on the court.
- [ ] Trail fades with age (opacity decreases for older positions).
- [ ] N seconds configurable via a small UI control (default: 5 seconds).

### Frontend — Timeline Filter

- [ ] Allow user to select a time range (start_frame → end_frame) to filter heatmap.
- [ ] Two-handle range slider component.
- [ ] Heatmap updates to reflect only positions within the selected range.

### Tests

- [ ] Unit test: KDE heatmap computation (known positions → expected grid shape and values).
- [ ] Unit test: heatmap API endpoint returns correct grid for a test job.
- [ ] Unit test: heatmap PNG generation writes a valid image file.

---

## Outputs

- `services/analytics_worker/heatmaps.py` — KDE heatmap generator.
- `apps/api/app/routers/heatmaps.py` — heatmap API endpoints.
- `apps/web/src/components/CourtHeatmap.tsx` — heatmap overlay component.
- `apps/web/src/components/FrameScrubber.tsx` — functional frame scrubber.
- `apps/web/src/components/PlayerTrail.tsx` — player trail overlay.
- Heatmap PNGs and JSON grids in MinIO for a test job.

---

## Definition of Done

- [ ] Heatmap renders correctly on the court for a real processed job.
- [ ] Frame scrubber moves player positions in real time.
- [ ] Player trail displays for a selected player.
- [ ] Timeline filter adjusts heatmap for selected time range.
- [ ] All unit tests pass.
- [ ] Phase status updated in `AGENTIC_EXECUTION_PLAN.md`.

---

## Completion Note

> _Agent: add completion date and summary here when done._

# Phase 03 — Mock Data Dashboard

> **Goal:** Build a fully functional analytics dashboard using synthetic (mock) telemetry data. No real video processing is required. The owner should be able to see the end product visualizations before any CV work begins.

---

## Status: 🔲 Pending

---

## Prerequisites

- Phase 02 complete (local dev stack running).

---

## Agent Instructions

Read `ARCHITECTURE.md` for the telemetry and analytics summary schemas before starting.

Your job is to build the frontend dashboard and the mock data pipeline that feeds it. The goal is a working UI that the owner can use to validate that the visualizations, layout, and output format meet their needs — before any real CV code is written.

Do not implement real video processing. Use hard-coded or generated mock data only.

---

## Mock Data Specification

### Mock Telemetry

Generate synthetic per-frame detections that simulate a 5v5 basketball game:

- 10 players (5 per team) with realistic court positions
- 1 ball (best-effort; can be missing some frames)
- 30 fps × 5 minutes = 9,000 frames minimum
- Player positions should follow plausible basketball movement patterns (not purely random)
- Track IDs stable across frames (1–10 for players, 11 for ball)

### Mock Analytics Summary

Compute or hard-code:

- Total distance per player (realistic range: 1,500–3,000 m for 5 min)
- Average speed per player
- Court coverage percentage per player
- Zone distribution (paint / mid-range / three-point) per player
- Team spacing average (in meters)

### Mock Job Record

- Pre-seed the database with 1–2 mock completed jobs.
- Jobs should reference mock telemetry URLs (can be static files in MinIO).

---

## Tasks

### Mock Data Generator

- [ ] Create `scripts/generate_mock_data.py`:
  - Generates `mock_telemetry.json` following the detection schema in `ARCHITECTURE.md`.
  - Generates `mock_analytics_summary.json` following the analytics summary schema.
  - Writes both files to MinIO `artifacts` bucket.
  - Seeds `jobs` table with a mock completed job record.

### API Endpoints

Implement the following read-only endpoints in `apps/api`:

- [ ] `GET /api/jobs` — list all jobs (returns mock job).
- [ ] `GET /api/jobs/{job_id}` — get job details.
- [ ] `GET /api/jobs/{job_id}/telemetry` — return telemetry JSON.
- [ ] `GET /api/jobs/{job_id}/analytics` — return analytics summary JSON.

### Frontend Dashboard

Build in `apps/web`:

#### Layout

- [ ] Sidebar navigation: Jobs list, Dashboard, Settings (placeholder).
- [ ] Main content area with tab navigation: Overview | Court Map | Players | Report.

#### Overview Tab

- [ ] Job status badge (Queued / Processing / Complete / Failed).
- [ ] Key stats cards: total players, game duration, team spacing average.
- [ ] Per-player stats table: Track ID, label, distance, avg speed, coverage %.

#### Court Map Tab

- [ ] SVG basketball court (full-court or half-court toggle).
- [ ] Court dimensions based on confirmed inputs (NBA default).
- [ ] Player position scatter for a selected frame (scrubber bar for frame selection).
- [ ] Team color coding (home = blue, away = red as default).

#### Players Tab

- [ ] Per-player card: track ID, team, distance, speed, zone distribution bar chart.

#### Report Tab

- [ ] Placeholder: "LLM coaching report will appear here after Phase 10."

---

## Court SVG Specification

The court SVG component must include:

- Full-court outline (28.65 m × 15.24 m scaled to SVG viewport)
- Center circle
- Three-point arcs (both ends)
- Paint / key rectangles (both ends)
- Free throw circles (both ends)
- Center line

SVG should accept a `orientation` prop: `full` | `half-left` | `half-right`.

---

## Outputs

- `scripts/generate_mock_data.py` — runnable mock data generator.
- `apps/api/app/routers/jobs.py` — jobs API router with mock-data-compatible endpoints.
- `apps/web/src/components/CourtSVG.tsx` — reusable court SVG component.
- `apps/web/src/app/dashboard/` — dashboard page with all tabs.
- Mock data seeded in local MinIO and PostgreSQL.

---

## Definition of Done

- [ ] `python scripts/generate_mock_data.py` runs without error and seeds data.
- [ ] `GET /api/jobs` returns at least 1 mock job.
- [ ] Dashboard loads at `http://localhost:3000/dashboard`.
- [ ] All 4 tabs render without console errors.
- [ ] CourtSVG renders correctly at full and half-court orientations.
- [ ] Owner has reviewed and confirmed the dashboard layout meets their needs.
- [ ] Phase status updated in `AGENTIC_EXECUTION_PLAN.md`.

---

## Completion Note

> _Agent: add completion date and summary here when done._

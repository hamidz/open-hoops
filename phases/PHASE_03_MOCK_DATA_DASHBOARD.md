# Phase 03 — Mock Data Dashboard

> **Goal:** Build a fully functional analytics dashboard using synthetic (mock) telemetry data. No real video processing is required. The owner should be able to see the end product visualizations before any CV work begins.

---

## Status: 🟡 In Progress

---

## Prerequisites

- Phase 02 complete (local dev stack running).

---

## Agent Instructions

Read `ARCHITECTURE.md` for the telemetry and analytics summary schemas before starting.
Read `docs/DESIGN_SYSTEM.md` before writing any CSS or component code — all visual decisions are pre-defined.
Read `docs/UX_FLOWS.md` for the onboarding flow, loading skeleton specs, and navigation structure.

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

Implement the following read-only endpoints in `apps/api` (use `/api/v1/` prefix — ADR-013):

- [ ] `GET /api/v1/jobs` — list all jobs (returns mock job).
- [ ] `GET /api/v1/jobs/{job_id}` — get job details.
- [ ] `GET /api/v1/jobs/{job_id}/telemetry` — return signed download URL (not inline JSON — see telemetry strategy in `docs/API_CONTRACT.md` Section 7).
- [ ] `GET /api/v1/jobs/{job_id}/telemetry/frame/{frame_index}` — return inline detections for one frame.
- [ ] `GET /api/v1/jobs/{job_id}/analytics` — return analytics summary (inline JSON).

### Frontend Dashboard

Build in `apps/web`:

#### Providers and State Setup

- [ ] Confirm `src/app/providers.tsx` wraps the app in `QueryClientProvider` (from Phase 01 scaffold).
- [ ] Configure `QueryClient` with sensible defaults:
  ```ts
  new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 10_000,       // 10 seconds
        retry: 2,
        refetchOnWindowFocus: true,
      }
    }
  })
  ```
- [ ] Create a `useJobStatus` hook using TanStack Query that polls job status:
  ```ts
  useQuery({
    queryKey: ['job', jobId],
    queryFn: () => fetchJob(jobId),
    refetchInterval: (query) => {
      // Stop polling when job reaches terminal state
      const status = query.state.data?.status
      return status === 'complete' || status === 'failed' ? false : 3000
    }
  })
  ```
  This replaces the fragile `setInterval`/`useEffect` pattern and is reusable in Phase 04.

#### Layout

- [ ] Sidebar navigation: Jobs list, Upload (Phase 04 placeholder), Settings (placeholder).
- [ ] Sidebar: 240px fixed width on desktop; collapses to icon mode on 1024px screens.
- [ ] Main content area with tab navigation: Overview | Court Map | Players | Report.

#### Design System Application

- [ ] Apply `docs/DESIGN_SYSTEM.md` color tokens via Tailwind config (dark mode default).
- [ ] Use Inter Variable + JetBrains Mono fonts loaded via `next/font/google`.
- [ ] All stat numbers use `font-mono` class with tabular numerics.

#### Overview Tab

- [ ] `JobStatusBadge` component — animated status badge using shadcn/ui `Badge` + Lucide icon.
- [ ] Skeleton loading state for all cards while data fetches.
- [ ] Key stats cards (shadcn/ui `Card`): total players, game duration, team spacing average.
- [ ] Per-player stats table (shadcn/ui `Table`): Track ID, label, distance, avg speed, coverage %.
- [ ] Empty state: display when no jobs exist (link to upload).

#### Court Map Tab

- [ ] `CourtSVG` component with visual spec from `docs/DESIGN_SYSTEM.md` Section 5.
- [ ] Court surface: dark background (`court-800`); court lines: `court-600`.
- [ ] Player markers: circle with team color, track number label.
- [ ] Full-court and half-court orientations.
- [ ] `FrameScrubber` component — shadcn/ui `Slider` with frame index display.
- [ ] Keyboard: `←`/`→` arrows step frames; `Space` plays/pauses.
- [ ] Skeleton: court-shaped rectangle while telemetry downloads from MinIO.

#### Players Tab

- [ ] Per-player `Card` with: track ID, team badge, distance (JetBrains Mono), speed, `ZoneBar` component.
- [ ] `ZoneBar`: horizontal bar split into paint / mid-range / three-point segments, team color tint.

#### Report Tab

- [ ] Placeholder card: "LLM coaching report will appear here after Phase 10." with Lucide `FileText` icon.

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

### Progress Note — 2026-05-03

The current dashboard can list jobs, show job details, and render generated first-pass player analytics after an upload. This is enough for a demoable first workflow, but the full Phase 03 target remains open: mock telemetry export, court SVG/tabs, scrubber interactions, and richer seeded dashboard states.

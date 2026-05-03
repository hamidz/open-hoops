# UX Flows and Diagrams — Open Hoops

> User journey, screen inventory, and planning diagrams for the MVP interface.

---

## 1. UX Principles

- Prefer guided workflows over hidden automation.
- Show progress and confidence at every expensive or uncertain step.
- Make manual correction a first-class part of the product.
- Avoid color-only communication; every status and warning needs text.
- Keep coach-facing output concise and action-oriented.
- Never show a blank void while content loads — use skeletons and placeholders.
- Keyboard power users (repeated use) should not be slowed by mouse-only flows.

---

## 2. Screen Inventory

| Screen | Route | Primary Purpose |
|---|---|---|
| Home / landing | `/` | First-time onboarding: what this is, how it works, link to upload |
| Dashboard | `/dashboard` | Job list and recent status overview |
| Upload | `/upload` | Select, validate, and upload video |
| Job detail | `/dashboard/jobs/{job_id}` | Status, metadata, tabs, actions |
| Calibration | `/dashboard/jobs/{job_id}/calibrate` | Manual court calibration |
| Report | `/dashboard/jobs/{job_id}/report` or tab | Generate and read coaching report |
| Settings placeholder | `/settings` or dashboard tab | Local configuration display, post-MVP expansion |

---

## 3. Primary User Journey

```text
Open dashboard
      ↓
Upload video
      ↓
Job queued
      ↓
Calibration needed?
      ├─ yes → Calibrate court → Job queued again
      └─ no  → Continue processing
      ↓
CV processing
      ↓
Telemetry and analytics generated
      ↓
Review dashboard visualizations
      ↓
Annotate players / shots if needed
      ↓
Recompute analytics
      ↓
Generate local LLM coaching report
      ↓
Export/download outputs
```

---

## 4. Upload Flow

```text
Select file
  ↓
Browser validates extension and size
  ↓
Show selected filename, size, and label input
  ↓
User clicks Upload
  ↓
Progress bar updates during multipart POST
  ↓
Success: redirect to job detail
  ↓
Failure: show clear recoverable error
```

Required UI states:

- Empty file dropzone.
- File selected and valid.
- File selected but invalid type.
- File selected but too large.
- Uploading with progress.
- Server validation failed.
- Upload succeeded.

---

## 5. Job Status Flow

```text
queued
  ↓
processing ──────────────┐
  │                      │
  ├─ calibration_needed  │
  │       ↓              │
  │   user calibrates    │
  │       ↓              │
  └──── queued           │
          ↓              │
       processing        │
          ↓              │
       complete          │
                         ↓
                       failed → retry → queued
```

Job detail must show:

- Status badge.
- Progress bar when `processing`.
- Calibration call-to-action when `calibration_needed`.
- Error message and retry button when `failed`.
- Delete action for non-processing jobs.
- Metadata: original filename, label, file size, upload time, sport.

---

## 6. Calibration Flow

```text
Open calibration page
      ↓
Load first video frame
      ↓
Show reference court diagram with named points
      ↓
User selects named court point
      ↓
User clicks matching point on frame
      ↓
Marker appears and can be moved/removed
      ↓
At 4+ points, Compute Calibration is enabled
      ↓
Backend computes homography and reprojection error
      ↓
Projected court overlay appears for visual check
      ↓
User accepts or resets
```

Calibration quality language:

| Reprojection Error | UI Label | Meaning |
|---|---|---|
| `< 10 px` | Good | Continue confidently |
| `10–25 px` | Review | Usable but inspect overlay |
| `> 25 px` | Poor | Recommend redoing points |

---

## 7. Dashboard Tabs

### Overview

- Job summary.
- Total players/tracks.
- Duration analyzed.
- Ball tracking coverage.
- Team spacing average.
- Recent warnings: low tracking coverage, missing calibration, failed artifacts.

### Court Map

- Court SVG with current player positions.
- Frame scrubber.
- Player/team filter.
- Optional player trail.
- Shot markers after annotation phase.

### Heatmaps

- Player/team selector.
- Opacity slider.
- Time range filter.
- PNG download action.

### Players

- Player cards or table.
- Label/team display.
- Distance, speed, coverage, tracking reliability.
- Zone distribution bars.

### Annotations

- Track list with thumbnail if available.
- Label input.
- Team selector.
- Flag incorrect toggle.
- Shot annotation controls.
- Recompute analytics button.

### Report

- Generate/regenerate button.
- Report status.
- Rendered report sections.
- Model and timestamp.
- Confidence caveat if tracking or ball coverage is low.
- Copy to clipboard.

---

## 8. Error and Empty States

| Context | Required Message |
|---|---|
| No jobs | Explain upload as next step and link to `/upload` |
| Upload invalid type | State supported types: MP4 and MOV |
| Upload too large | Show configured max size |
| Calibration missing | Explain why calibration is needed and provide button |
| Telemetry missing | Explain job is not complete or processing failed |
| Analytics missing | Offer recompute if telemetry exists |
| Ollama unavailable | Explain local model service is not reachable |
| Low tracking coverage | Warn that metrics/report confidence is reduced |

---

## 9. Onboarding Flow (First-Time User)

The `/` home page serves as the onboarding experience for a first-time user who has never uploaded a video.

```text
Landing page loads
      ↓
Hero: "Open Hoops — Local basketball analytics"
      ↓
3-step explainer:
  1. Upload a game video
  2. Calibrate the court (one-time per camera angle)
  3. Review player movement, heatmaps, and get a coaching report
      ↓
CTA: "Upload your first video →"
      ↓
If jobs already exist: dashboard link instead
```

Required landing page sections:

- **Hero:** Product tagline + primary CTA button.
- **How it works:** 3-step visual walkthrough (icons + short text per step).
- **What you get:** 3–4 output previews (heatmap screenshot, analytics card, report excerpt — use static images from mock data).
- **Privacy note:** "Everything stays on your machine. No cloud accounts needed."
- **System status:** Small indicator showing whether Docker services are healthy (`GET /api/v1/health`). If any service is down, show a warning with a link to `docs/QUICKSTART.md`.

---

## 10. Loading and Skeleton States

Every page with async data must show skeletons before content renders. Never show blank voids.

| Context | Skeleton Behavior |
|---|---|
| Job list (`/dashboard`) | 3–5 `Skeleton` rows matching job card height while TanStack Query fetches |
| Job detail (`/dashboard/jobs/{id}`) | Skeleton for status badge, metadata fields, and tab content area |
| Court SVG (court map tab) | `Skeleton` rectangle with 1.88:1 aspect ratio (court proportions) |
| Player stats cards | 4 `Skeleton` cards in a 2-column grid |
| Heatmap overlay | Show empty court SVG immediately; overlay fades in when KDE data arrives |
| Calibration frame | `Skeleton` full-width rectangle, aspect ratio preserved until frame image loads |
| Analytics summary | 4 `Skeleton` stat cards + 1 `Skeleton` table |
| Coaching report | Skeleton lines simulating paragraph text |

**Implementation note:** Use TanStack Query's `isLoading` and `isFetching` states. Show skeleton on `isLoading` (no cached data). Show stale data with a subtle refresh indicator on `isFetching` (has cached data, refreshing in background).

---

## 11. Calibration Point Reference Spec

The calibration panel must include a reference court diagram with exactly these named points available for selection:

| # | Point Label | Court Coordinates (NBA, meters) | Required? |
|---|---|---|---|
| 1 | Near-left corner | [0, 0] | Required (min 4) |
| 2 | Near-right corner | [0, 15.24] | Required (min 4) |
| 3 | Far-left corner | [28.65, 0] | Required (min 4) |
| 4 | Far-right corner | [28.65, 15.24] | Required (min 4) |
| 5 | Left free throw line — left | [5.79, 1.83] | Recommended |
| 6 | Left free throw line — right | [5.79, 13.41] | Recommended |
| 7 | Right free throw line — left | [22.86, 1.83] | Recommended |
| 8 | Right free throw line — right | [22.86, 13.41] | Recommended |
| 9 | Center circle center | [14.325, 7.62] | Optional |

**UX flow for point placement:**

1. The reference panel shows the court diagram with all 9 points labeled as numbered circles.
2. User clicks a numbered point on the reference diagram to **select** it. Selected point highlights with a pulsing ring.
3. User clicks the corresponding location on the video frame. A numbered marker appears on the frame.
4. User can click and drag any placed marker to adjust position.
5. User can click a placed marker and press `Delete` to remove it.
6. Status counter shows: "4/4 required points placed. Add more for better accuracy."
7. "Compute Calibration" button enables when ≥ 4 points are placed.
8. After computing: show reprojection error badge + overlay on frame.

**FIBA court note:** FIBA dimensions differ from NBA (28 m × 15 m, 6.75 m 3pt arc, 5.8 m free throw distance). The reference panel switches coordinate labels when "FIBA" is selected in the court type dropdown.

---

## 12. Keyboard Power User Shortcuts

Coaches using this tool repeatedly should have keyboard shortcuts for high-frequency actions:

| Context | Key | Action |
|---|---|---|
| Dashboard | `N` | Navigate to Upload page |
| Dashboard | `↑` / `↓` | Navigate job list |
| Dashboard | `Enter` | Open selected job |
| Job detail | `1`–`6` | Switch tabs (Overview, Court Map, Heatmaps, Players, Annotations, Report) |
| Court map tab | `←` / `→` | Step frame scrubber by 1 frame |
| Court map tab | `Shift+←` / `Shift+→` | Step frame scrubber by 10 frames |
| Court map tab | `Space` | Play/pause frame scrubber animation |
| Heatmaps tab | `P` | Cycle through players |
| Players tab | `↑` / `↓` | Navigate player list |
| Calibration page | `Delete` | Remove last placed calibration point |
| Calibration page | `Escape` | Deselect active reference point |
| Any page | `?` | Show keyboard shortcut help overlay |

Shortcuts are documented in a `KeyboardShortcutsHelp` component triggered by `?`. All shortcuts that modify data require confirmation or are trivially reversible.

---

## 13. Accessibility Checklist

- All controls reachable by keyboard.
- Status text visible in addition to color badges.
- Upload and calibration errors announced near the relevant control.
- Court markers have labels/numbers visible outside color alone.
- Sliders have text values and accessible names.
- Tables have headings and sortable column labels where applicable.
- Keyboard shortcuts do not conflict with browser defaults or screen reader shortcuts.
- `prefers-reduced-motion`: all non-essential animations are disabled.

---

## 14. UX Review Gates

- Phase 03: Owner validates dashboard layout using mock data.
- Phase 04: Owner validates upload/status flow.
- Phase 06: Owner validates calibration flow with a real frame.
- Phase 08: Owner validates heatmap and scrubber usability.
- Phase 11: Owner validates annotation workflow.
- Phase 12: Owner validates end-to-end quickstart flow.

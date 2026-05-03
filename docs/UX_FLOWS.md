# UX Flows and Diagrams — Open Hoops

> User journey, screen inventory, and planning diagrams for the MVP interface.

---

## 1. UX Principles

- Prefer guided workflows over hidden automation.
- Show progress and confidence at every expensive or uncertain step.
- Make manual correction a first-class part of the product.
- Avoid color-only communication; every status and warning needs text.
- Keep coach-facing output concise and action-oriented.

---

## 2. Screen Inventory

| Screen | Route | Primary Purpose |
|---|---|---|
| Home / landing | `/` | Project intro and link to dashboard/upload |
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

## 9. Accessibility Checklist

- All controls reachable by keyboard.
- Status text visible in addition to color badges.
- Upload and calibration errors announced near the relevant control.
- Court markers have labels/numbers visible outside color alone.
- Sliders have text values and accessible names.
- Tables have headings and sortable column labels where applicable.

---

## 10. UX Review Gates

- Phase 03: Owner validates dashboard layout using mock data.
- Phase 04: Owner validates upload/status flow.
- Phase 06: Owner validates calibration flow with a real frame.
- Phase 08: Owner validates heatmap and scrubber usability.
- Phase 11: Owner validates annotation workflow.
- Phase 12: Owner validates end-to-end quickstart flow.

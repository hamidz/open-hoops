# Phase 06 — Court Calibration

> **Goal:** Implement the manual court calibration tool. The user clicks known points on the first video frame to define the mapping from pixel coordinates to real-world court coordinates.

---

## Status: 🔲 Pending

---

## Prerequisites

- Phase 04 complete (video upload, job record exists).
- Phase 05 CV worker homography module (`pipeline/homography.py`) may begin development concurrently — calibration feeds the CV pipeline. Phase 06 backend (homography computation) should be completed **before** Phase 05 integration testing, so the CV worker can use a real computed homography matrix rather than a hardcoded one.

**Recommended dependency order:**
```
Phase 06 — Backend Only (homography.py + API endpoints + tests)
      ↓
Phase 05 — CV Engine (uses real calibration from Phase 06 backend)
      ↕ (concurrent)
Phase 06 — Frontend UI (CalibrationCanvas + CourtReferencePanel)
```

---

## Agent Instructions

Read `ARCHITECTURE.md` for the calibration data flow and homography schema.
Read `docs/ADR.md` ADR-008 for the decision to use manual calibration.
Read `docs/DESIGN_SYSTEM.md` Section 5.4 for calibration point marker visual spec.
Read `docs/UX_FLOWS.md` Sections 11 and 12 for the calibration interaction flow and keyboard shortcuts.

Your job is to implement the calibration UI and the homography computation backend. This is the most UX-critical feature in the MVP — it must be intuitive and forgiving.

---

## Calibration Concept

To map pixel coordinates from the video to real basketball court coordinates, we need a homography matrix. This matrix is computed by providing at least 4 pairs of:

- A point in the video frame (pixels): `[px, py]`
- The corresponding known point on the court (meters from origin): `[court_x, court_y]`

Standard calibration points (use at least 4, recommend 6–8):

| Point Label | Court Coordinates (NBA, meters) |
|---|---|
| Near left corner | [0, 0] |
| Near right corner | [0, 15.24] |
| Far left corner | [28.65, 0] |
| Far right corner | [28.65, 15.24] |
| Left free throw line left | [5.79, 1.83] |
| Left free throw line right | [5.79, 13.41] |
| Right free throw line left | [22.86, 1.83] |
| Right free throw line right | [22.86, 13.41] |
| Center circle center | [14.325, 7.62] |

The calibration tool should provide a reference court diagram with these points labeled so the user knows which point to click. The exact UX interaction flow is specified in `docs/UX_FLOWS.md` Section 11. The visual design of markers and the reference panel is specified in `docs/DESIGN_SYSTEM.md` Section 5.4.

---

## Tasks

### API — Calibration Endpoints

- [ ] `GET /api/v1/jobs/{job_id}/calibration/frame` — return the first frame of the video as a JPEG image URL (stored in MinIO, signed URL, 30-minute expiry).
- [ ] `POST /api/v1/jobs/{job_id}/calibration` — accept calibration point pairs and compute homography:

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

- [ ] Compute homography matrix using `cv2.findHomography` with RANSAC.
- [ ] Store homography matrix as `calibration_json` in the job record.
- [ ] Update job status to `queued` (ready for CV processing) if previously `calibration_needed`.
- [ ] Return computed matrix and reprojection error estimate.

- [ ] `GET /api/v1/jobs/{job_id}/calibration` — return current calibration state (points + matrix if computed).
- [ ] `DELETE /api/v1/jobs/{job_id}/calibration` — reset calibration (allow redo).

### Frame Extraction for Calibration

- [ ] During upload (Phase 04), or on first calibration request:
  - Extract frame 0 from the video.
  - Save as `{job_id}/frame_0.jpg` in MinIO `artifacts` bucket.

### Frontend — Calibration UI

- [ ] Calibration page at `/dashboard/jobs/[job_id]/calibrate`.
- [ ] Display the first video frame as a full-width image.
- [ ] Reference court diagram panel (SVG, from Phase 03 CourtSVG component) with labeled calibration points.

#### Interaction Flow

1. User selects a court point from the reference diagram (or from a dropdown list).
2. User clicks the corresponding location on the video frame image.
3. A numbered marker appears at the clicked location.
4. User can reposition or remove any marker.
5. After ≥ 4 pairs, "Compute Calibration" button becomes active.
6. On compute: POST to API, display reprojection error, show success/failure.
7. User can re-do any point or reset all.

#### Validation UI

- [ ] Show a reprojection error indicator:
  - Green: < 10 pixels average error.
  - Yellow: 10–25 pixels.
  - Red: > 25 pixels (warn user to re-do points).
- [ ] Overlay projected court grid on video frame after successful calibration (visual verification).

### Tests

- [ ] Unit test: homography computation with known points.
- [ ] Unit test: reprojection error calculation.
- [ ] Unit test: calibration API request/response validation.

---

## Outputs

- `apps/api/app/routers/calibration.py` — calibration API endpoints.
- `apps/api/app/services/homography.py` — homography computation service.
- `apps/web/src/app/dashboard/jobs/[job_id]/calibrate/` — calibration UI page.
- `apps/web/src/components/CalibrationCanvas.tsx` — interactive frame image with click-to-mark.
- `apps/web/src/components/CourtReferencePanel.tsx` — reference court diagram with labeled points.

---

## Definition of Done

- [ ] User can open the calibration page for an uploaded job.
- [ ] User can click ≥ 4 points on the video frame.
- [ ] Homography matrix computed and stored in the job record.
- [ ] Reprojection error displayed to the user.
- [ ] Calibrated job re-enters the processing queue.
- [ ] All tests pass.
- [ ] Phase status updated in `AGENTIC_EXECUTION_PLAN.md`.

---

## Completion Note

> _Agent: add completion date and summary here when done._

# Phase 11 — Annotation Workflow

> **Goal:** Allow users to manually label players (names/numbers), assign team colors, confirm or correct shot events, and improve the accuracy of analytics by enriching the raw telemetry.

---

## Status: 🔲 Pending

---

## Prerequisites

- Phase 05 complete (telemetry with track IDs available).
- Phase 09 complete (analytics depend on team assignment).

---

## Agent Instructions

Read `ARCHITECTURE.md` for the telemetry and analytics schemas.

Your job is to implement the annotation layer that allows users to enrich raw tracking output with human-provided labels and corrections. This feeds back into the analytics and LLM report generation.

Annotations are stored separately from telemetry — the telemetry is never mutated. Annotations overlay on top at the analytics and display layer.

---

## Annotation Types

### 1. Player Labeling

- Assign a human-readable label to a track ID: `{ track_id: 3, label: "Jordan #23" }`.
- Assign a team to a track ID: `{ track_id: 3, team: "home" }`.

### 2. Team Color Assignment

- Set display color for home and away teams.
- Stored per-job: `{ home_color: "#1d4ed8", away_color: "#dc2626" }`.

### 3. Shot Event Annotation (MVP: manual)

- User marks a frame and location as a shot attempt.
- Fields: `{ frame_index, track_id, court_xy_m, made: true|false, shot_type: "3pt|2pt|ft" }`.

### 4. Event Correction

- User can mark a detection as incorrect (e.g., false positive — YOLO detected a referee as a player).
- Flagged track IDs are excluded from analytics.
- `{ track_id: 7, flagged: true, reason: "referee" }`.

---

## Tasks

### Annotation Data Model

- [ ] Define `Annotation` Pydantic model in `packages/shared_types/models/annotation.py`:

```python
class PlayerAnnotation(BaseModel):
    track_id: int
    label: Optional[str]
    team: Optional[Literal["home", "away"]]
    flagged: bool = False
    flag_reason: Optional[str]

class ShotAnnotation(BaseModel):
    frame_index: int
    track_id: int
    court_xy_m: tuple[float, float]
    made: bool
    shot_type: Literal["3pt", "2pt", "ft"]

class TeamColors(BaseModel):
    home_color: str  # hex
    away_color: str

class JobAnnotations(BaseModel):
    job_id: str
    player_annotations: list[PlayerAnnotation]
    shot_annotations: list[ShotAnnotation]
    team_colors: TeamColors
    updated_at: datetime
```

### API Endpoints

- [ ] `GET /api/jobs/{job_id}/annotations` — return all annotations for a job.
- [ ] `PUT /api/jobs/{job_id}/annotations/players/{track_id}` — set label/team/flag for a player.
- [ ] `POST /api/jobs/{job_id}/annotations/shots` — add a shot annotation.
- [ ] `DELETE /api/jobs/{job_id}/annotations/shots/{shot_id}` — remove a shot annotation.
- [ ] `PUT /api/jobs/{job_id}/annotations/team-colors` — update team display colors.
- [ ] `POST /api/jobs/{job_id}/annotations/recompute` — trigger analytics recomputation using updated annotations.

### Annotation Storage

- [ ] Store annotations as `artifacts/{job_id}/annotations.json` in MinIO.
- [ ] Also store in PostgreSQL `annotations` table for fast querying.

### Analytics Integration

- [ ] Update `services/analytics_worker` to read `annotations.json` if present:
  - Apply `team` assignments from player annotations.
  - Exclude flagged track IDs.
  - Include shot annotations in per-player shot stats.

### Frontend — Player Annotation Panel

- [ ] Add annotation sidebar to the job dashboard.
- [ ] For each detected track ID, show:
  - Preview thumbnail from a debug frame.
  - Text input for player label.
  - Dropdown for team assignment (Home / Away / Unknown).
  - "Flag as incorrect" toggle.
- [ ] Team color pickers (home + away).
- [ ] "Save Annotations" button → PUT to API.
- [ ] "Recompute Analytics" button → POST recompute.

### Frontend — Shot Annotation Tool

- [ ] In the Court Map tab, add "Annotate Shot" mode toggle.
- [ ] In this mode: clicking on the court SVG creates a shot annotation.
- [ ] Shot dialog: player selector, made/missed toggle, shot type selector.
- [ ] Confirmed shots displayed as markers on the court (❌ missed, ✅ made).

### Tests

- [ ] Unit test: annotation model validation.
- [ ] Unit test: analytics recompute excludes flagged track IDs.
- [ ] Unit test: shot annotations appear in player stats after recompute.

---

## Outputs

- `packages/shared_types/models/annotation.py`
- `apps/api/app/routers/annotations.py`
- `services/analytics_worker` — updated to consume annotations.
- `apps/web/src/components/AnnotationPanel.tsx`
- `apps/web/src/components/ShotAnnotationTool.tsx`

---

## Definition of Done

- [ ] User can label all 10 players and assign to teams.
- [ ] User can mark 3+ shot events on the court.
- [ ] "Recompute Analytics" triggers updated analytics with annotations applied.
- [ ] Dashboard reflects updated team colors and player labels.
- [ ] All tests pass.
- [ ] Phase status updated in `AGENTIC_EXECUTION_PLAN.md`.

---

## Completion Note

> _Agent: add completion date and summary here when done._

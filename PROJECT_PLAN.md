# Project Plan — Open Hoops

> Documentation-first, agentic solo project plan for an open-source basketball analytics platform.

---

## 1. Vision

Build an open-source, local-first basketball analytics platform that turns ordinary game video into useful coaching insights.

The platform should allow a coach, trainer, parent, or analyst to upload or process video and receive:

- player and ball tracking
- court-mapped telemetry
- movement heatmaps
- shot charts over time
- possession and spacing insights
- local LLM-generated coaching reports

## 2. Product Goal

**Poor man's sports analytics, pro-level output.**

This project is intentionally designed to use open-source tools and self-hostable infrastructure wherever possible.

## 3. Project Type

This is an **agentic solo project**.

That means:

- planning happens in Markdown first
- each phase is executed independently
- agents should work from explicit instructions and bounded scope
- no large implementation starts without a phase plan
- documentation is part of the product, not an afterthought

## 4. Recommended Stack

### Frontend
- Next.js
- Tailwind CSS
- SVG/D3/Plotly-based court visualizations

### Backend
- FastAPI
- Python worker services

### CV / ML
- OpenCV
- Ultralytics YOLO
- ByteTrack or BoT-SORT
- Homography-based court mapping

### Storage / Infra
- PostgreSQL
- Redis
- MinIO
- Docker Compose

### Local AI
- Ollama
- Llama / Mistral / Qwen class local models

## 5. MVP Definition

Recommended MVP:

A user uploads a fixed sideline basketball video, manually calibrates the court, processes the video, and receives:

- player/team movement telemetry
- court heatmaps
- basic analytics summaries
- a local LLM-generated coaching report

## 6. Non-Goals For MVP

The MVP should **not** attempt to solve everything.

Not MVP:

- perfect ball tracking
- fully automatic player identity
- flawless shot classification
- live streaming analytics
- multi-camera fusion
- mobile-first production experience
- fully autonomous coaching analysis without user review

## 7. Major Phases

### Phase 00 — Discovery
- confirm project inputs
- confirm MVP constraints
- confirm default court assumptions
- confirm hardware target

### Phase 01 — Repo Boilerplate
- monorepo plan
- directory structure
- docs structure
- initial implementation prompt

### Phase 02 — Local Dev Stack
- Docker Compose services
- local environment assumptions
- storage and queue planning

### Phase 03 — Mock Data Dashboard
- fake telemetry
- placeholder court visuals
- dashboard scaffolding

### Phase 04 — Video Upload Workflow
- upload UX
- metadata schema
- job creation flow

### Phase 05 — CV Engine MVP
- frame extraction
- detection
- tracking
- telemetry export

### Phase 06 — Court Calibration
- manual point selection
- homography transform
- court coordinate mapping

### Phase 07 — Telemetry Export
- detections schema
- tracks schema
- summary schema
- debug artifacts

### Phase 08 — Heatmaps and Visualizations
- movement heatmaps
- zone overlays
- timeline filters

### Phase 09 — Basic Analytics
- spacing metrics
- movement density
- court usage summaries

### Phase 10 — Local LLM Reports
- analytics summary prompt
- report generation
- confidence-aware report language

### Phase 11 — Annotation Workflow
- manual corrections
- shot confirmation
- team/player labeling

### Phase 12 — Self-Hosted Release
- Docker Compose release path
- quickstart docs
- sample data

## 8. Key Risks

1. Ball detection is hard.
2. Camera quality and angle variation will reduce reliability.
3. Player identity is difficult without manual help.
4. Shot detection is harder than movement analytics.
5. LLMs can hallucinate if given poor summaries.

## 9. Strategic Recommendations

1. Build the dashboard with **mock telemetry first**.
2. Treat **manual calibration** as a feature, not a failure.
3. Prioritize **movement and spacing** before advanced shot intelligence.
4. Keep the entire system **self-hostable**.
5. Use **Markdown as source of truth** for every phase.

## 10. Definition of Done for Planning Stage

Planning stage is complete when:

- core repo documentation exists
- phase files exist
- tasks files exist
- project owner inputs are clearly listed
- implementation can begin one phase at a time

## 11. Inputs Needed From Owner

See [INPUTS_NEEDED.md](./INPUTS_NEEDED.md).

---

## 12. Post-MVP Roadmap

The following capabilities are explicitly out of scope for v0.1.0-MVP but are planned for future releases.

### Performance & Accuracy

- **Automatic court calibration** — Hough line detection + template matching to eliminate manual point-click. Targeted for v0.2.0.
- **Fine-tuned YOLO model** — Domain-specific training data for better ball detection and player/referee disambiguation.
- **BoT-SORT as default tracker** — Better identity preservation for cameras with minor pan/tilt. Revisit after Phase 05 evaluation.
- **Re-ID module** — Re-identification across shot boundaries and occlusions using appearance embeddings.

### Video Input

- **Multi-camera support** — Fuse tracks from 2+ synchronized camera angles.
- **Live stream analytics** — RTSP/HLS input for real-time processing (significant architecture change).
- **Pan-tilt-zoom (PTZ) camera support** — Motion compensation for moving cameras.
- **Chunked/resumable upload** — tus.io protocol for large files over slow connections.

### Analytics

- **Shot detection** — Automatic detection of shot attempts from trajectory analysis (no annotation required).
- **Possession tracking** — Ball-player proximity to determine possession sequences.
- **Play recognition** — Pattern matching to identify common plays (pick-and-roll, fast break, etc.).
- **Season aggregation** — Combine analytics across multiple games for season-level trends.

### Reporting & Export

- **PDF report export** — Printable coaching report with embedded visualizations.
- **Video clip export** — Auto-cut highlight clips based on annotated shot events.
- **CSV export** — Raw telemetry and analytics for import into third-party tools.
- **Shareable report links** — Expiring share links for distributing reports without account login.

### Infrastructure

- **Cloud deployment option** — Optional cloud profile (AWS or GCP) for teams without local GPU hardware.
- **Multi-user support** — Authentication, team workspaces, and role-based access control.
- **Mobile-responsive UI** — Optimized dashboard experience for tablet/phone review.
- **Sensor-agnostic telemetry ingestion** — Accept GPS, UWB, or RFID position data directly, bypassing the CV pipeline.

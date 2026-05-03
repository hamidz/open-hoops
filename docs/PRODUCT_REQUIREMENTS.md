# Product Requirements — Open Hoops

> Product scope, success criteria, and MVP acceptance requirements. This document closes the gap between the high-level project plan and phase-level implementation tasks.

---

## 1. Product Summary

Open Hoops is a local-first basketball video analytics platform for coaches, trainers, parents, and analysts who want useful movement, spacing, and coaching insight without paid cloud analytics tooling.

The MVP intentionally favors reliability, transparency, and coach-reviewable output over fully automated sports intelligence.

---

## 2. Target Users

| User | Needs | MVP Support |
|---|---|---|
| Coach | Review team spacing, court usage, movement patterns | Dashboard, heatmaps, analytics summary, coaching report |
| Trainer | Review player movement and effort | Per-player distance, speed, coverage, trails |
| Parent / volunteer analyst | Run analysis locally without cloud setup | Docker Compose, simple upload, guided calibration |
| Developer / contributor | Build phase-by-phase from clear specs | Phase docs, ADRs, schemas, API contract |

---

## 3. MVP Problem Statements

1. Basketball game video is hard to review objectively without expensive tools.
2. Cloud sports analytics products are costly and may require uploading sensitive youth or school footage.
3. Computer vision is imperfect, so the product must let humans calibrate, label, and correct outputs.
4. Coaches need concise, actionable summaries rather than raw tracking data alone.

---

## 4. MVP User Stories

### Upload and Process Video

- As a user, I can upload an MP4 or MOV basketball video from my local machine.
- As a user, I can see upload progress and clear validation errors.
- As a user, I can monitor queued, processing, calibration-needed, complete, and failed job states.
- As a user, I can retry or delete failed jobs.

### Calibrate Court

- As a user, I can open the first frame of the uploaded video.
- As a user, I can click known court points and compute a homography.
- As a user, I can see calibration quality through reprojection error and a projected court overlay.
- As a user, I can reset and redo calibration if it is poor.

### Review Analytics

- As a user, I can view player and team movement on a court diagram.
- As a user, I can inspect per-player distance, average speed, max speed, court coverage, and zone distribution.
- As a user, I can view movement heatmaps by player, team, and selected time range.
- As a user, I can understand confidence limitations when tracking coverage is low.

### Annotate and Correct

- As a user, I can label players, assign teams, choose team colors, and flag incorrect tracks.
- As a user, I can manually mark shot attempts and made/missed outcomes.
- As a user, I can recompute analytics after annotations.

### Generate Coaching Report

- As a user, I can generate a local LLM coaching report from analytics data.
- As a user, I can see which model generated the report and when.
- As a user, I can copy or regenerate the report.
- As a user, I can trust that reports do not invent unsupported numbers.

---

## 5. MVP Functional Requirements

| Area | Requirement |
|---|---|
| Video input | Accept `.mp4` and `.mov` files up to configured max size, default 4 GB |
| Storage | Store videos and artifacts locally in MinIO |
| Jobs | Persist job status, progress, metadata, artifacts, and errors in PostgreSQL |
| Queue | Use Redis-backed background processing for CV, analytics, and report work |
| Calibration | Support manual 4+ point calibration with reprojection error feedback |
| CV | Detect players and ball best-effort, track objects, and export telemetry |
| Telemetry | Validate output against canonical schemas in `docs/DATA_SCHEMAS.md` |
| Analytics | Compute movement, coverage, spacing, zones, and ball coverage metrics |
| Visualization | Render court map, heatmaps, frame scrubber, player trails, and analytics cards |
| Annotation | Store annotations separately from telemetry and apply during analytics recompute |
| Reports | Generate local Ollama reports from analytics summary only |
| Export | Allow JSON and PNG artifact download for MVP outputs |

---

## 6. MVP Non-Functional Requirements

| Category | Requirement |
|---|---|
| Privacy | No external cloud service required for normal MVP operation |
| Security | No committed secrets; `.env` files ignored; raw MinIO credentials never exposed to frontend |
| Reliability | Failed jobs preserve a human-readable error and can be retried |
| Performance | CPU fallback required; target at least 5 sampled frames/sec in CV worker |
| Reproducibility | Docker Compose starts the full stack from documented setup steps |
| Observability | Health endpoint reports core service status; workers log progress and failures |
| Maintainability | Markdown specs, ADRs, and schemas stay synchronized with implementation |
| Accessibility | UI controls must be keyboard reachable and errors must be text-visible, not color-only |

---

## 7. MVP Acceptance Criteria

The MVP is acceptable when all of the following are true:

- A new user can follow `docs/QUICKSTART.md` and start the platform locally.
- A user can upload a supported video and see a job record in the dashboard.
- A user can calibrate the court from the first frame and receive visible quality feedback.
- The CV worker produces telemetry that validates against schema version `1.0`.
- The analytics worker produces summary metrics that validate against schema version `1.0`.
- Heatmaps and player trails render from real telemetry, not only mock data.
- A user can label players, assign teams, flag bad tracks, annotate shots, and recompute analytics.
- A local Ollama report can be generated from the analytics summary without invented statistics.
- All documented release checks in `docs/TESTING_STRATEGY.md` pass.
- `INPUTS_NEEDED.md` is confirmed by the owner.

---

## 8. Out of Scope for MVP

- Automatic court calibration.
- Production-grade ball possession inference.
- Fully automatic shot detection.
- Live stream ingestion.
- Multi-camera fusion.
- Cloud-hosted multi-tenant deployment.
- Authentication and role-based access control.
- Native mobile applications.

---

## 9. Owner Review Gates

| Gate | When | Owner confirms |
|---|---|---|
| Gate 0 | End of Phase 00 | Inputs, assumptions, and sample data path |
| Gate 1 | End of Phase 03 | Dashboard layout and mock analytics are useful |
| Gate 2 | End of Phase 06 | Calibration UX is understandable and accurate enough |
| Gate 3 | End of Phase 09 | Analytics metrics are useful and explainable |
| Gate 4 | End of Phase 11 | Annotation workflow is sufficient for correction/review |
| Gate 5 | End of Phase 12 | Quickstart and release package are ready |

---

## 10. Requirement Traceability

| Requirement Area | Primary Phase(s) | Reference Docs |
|---|---|---|
| Product scope | 00, 12 | `PROJECT_PLAN.md`, `INPUTS_NEEDED.md` |
| Upload / jobs | 02, 04 | `docs/API_CONTRACT.md`, `docs/DATA_SCHEMAS.md` |
| Calibration | 04, 06 | `docs/UX_FLOWS.md`, `docs/DATA_SCHEMAS.md` |
| CV telemetry | 05, 07 | `ARCHITECTURE.md`, `docs/DATA_SCHEMAS.md` |
| Analytics / heatmaps | 08, 09 | `docs/DATA_SCHEMAS.md`, `docs/API_CONTRACT.md` |
| LLM reports | 10 | `docs/SECURITY_PRIVACY.md`, `docs/DATA_SCHEMAS.md` |
| Annotation | 11 | `docs/DATA_SCHEMAS.md`, `docs/UX_FLOWS.md` |
| Release | 12 | `docs/TESTING_STRATEGY.md`, `CONTRIBUTING.md` |

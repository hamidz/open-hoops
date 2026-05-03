# Phase 04 — Video Upload Workflow

> **Goal:** Implement the end-to-end video upload flow: user selects a video file, it uploads to MinIO, a job record is created, and the job is queued for processing.

---

## Status: 🟡 In Progress

---

## Prerequisites

- Phase 02 complete (infrastructure running).
- Phase 03 complete (dashboard exists — add upload UI to it).

---

## Agent Instructions

Read `ARCHITECTURE.md` for the job record schema and data flow before starting.

Your job is to implement the complete upload → job creation → queue pipeline. Do not implement CV processing — the queued job will be picked up in Phase 05.

---

## Upload Workflow (Step by Step)

```
User selects video file in UI
        ↓
Frontend: validate file type + size
        ↓
Frontend: POST /api/jobs/upload (multipart form)
        ↓
API: validate video metadata
        ↓
API: stream video to MinIO (videos bucket)
        ↓
API: create Job record in PostgreSQL (status: queued)
        ↓
API: enqueue job_id in Redis queue
        ↓
API: return { job_id, status: "queued" }
        ↓
Frontend: redirect to /dashboard/jobs/{job_id}
        ↓
Frontend: poll GET /api/jobs/{job_id} every 3 seconds
        ↓
Frontend: display job status updates in real time
```

---

## Tasks

### API — Upload Endpoint

- [ ] `POST /api/jobs/upload` — multipart file upload endpoint:
  - Accepts: `video` (file), `label` (optional string), `sport` (optional, default: `basketball`)
  - Validates file extension: `.mp4`, `.mov` only.
  - Validates file size: reject if > 4 GB (configurable via env var).
  - Streams file to MinIO `videos` bucket using UUID-based key.
  - Creates `Job` record in PostgreSQL with status `queued`.
  - **Extracts frame 0 from the video and saves it to `artifacts/{job_id}/frame_0.jpg` in MinIO.** This makes the first frame immediately available for court calibration (Phase 06) without waiting for the CV worker.
  - Enqueues `job_id` in Redis.
  - Returns `{ job_id, status, created_at }`.

### API — Job Management Endpoints

- [ ] `GET /api/jobs/{job_id}` — return full job record including status, `progress_pct`, urls, timestamps, and `error_message`.
- [ ] `GET /api/jobs` — list jobs, ordered by `created_at` descending, with pagination.
- [ ] `POST /api/jobs/{job_id}/retry` — re-queue a `failed` job:
  - Resets status to `queued`, clears `error_message`, and enqueues `job_id`.
  - Returns `{ job_id, status: "queued" }`.
  - Returns 409 if job is not in `failed` status.
- [ ] `DELETE /api/jobs/{job_id}` — delete a job and all associated MinIO artifacts:
  - Deletes job record from PostgreSQL.
  - Deletes all objects under `{job_id}/` prefix in `videos`, `telemetry`, and `artifacts` buckets.
  - Returns 204 No Content.

### Video Metadata

On upload, extract and store:

- [ ] File size (bytes)
- [ ] Original filename
- [ ] Upload timestamp
- [ ] Sport label (default: `basketball`)
- [ ] Optional user-provided label

### Frontend — Upload UI

- [ ] Upload page at `/upload` (or modal/drawer from dashboard).
- [ ] Drag-and-drop file input (fallback: file picker button).
- [ ] File type validation in browser before upload (`.mp4`, `.mov`).
- [ ] Upload progress bar (using `XMLHttpRequest` or `axios` with `onUploadProgress`).
- [ ] Error state: clear message for invalid file type, size too large, or server error.
- [ ] On success: redirect to `/dashboard/jobs/{job_id}` with status "Queued".
- [ ] **Note:** Single-POST upload only for MVP. For files > 1 GB on slow connections, upload may time out. Chunked/resumable upload is deferred post-MVP (see `docs/ADR.md` ADR-011).

### Frontend — Job Status Polling

- [ ] Job detail page at `/dashboard/jobs/[job_id]`.
- [ ] Poll `GET /api/jobs/{job_id}` every 3 seconds while status is `queued` or `processing`.
- [ ] Display status badge (Queued, Processing, Calibration Needed, Complete, Failed).
- [ ] When status is `processing`: display a progress bar driven by `progress_pct`.
- [ ] **When status is `calibration_needed`: display a "Calibrate Now" button linking to `/dashboard/jobs/{job_id}/calibrate`.** Do not auto-redirect — user should see the instruction.
- [ ] When status is `failed`: display `error_message` and a "Retry" button that calls `POST /api/jobs/{job_id}/retry`.
- [ ] Display video metadata (label, filename, upload time, file size).
- [ ] Display a "Delete Job" button (with confirmation dialog) for all non-`processing` statuses.

### Error Handling

- [ ] API returns structured error responses: `{ error: string, detail: string }`.
- [ ] Frontend displays meaningful error messages (not raw HTTP status codes).
- [ ] If MinIO upload fails, job is not created and error is returned.
- [ ] If Redis enqueue fails, job is marked as `failed` with reason stored.

### Tests

- [ ] Unit test: file validation logic (extension, size).
- [ ] Unit test: MinIO upload (mock MinIO client).
- [ ] Unit test: frame 0 extraction on upload.
- [ ] Unit test: retry endpoint transitions `failed` → `queued`.
- [ ] Unit test: delete endpoint removes job record and MinIO objects.
- [ ] Integration test: full upload → job created → job queued flow.

---

## Environment Variables

Add to `.env.example`:

```
MAX_UPLOAD_SIZE_GB=4
MINIO_VIDEOS_BUCKET=videos
FRAME_ZERO_EXTRACTION=true
```

---

## Outputs

- `apps/api/app/routers/jobs.py` — upload, status, retry, and delete endpoints.
- `apps/api/app/services/storage.py` — MinIO upload and delete service.
- `apps/api/app/services/queue.py` — Redis enqueue service.
- `apps/api/app/services/frame_extractor.py` — frame 0 extraction on upload.
- `apps/web/src/app/upload/` — upload page.
- `apps/web/src/app/dashboard/jobs/[job_id]/` — job detail page with polling, progress bar, Calibrate Now CTA, Retry button, and Delete button.

---

## Definition of Done

- [ ] User can upload a `.mp4` file via the UI.
- [ ] File appears in MinIO `videos` bucket.
- [ ] Job record created in PostgreSQL with status `queued`.
- [ ] Job detail page shows correct status and metadata.
- [ ] All unit and integration tests pass.
- [ ] Phase status updated in `AGENTIC_EXECUTION_PLAN.md`.

---

## Completion Note

### Progress Note — 2026-05-03

The browser upload flow works through both native dev and Docker Compose: `.mp4` selection, progress upload, redirect to job detail, and generated analytics display. The implementation currently uses local JSON/filesystem storage and mock analytics; remaining Phase 04 scope includes MinIO persistence, PostgreSQL job records, Redis/ARQ enqueue, real frame-zero extraction, and retry UI wiring.

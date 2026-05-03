# Phase 05 — CV Engine MVP

> **Goal:** Implement the computer vision pipeline that processes a queued video job: extract frames, detect players and ball, track them across frames, and produce a telemetry JSON file.

---

## Status: 🔲 Pending

---

## Prerequisites

- Phase 04 complete (video upload and job queue working).
- Phase 06 may run concurrently — court calibration is applied to telemetry in this phase but the calibration UI is built in Phase 06. For Phase 05 testing, use a pre-computed hardcoded homography matrix.

---

## Agent Instructions

Read `ARCHITECTURE.md` for the detection schema and CV worker responsibilities.
Read `docs/STACK.md` for CV library choices (YOLO, ByteTrack).
Read `INPUTS_NEEDED.md` for confirmed hardware and video format assumptions.

Your job is to implement `services/cv_worker`. The worker picks up a job from the Redis queue, processes the video, and saves telemetry output.

Do not implement analytics or LLM report generation in this phase.

---

## CV Pipeline (Step by Step)

```
Pick up job_id from Redis queue
        ↓
Update job status → "processing"
        ↓
Download video from MinIO
        ↓
Extract frames (configurable: every Nth frame for speed)
        ↓
For each frame batch:
    Run YOLO detection (persons + sports ball)
    Run ByteTrack tracker → assign track_ids
    Apply homography (if calibration exists; else skip court_xy)
    Append frame detections to telemetry list
        ↓
Write telemetry JSON to MinIO (telemetry bucket)
        ↓
Update job record: telemetry_url, status → "complete" (or "calibration_needed")
        ↓
Enqueue analytics job (Phase 09)
```

---

## Tasks

### Worker Infrastructure

- [ ] Implement `services/cv_worker/worker.py`:
  - Connects to Redis queue on startup.
  - Polls for jobs continuously.
  - Handles graceful shutdown on SIGTERM.
- [ ] Job processing is idempotent — re-processing a job overwrites previous output.
- [ ] Worker updates job status at each pipeline step.

### Frame Extraction

- [ ] Implement `services/cv_worker/pipeline/extractor.py`:
  - Use `cv2.VideoCapture` to read the video.
  - Support configurable frame sampling rate (default: every 3rd frame = 10 fps effective).
  - Extract video metadata: total frames, fps, resolution, duration.
  - Store metadata in job record.

### Detection

- [ ] Implement `services/cv_worker/pipeline/detector.py`:
  - Load `YOLOv8n` by default. Model path configurable via env var.
  - Detect class 0 (person) and class 32 (sports ball) only.
  - Confidence threshold: 0.4 (configurable via env var).
  - Return bounding boxes in `[x1, y1, x2, y2]` pixel format.

### Tracking

- [ ] Implement `services/cv_worker/pipeline/tracker.py`:
  - Use ByteTrack via Ultralytics `.track()` method.
  - Assign stable `track_id` per object across frames.
  - Handle track loss/reacquisition gracefully.

### Homography Application

- [ ] Implement `services/cv_worker/pipeline/homography.py`:
  - Accept homography matrix (from job calibration record).
  - Transform `bbox` center point (bottom-center, feet position) from pixel to court coordinates (meters).
  - If no calibration exists: set `court_xy` to `null` and continue.

### Telemetry Output

- [ ] Implement telemetry JSON writer per schema in `ARCHITECTURE.md`:

```json
{
  "job_id": "uuid",
  "video_metadata": {
    "fps": 30,
    "total_frames": 54000,
    "resolution": [1920, 1080],
    "duration_seconds": 1800,
    "sampled_every_n_frames": 3
  },
  "frames": [
    {
      "frame": 0,
      "timestamp_ms": 0,
      "detections": [
        {
          "track_id": 1,
          "class": "person",
          "bbox_px": [100, 200, 150, 350],
          "confidence": 0.91,
          "court_xy": [4.2, 7.8]
        }
      ]
    }
  ]
}
```

- [ ] Write telemetry JSON to MinIO `telemetry` bucket as `{job_id}/telemetry.json`.
- [ ] Write a separate `{job_id}/video_metadata.json` for fast access.

### Error Handling

- [ ] If YOLO model fails to load: mark job as `failed`, log error, do not crash worker.
- [ ] If video file is corrupt or unreadable: mark job as `failed`, log error.
- [ ] If MinIO write fails: retry 3 times with exponential backoff, then fail.
- [ ] Worker continues to process next job after a failed job — never hangs.

### Performance

- [ ] Frame processing: target ≥ 5 frames/second on CPU (no GPU).
- [ ] Memory: release frame tensors after detection to avoid OOM.
- [ ] Log processing rate every 100 frames.

### Configuration (via env vars)

```
YOLO_MODEL=yolov8n.pt
YOLO_CONFIDENCE_THRESHOLD=0.4
FRAME_SAMPLE_RATE=3
CV_WORKER_CONCURRENCY=1
```

### Tests

- [ ] Unit test: frame extraction from a short synthetic video.
- [ ] Unit test: detection output format validation.
- [ ] Unit test: homography transform (known input → expected output).
- [ ] Unit test: telemetry JSON schema validation.
- [ ] Integration test: full pipeline on a 10-second test clip.

---

## Outputs

- `services/cv_worker/worker.py` — main worker loop.
- `services/cv_worker/pipeline/extractor.py`
- `services/cv_worker/pipeline/detector.py`
- `services/cv_worker/pipeline/tracker.py`
- `services/cv_worker/pipeline/homography.py`
- `services/cv_worker/pipeline/telemetry_writer.py`
- Telemetry JSON in MinIO for a processed test video.
- Updated job record with `telemetry_url` and status `complete`.

---

## Definition of Done

- [ ] Worker processes a queued video job end-to-end without crashing.
- [ ] Telemetry JSON written to MinIO and matches schema.
- [ ] Job status updates correctly through all pipeline stages.
- [ ] All unit and integration tests pass.
- [ ] Phase status updated in `AGENTIC_EXECUTION_PLAN.md`.

---

## Completion Note

> _Agent: add completion date and summary here when done._

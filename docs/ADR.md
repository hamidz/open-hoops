# Architecture Decision Records — Open Hoops

> A log of significant technical decisions made during the design of this project.
> Each record captures what was decided, why, and what alternatives were considered.

---

## ADR-001 — Local-First Architecture

**Date:** 2025-05  
**Status:** Accepted

### Decision

The platform is designed to run entirely on a local machine. No cloud services are required for MVP functionality.

### Rationale

- User video data is sensitive (private games, minors may be visible).
- Cloud services add cost, latency, and vendor lock-in.
- The target user is a coach or analyst with a modern laptop, not a cloud operator.
- Local-first does not prevent future cloud deployment — it establishes a stronger baseline.

### Alternatives Considered

- AWS S3 + Lambda for processing: rejected — adds cost and requires internet.
- Firebase: rejected — proprietary, cloud-only.

---

## ADR-002 — MinIO for Object Storage

**Date:** 2025-05  
**Status:** Accepted

### Decision

Use MinIO as local object storage for videos, telemetry files, and generated artifacts.

### Rationale

- MinIO is S3-compatible. Any code written against MinIO works against AWS S3 unchanged.
- Provides a migration path to cloud without code changes.
- Docker image available; runs in Docker Compose with no external dependency.

### Alternatives Considered

- Local filesystem: simpler but not scalable, no URL-based access pattern.
- AWS S3: rejected — cloud dependency violates ADR-001.

---

## ADR-003 — FastAPI Over Django REST Framework

**Date:** 2025-05  
**Status:** Accepted

### Decision

Use FastAPI as the API framework, not Django REST Framework (DRF).

### Rationale

- FastAPI is async-native, which is important for non-blocking job status polling.
- FastAPI auto-generates OpenAPI docs from type hints — reduces documentation burden.
- Pydantic integration is first-class — same models used for validation and serialization.
- Lighter weight than Django — less ORM magic, more explicit control.

### Alternatives Considered

- Flask: simpler but no async, no built-in OpenAPI.
- DRF: mature but heavy for this project's needs.

---

## ADR-004 — Ultralytics YOLO for Detection

**Date:** 2025-05  
**Status:** Accepted

### Decision

Use Ultralytics YOLO (YOLOv8+) for player and ball detection.

### Rationale

- Best-in-class real-time detection with excellent Python API.
- Pre-trained on COCO which includes `person` (class 0) and `sports ball` (class 32).
- Includes ByteTrack out of the box — no separate integration required.
- Active development, large community, well-documented.

### Alternatives Considered

- Detectron2: more powerful but far heavier and harder to deploy.
- MediaPipe: good for pose estimation but not ideal for sports tracking.
- Custom-trained model: not required for MVP — COCO person detection is sufficient.

---

## ADR-005 — Ollama for Local LLM

**Date:** 2025-05  
**Status:** Accepted

### Decision

Use Ollama to serve local LLMs for coaching report generation.

### Rationale

- Zero cloud dependency — all LLM inference runs locally.
- OpenAI-compatible API — easy to swap models without code changes.
- Supports Llama, Mistral, Qwen, and many other open models.
- Simple installation, Docker-compatible.

### Alternatives Considered

- OpenAI API: rejected — requires internet and API key; violates ADR-001.
- Hugging Face Transformers direct: possible but more complex to serve locally.
- LM Studio: good UI but no programmatic API suitable for automation.

---

## ADR-006 — Markdown as Source of Truth

**Date:** 2025-05  
**Status:** Accepted

### Decision

All design decisions, phase plans, and specifications live in Markdown files. Code must conform to Markdown specs, not the other way around.

### Rationale

- This is an agentic project. Agents need explicit, unambiguous instructions.
- Markdown is version-controlled alongside code — decisions are traceable.
- Reduces the "big design up front" anti-pattern — each phase doc is scoped and bounded.
- Human owner can review and confirm specs without reading code.

### Alternatives Considered

- GitHub Issues: fragmented, no enforced structure.
- Notion / Confluence: external tool, not version-controlled with code.
- In-code comments: too granular, not accessible to non-technical owners.

---

## ADR-007 — Mock Data Before Real CV

**Date:** 2025-05  
**Status:** Accepted

### Decision

Phase 03 builds a fully functional dashboard using mock/synthetic telemetry data before any real computer vision is implemented.

### Rationale

- Decouples frontend development from CV complexity.
- Allows the owner to validate the UX and analytics output format early.
- Reduces the risk of building a CV pipeline for visualizations that don't meet the owner's needs.
- Mock data can become the test fixture for all downstream phases.

### Alternatives Considered

- Build CV first, then dashboard: riskier — if CV output format changes, dashboard changes too.
- Simultaneous development: harder to coordinate in an agentic solo project.

---

## ADR-008 — Manual Court Calibration for MVP

**Date:** 2025-05  
**Status:** Accepted

### Decision

Court calibration in the MVP requires the user to manually click 4+ known points on the first frame of the video to define the homography transform. Automatic court line detection is a post-MVP feature.

### Rationale

- Automatic court line detection (Hough transforms, semantic segmentation) is fragile — it depends on camera angle, lighting, and court marking quality.
- Manual calibration is reliable, predictable, and gives the user control.
- Once calibrated, the homography persists for the entire video — low user burden.
- "Manual workflow before automation" is a stated project principle.

### Alternatives Considered

- Automatic calibration: post-MVP goal. More research needed.
- Template matching: brittle for non-standard court angles.

---

## ADR-009 — ByteTrack as Default Tracker

**Date:** 2025-05  
**Status:** Provisional (confirm in Phase 05)

### Decision

Default to ByteTrack for multi-object tracking. Revisit BoT-SORT in Phase 05 based on test results.

### Rationale

- ByteTrack is included in Ultralytics — zero additional integration.
- Performs well on crowded sports scenes.
- Lower latency than BoT-SORT, which is important for CPU-only scenarios.

### Alternatives Considered

- BoT-SORT: better camera motion compensation, but more compute-heavy. Suitable if camera pan/tilt support is added post-MVP.
- DeepSORT: older, less accurate than ByteTrack on benchmarks.

---

## How To Add a New ADR

Copy this template:

```markdown
## ADR-XXX — [Short Title]

**Date:** YYYY-MM  
**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-XXX

### Decision

[One paragraph: what was decided.]

### Rationale

[Why this decision was made.]

### Alternatives Considered

- [Alternative]: [why rejected or deferred].
```

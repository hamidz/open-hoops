# Inputs Needed — Open Hoops

> Before implementation begins, the project owner must confirm or decide the items below.
> Agents should not start Phase 01 until this file has been reviewed and marked complete.

---

## Status

- [ ] **INCOMPLETE** — review and fill in all sections, then change status to `CONFIRMED`.

---

## 1. Video Input Assumptions

| Question | Default Assumption | Owner Confirmed? |
|---|---|---|
| Camera angle | Fixed sideline, full-court view | [ ] |
| Camera motion | Static (no pan/tilt/zoom) | [ ] |
| Video resolution | 1080p minimum | [ ] |
| Frame rate | 30 fps minimum | [ ] |
| File formats accepted | MP4, MOV | [ ] |
| Video duration range | 5 min – 2 hrs | [ ] |
| Single camera only for MVP | Yes | [ ] |

**Owner notes:**

> _Add any clarifications here._

---

## 2. Court Assumptions

| Question | Default Assumption | Owner Confirmed? |
|---|---|---|
| Court type | Full NBA/FIBA half-court or full-court | [ ] |
| Court markings visible | Yes, standard painted lines | [ ] |
| Calibration method | Manual point-click (4 corners minimum) | [ ] |
| Court dimensions stored | Standard NBA (28.65 m × 15.24 m) | [ ] |

**Owner notes:**

> _Add any clarifications here._

---

## 3. Players and Teams

| Question | Default Assumption | Owner Confirmed? |
|---|---|---|
| Number of players tracked | Up to 10 (5v5) | [ ] |
| Player identity method for MVP | Jersey color clustering, manual labeling | [ ] |
| Team jersey colors needed up front | No — assigned post-detection | [ ] |
| Ball tracking required for MVP | Best-effort, graceful failure acceptable | [ ] |

**Owner notes:**

> _Add any clarifications here._

---

## 4. Hardware Target

| Question | Default Assumption | Owner Confirmed? |
|---|---|---|
| Development machine OS | macOS or Linux | [ ] |
| Minimum RAM | 16 GB | [ ] |
| GPU available | Optional — CPU fallback required | [ ] |
| GPU (if present) | NVIDIA CUDA or Apple MPS | [ ] |
| Target deployment | Local self-hosted, Docker Compose | [ ] |

**Owner notes:**

> _Add any clarifications here._

---

## 5. Output Requirements

| Question | Default Assumption | Owner Confirmed? |
|---|---|---|
| Primary output format | Web dashboard + JSON export | [ ] |
| PDF report export for MVP | No | [ ] |
| LLM report required for MVP | Yes — local Ollama | [ ] |
| LLM model preference | Llama 3 / Mistral 7B class | [ ] |
| Sharing/export for MVP | Download JSON + PNG heatmaps | [ ] |

**Owner notes:**

> _Add any clarifications here._

---

## 6. Sample Data

| Question | Default Assumption | Owner Confirmed? |
|---|---|---|
| Sample video available for testing | TBD | [ ] |
| If no real video, use synthetic mock data | Yes | [ ] |
| Sample video resolution confirmed | TBD | [ ] |

**Owner notes / sample video link:**

> _Provide a link or description of available test video here._

---

## 7. Open Questions

List any items that are still unresolved or require more research:

1. _Which YOLO model weight to default to (YOLOv8n vs YOLOv8m)?_
2. _Which tracker to default to (ByteTrack vs BoT-SORT)?_
3. _Is Ollama pre-installed on the target dev machine?_
4. _Will real court line detection be attempted in MVP or always manual calibration?_

---

## Sign-Off

When all sections are confirmed, update the status at the top of this file to:

```
- [x] **CONFIRMED** — all inputs reviewed by owner on YYYY-MM-DD.
```

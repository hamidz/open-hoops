# Inputs Needed — Open Hoops

> Before implementation begins, the project owner must confirm or decide the items below.
> Agents should not start Phase 01 until this file has been reviewed and marked complete.

---

## Status

- [x] **CONFIRMED** — all inputs reviewed and formalized by owner on 2026-05-03. See notes and open-question resolutions in each section.

---

## 1. Video Input Assumptions

| Question | Default Assumption | Owner Confirmed? |
|---|---|---|
| Camera angle | Fixed sideline, full-court view | ✅ 4K phone, fixed sideline |
| Camera motion | Static (no pan/tilt/zoom) | ✅ Static confirmed |
| Video resolution | 1080p minimum | ✅ 4K (3840×2160) primary; 1080p fallback |
| Frame rate | 30 fps minimum | ✅ 30 fps (phone default) |
| File formats accepted | MP4, MOV | ✅ MP4 and MOV |
| Video duration range | 5 min – 2 hrs | ✅ Confirmed |
| Single camera only for MVP | Yes | ✅ Yes |

**Owner notes:**

> Primary camera is a 4K smartphone (fixed sideline mount). 4K resolution creates larger file sizes — the 4 GB upload cap is appropriate for phone-captured 4K clips of typical game segments. The CV worker will downsample frames during processing for performance.

---

## 2. Court Assumptions

| Question | Default Assumption | Owner Confirmed? |
|---|---|---|
| Court type | Full NBA/FIBA half-court or full-court | ✅ Both full-court and half-court supported; user selects per job |
| Court markings visible | Yes, standard painted lines | ✅ Standard painted lines confirmed |
| Calibration method | Manual point-click (4 corners minimum) | ✅ Manual for MVP (see ADR-008) |
| Court dimensions stored | Standard NBA (28.65 m × 15.24 m) or FIBA (28 m × 15 m) | ✅ Both NBA and FIBA supported; user selects at calibration time |

**Owner notes:**

> Court selection (NBA vs FIBA) will be a dropdown in the calibration UI. NBA is the default. FIBA dimensions differ slightly — the zone boundaries in `docs/DATA_SCHEMAS.md` will use the selected standard.

---

## 3. Players and Teams

| Question | Default Assumption | Owner Confirmed? |
|---|---|---|
| Number of players tracked | Up to 12 (5v5 game or practice drills) | ✅ Up to 12 confirmed (practice sessions may have more) |
| Player identity method for MVP | Jersey color clustering, manual labeling | ✅ Confirmed |
| Team jersey colors needed up front | No — assigned post-detection | ✅ Confirmed |
| Ball tracking required for MVP | Best-effort, graceful failure acceptable | ✅ Confirmed |

**Owner notes:**

> Practice sessions may involve more than 10 players. The tracker should not hard-cap track IDs — track up to 12 active tracks and let the user label/assign teams afterward.

---

## 4. Hardware Target

| Question | Default Assumption | Owner Confirmed? |
|---|---|---|
| Development machine OS | Windows 11 + WSL2 (Ubuntu 22.04) | ✅ Windows confirmed; WSL2 required for ROCm GPU support |
| Minimum RAM | 16 GB | ✅ 64 GB confirmed |
| GPU available | AMD Radeon RX 9700 AI (RDNA3, 32 GB VRAM) | ✅ AMD confirmed — see GPU notes below |
| GPU acceleration method | AMD ROCm via WSL2 (not CUDA) | ✅ CUDA does not apply (AMD GPU) |
| Target deployment | Local self-hosted, Docker Compose in WSL2 | ✅ Initially local |
| Available disk space | 50 GB minimum recommended | ✅ 500 GB confirmed |
| nvidia-container-toolkit | Not applicable (AMD GPU) | ✅ N/A |

### AMD GPU and ROCm Notes

> ⚠️ **Critical hardware note:** The confirmed GPU is an **AMD RDNA3** card. AMD GPUs use **ROCm** (Radeon Open Compute), not NVIDIA CUDA. ROCm requires:
> - Linux kernel driver (not available natively on Windows)
> - **WSL2 on Windows** with the `amdgpu` kernel driver loaded
> - PyTorch built with ROCm support (`torch` ROCm wheels from PyTorch.org)
>
> **Implication:** All Docker-based services requiring GPU acceleration must run inside WSL2. The Docker Desktop WSL2 backend is used. The `docker-compose.gpu.yml` override targets ROCm, not NVIDIA CUDA.
>
> **Processing time estimates with ROCm on AMD RX 9700 AI (RDNA3):**

| Video Duration | Estimated ROCm Processing Time |
|---|---|
| 10 minutes | ~3–8 minutes |
| 1 hour | ~18–48 minutes |
| 2 hours | ~36–96 minutes |

> ROCm performance varies by driver maturity. These are estimates. CPU fallback always available.

### Processing Time Expectations (CPU Fallback)

At the default CPU settings (YOLOv8n, 1x concurrency, every 3rd frame), processing is approximately **3–5× slower than real time**. Example estimates:

| Video Duration | Estimated CPU Processing Time |
|---|---|
| 10 minutes | ~30–50 minutes |
| 1 hour | ~3–5 hours |
| 2 hours | ~6–10 hours |

**Owner notes:**

> Development will use Docker Desktop with the WSL2 backend. The `infra/docker-compose.gpu.yml` override is the ROCm path. CPU fallback works without any GPU setup.

---

## 5. Output Requirements

| Question | Default Assumption | Owner Confirmed? |
|---|---|---|
| Primary output format | Web dashboard + JSON export | ✅ Confirmed |
| PDF report export for MVP | No | ✅ Post-MVP |
| LLM report required for MVP | Yes — local Ollama | ✅ Confirmed |
| LLM model preference | Llama 3.1 8B / Mistral 7B class (quantized) | ✅ Best model supported by hardware |
| Sharing/export for MVP | Download JSON + PNG heatmaps | ✅ Confirmed |

**Owner notes:**

> Use the largest model that runs comfortably on the AMD R9700 AI (32 GB VRAM). With ROCm, Llama 3.1 70B Q4 may be feasible. Default to `llama3.1:8b` for reliability; allow override via env var.

---

## 6. Sample Data

| Question | Default Assumption | Owner Confirmed? |
|---|---|---|
| Sample video available for testing | Synthetic short clip generated by `scripts/generate_mock_data.py` | ✅ Synthetic data acceptable for initial phases |
| If no real video, use synthetic mock data | Yes — `scripts/generate_mock_data.py` | ✅ Confirmed |
| Sample video resolution confirmed | 1080p synthetic clip | ✅ Confirmed for testing |

**Owner notes:**

> A synthetic 10-second 1080p video clip will be generated for CV pipeline testing (Phase 05). Real 4K game footage will be used for validation once Phase 06 calibration is working.

---

## 7. Open Questions

All questions resolved as follows:

1. **YOLO model weight:** Use `YOLOv8m` (medium) by default with ROCm GPU. Fall back to `YOLOv8n` (nano) on CPU. The AMD R9700 AI's 32 GB VRAM can comfortably run YOLOv8m in real-time. Override via `YOLO_MODEL` env var.

2. **Tracker default:** **ByteTrack** (ADR-009). Evaluate BoT-SORT during Phase 05 and update ADR-009 if results favor it.

3. **Ollama pre-installed:** No — Ollama will run as a Docker container in WSL2 (`ollama/ollama` image). Models are downloaded on first use via `docker exec ollama ollama pull llama3.1:8b`.

4. **Court line detection:** Manual calibration for MVP (ADR-008). Automatic detection is post-MVP.

5. **Chunked/resumable upload:** Single-POST upload acceptable for MVP on a local network (ADR-011). 4 GB cap is appropriate for 4K phone footage.

6. **GPU acceleration:** AMD ROCm via WSL2. See Section 4 above. NVIDIA CUDA does not apply.

---

## Sign-Off

When all sections are confirmed, update the status at the top of this file to:

```
- [x] **CONFIRMED** — all inputs reviewed by owner on YYYY-MM-DD.
```

**Status: CONFIRMED — 2026-05-03. All inputs formalized. AMD ROCm / WSL2 path confirmed. Phase 00 complete.**

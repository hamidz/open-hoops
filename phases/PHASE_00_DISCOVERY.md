# Phase 00 — Discovery

> **Goal:** Confirm all project inputs and constraints before any implementation begins.
> No code is written in this phase.

---

## Status: ✅ Done — 2026-05-03

---

## Prerequisites

- None. This is the first phase.

## Agent Instructions

Do not write code in this phase. Your job is to:

1. Read `INPUTS_NEEDED.md` and identify any items that are not yet confirmed.
2. Prepare a short list of open questions for the owner.
3. Update `INPUTS_NEEDED.md` with any answers provided by the owner.
4. Mark the phase complete when all items in `INPUTS_NEEDED.md` are confirmed.

---

## Tasks

- [x] Read `INPUTS_NEEDED.md` in full.
- [x] Identify all unchecked items.
- [x] Report open questions to the project owner.
- [x] Owner confirms: video input assumptions.
- [x] Owner confirms: court assumptions.
- [x] Owner confirms: player/team tracking assumptions.
- [x] Owner confirms: hardware target.
- [x] Owner confirms: output requirements.
- [x] Owner confirms: sample data availability.
- [x] Owner resolves all open questions in `INPUTS_NEEDED.md` Section 7.
- [x] `INPUTS_NEEDED.md` status updated to `CONFIRMED`.
- [x] `AGENTIC_EXECUTION_PLAN.md` Phase 00 status updated to `✅ Done`.

---

## Outputs

- `INPUTS_NEEDED.md` — fully confirmed.

---

## Definition of Done

- All checkboxes in `INPUTS_NEEDED.md` are ticked.
- Owner has signed off in the sign-off section of `INPUTS_NEEDED.md`.

---

## Completion Note

> Completed 2026-05-03. All inputs in `INPUTS_NEEDED.md` confirmed by owner. Key resolutions:
> - Hardware: AMD Radeon RX 9700 AI (RDNA3, 32 GB VRAM) on Windows + WSL2. ROCm acceleration path.
> - Camera: 4K smartphone, fixed sideline.
> - Court: Both NBA and FIBA supported; user selects at calibration time.
> - Players: Up to 12 tracked; jersey color clustering + manual labeling.
> - YOLO: YOLOv8m default with ROCm; YOLOv8n CPU fallback.
> - Tracker: ByteTrack default (evaluate BoT-SORT in Phase 05).
> - LLM: Ollama via Docker in WSL2, `llama3.1:8b` default.
> - Upload: Single-POST, 4 GB cap acceptable for local MVP.

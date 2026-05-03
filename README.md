# Open Hoops

> Open-source, local-first basketball video analytics platform.

---

## Project Status

Runnable first-workflow MVP scaffold.

The repository now includes a Dockerized FastAPI backend, Next.js frontend, shared types, worker stubs, and a local upload-to-stats workflow. The broader CV, calibration, heatmap, annotation, and LLM phases remain guided by the Markdown phase plans.

## Mission

Democratize pro-style basketball analytics using open-source computer vision, local processing, and agent-assisted execution.

## MVP Goal

Upload a fixed sideline basketball video, manually calibrate the court, process the video, and generate:

- player and team movement heatmaps
- court-position telemetry
- basic analytics summaries
- local LLM coaching reports

## Principles

- Open-source first
- Local-first where possible
- Markdown before code
- One phase at a time
- Mock data before real CV
- Manual workflow before automation
- Useful coaching output over flashy demos

## Start Here

- [PROJECT_PLAN.md](./PROJECT_PLAN.md)
- [docs/PRODUCT_REQUIREMENTS.md](./docs/PRODUCT_REQUIREMENTS.md)
- [docs/PLANNING_GAP_REVIEW.md](./docs/PLANNING_GAP_REVIEW.md)
- [AGENTIC_EXECUTION_PLAN.md](./AGENTIC_EXECUTION_PLAN.md)
- [INPUTS_NEEDED.md](./INPUTS_NEEDED.md)
- [CONTRIBUTING.md](./CONTRIBUTING.md)
- [docs/README.md](./docs/README.md)

## Repository Intent

This repo contains both the planning artifacts and a minimal runnable implementation. From a fresh clone, configure `.env`, run setup, open the web app, upload an `.mp4`/`.mov`, and view generated first-pass stats.

The implementation intentionally uses generated/mock analytics for the first workflow; production CV processing remains in the later phase plans.

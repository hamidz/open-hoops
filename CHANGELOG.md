# Changelog — Open Hoops

All notable changes to Open Hoops will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Project planning documentation (Phases 00–12)
- Architecture, ADR, Glossary, Stack, and Data Schema reference docs
- Product requirements, API contract, UX flows, security/privacy, testing strategy, and planning gap review docs
- `CONTRIBUTING.md` contributor guide
- `.github/workflows/copilot-setup-steps.yml` — Copilot agent environment setup

---

<!-- New releases go above this line in the format below:

## [0.2.0] - YYYY-MM-DD

### Added
- ...

### Changed
- ...

### Fixed
- ...

### Removed
- ...

-->

## [0.1.0-mvp] - TBD

_First self-hosted MVP release. Covers Phases 01–12._

### Added
- Full monorepo scaffold (Next.js frontend, FastAPI backend, CV/analytics/LLM workers)
- Docker Compose local dev stack (PostgreSQL, Redis, MinIO, Ollama)
- Video upload workflow with frame-zero extraction and job queue
- Manual court calibration with homography transform
- CV pipeline: YOLO player/ball detection, ByteTrack tracking, telemetry export
- Telemetry schema v1.0 with Pydantic validation and auto-generated TypeScript types
- Player movement heatmaps (Gaussian KDE) with timeline filter
- Basic analytics: distance, speed, court coverage, zone distribution, team spacing
- Annotation workflow: player labeling, team assignment, shot annotation
- Local LLM coaching reports via Ollama (llama3)
- Self-hosted release: production Docker Compose, quickstart docs, setup scripts

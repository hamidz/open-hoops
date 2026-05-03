# Documentation Index — Open Hoops

> Central index for all project documentation.

---

## Core Documents

| Document | Purpose |
|---|---|
| [README.md](../README.md) | Project overview and mission |
| [PROJECT_PLAN.md](../PROJECT_PLAN.md) | Full project vision and phase list |
| [ARCHITECTURE.md](../ARCHITECTURE.md) | System architecture and data schemas |
| [AGENTIC_EXECUTION_PLAN.md](../AGENTIC_EXECUTION_PLAN.md) | How agents execute this project |
| [INPUTS_NEEDED.md](../INPUTS_NEEDED.md) | Owner-confirmed constraints and decisions |

---

## Technical Documentation

| Document | Purpose |
|---|---|
| [docs/PRODUCT_REQUIREMENTS.md](./PRODUCT_REQUIREMENTS.md) | MVP requirements, acceptance criteria, users, and review gates |
| [docs/API_CONTRACT.md](./API_CONTRACT.md) | REST API contract, error shape, and job state transitions |
| [docs/UX_FLOWS.md](./UX_FLOWS.md) | User journeys, screen inventory, and UX diagrams |
| [docs/SECURITY_PRIVACY.md](./SECURITY_PRIVACY.md) | Security, privacy, threat model, and local data-handling requirements |
| [docs/TESTING_STRATEGY.md](./TESTING_STRATEGY.md) | Cross-phase testing strategy, release gates, and validation requirements |
| [docs/PLANNING_GAP_REVIEW.md](./PLANNING_GAP_REVIEW.md) | Planning review summary and remaining owner decisions |
| [docs/STACK.md](./STACK.md) | Technology choices with rationale |
| [docs/GLOSSARY.md](./GLOSSARY.md) | Domain terms and definitions |
| [docs/ADR.md](./ADR.md) | Architecture Decision Records |
| [docs/DATA_SCHEMAS.md](./DATA_SCHEMAS.md) | Canonical data schemas (Job, Telemetry, Analytics, Annotations, Report) |

---

## Phase Plans

| Phase | Document |
|---|---|
| Phase 00 — Discovery | [phases/PHASE_00_DISCOVERY.md](../phases/PHASE_00_DISCOVERY.md) |
| Phase 01 — Repo Boilerplate | [phases/PHASE_01_REPO_BOILERPLATE.md](../phases/PHASE_01_REPO_BOILERPLATE.md) |
| Phase 02 — Local Dev Stack | [phases/PHASE_02_LOCAL_DEV_STACK.md](../phases/PHASE_02_LOCAL_DEV_STACK.md) |
| Phase 03 — Mock Data Dashboard | [phases/PHASE_03_MOCK_DATA_DASHBOARD.md](../phases/PHASE_03_MOCK_DATA_DASHBOARD.md) |
| Phase 04 — Video Upload Workflow | [phases/PHASE_04_VIDEO_UPLOAD.md](../phases/PHASE_04_VIDEO_UPLOAD.md) |
| Phase 05 — CV Engine MVP | [phases/PHASE_05_CV_ENGINE.md](../phases/PHASE_05_CV_ENGINE.md) |
| Phase 06 — Court Calibration | [phases/PHASE_06_COURT_CALIBRATION.md](../phases/PHASE_06_COURT_CALIBRATION.md) |
| Phase 07 — Telemetry Export | [phases/PHASE_07_TELEMETRY_EXPORT.md](../phases/PHASE_07_TELEMETRY_EXPORT.md) |
| Phase 08 — Heatmaps and Visualizations | [phases/PHASE_08_HEATMAPS.md](../phases/PHASE_08_HEATMAPS.md) |
| Phase 09 — Basic Analytics | [phases/PHASE_09_BASIC_ANALYTICS.md](../phases/PHASE_09_BASIC_ANALYTICS.md) |
| Phase 10 — Local LLM Reports | [phases/PHASE_10_LOCAL_LLM_REPORTS.md](../phases/PHASE_10_LOCAL_LLM_REPORTS.md) |
| Phase 11 — Annotation Workflow | [phases/PHASE_11_ANNOTATION.md](../phases/PHASE_11_ANNOTATION.md) |
| Phase 12 — Self-Hosted Release | [phases/PHASE_12_RELEASE.md](../phases/PHASE_12_RELEASE.md) |

---

## How To Navigate This Repo

1. **Starting fresh?** Read `README.md` → `PROJECT_PLAN.md` → `INPUTS_NEEDED.md`.
2. **Confirming scope?** Read `docs/PRODUCT_REQUIREMENTS.md` → `docs/PLANNING_GAP_REVIEW.md`.
3. **About to implement?** Read `ARCHITECTURE.md` → `docs/API_CONTRACT.md` → `docs/DATA_SCHEMAS.md` → phase doc for your current phase.
4. **Running an agent?** Use the agent prompt template in `AGENTIC_EXECUTION_PLAN.md`.
5. **Looking up a term?** See `docs/GLOSSARY.md`.
6. **Wondering why we chose X?** See `docs/ADR.md`.

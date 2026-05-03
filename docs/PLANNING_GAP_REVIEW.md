# Planning Gap Review — Open Hoops

> Cross-document review of planning coverage and remaining owner decisions before coding begins.

---

## 1. Review Summary

The repository already had strong phase plans, architecture notes, ADRs, stack choices, and canonical data schemas. The main gaps were cross-cutting documents that connect the phase plans into a complete product planning package.

This document covers two rounds of planning gap resolution:

**Round 1 (initial review):** Added missing planning coverage for product requirements, API contract, UX flows, security/privacy, and testing strategy.

**Round 2 (deep analysis — 2026-05-03):** Resolved critical blockers and expanded planning for hardware compatibility, design system, state management, monorepo tooling, security, testing rigor, and missing infrastructure artifacts.

---

## 2. Gaps Closed — Round 1

| Gap | Resolution |
|---|---|
| No single product requirements reference | Added `docs/PRODUCT_REQUIREMENTS.md` |
| No API contract before implementation | Added `docs/API_CONTRACT.md` |
| UX flows spread across phase docs only | Added `docs/UX_FLOWS.md` |
| Security/privacy rules only briefly covered in architecture | Added `docs/SECURITY_PRIVACY.md` |
| No global testing strategy | Added `docs/TESTING_STRATEGY.md` |
| Documentation index did not list all planning docs | Updated `docs/README.md` |
| Schema version policy conflicted with annotation/report examples | Updated `docs/DATA_SCHEMAS.md` |
| Phase order around Phase 10/11 needed clearer explanation | Clarified sequencing in planning docs |

---

## 3. Gaps Closed — Round 2 (Deep Analysis)

| Gap | Resolution |
|---|---|
| AMD GPU (RDNA3) / ROCm not in stack — NVIDIA assumed | Updated `ARCHITECTURE.md` (Section 9), `docs/STACK.md`, `CONTRIBUTING.md` |
| Windows + WSL2 requirement not stated | Updated `CONTRIBUTING.md` with WSL2 setup section |
| INPUTS_NEEDED.md incomplete — partial owner answers | Formalized all answers, marked CONFIRMED |
| Phase 00 not closed | Closed with completion note, updated `AGENTIC_EXECUTION_PLAN.md` |
| No design system document | Created `docs/DESIGN_SYSTEM.md` (colors, typography, components, court SVG, motion) |
| No component library decision | shadcn/ui locked in ADR-015 + `docs/STACK.md` |
| No icon system | Lucide React locked in ADR-015 |
| No server state management | TanStack Query + Zustand locked in ADR-014 + `docs/STACK.md` |
| No monorepo tooling | Turborepo locked in ADR-015 |
| ARQ vs Celery undecided | ARQ locked in ADR-012 |
| API routes unversioned | `/api/v1/` prefix applied in `docs/API_CONTRACT.md`, ADR-013 |
| Telemetry file size problem unaddressed | Streaming strategy (signed URL default) added to `docs/API_CONTRACT.md` Section 7 |
| Wrong team assignment heuristic (track_id parity) | Fixed in `docs/DATA_SCHEMAS.md` — team is `null` until annotated |
| CORS policy missing | Added to `docs/API_CONTRACT.md` Section 14 and `docs/SECURITY_PRIVACY.md` |
| MIME type validation missing | Added to `docs/SECURITY_PRIVACY.md` Section 6 (requires `python-filetype`) |
| Prompt injection for player labels | Added to `docs/SECURITY_PRIVACY.md` Section 9 |
| Signed URL expiry not specified | Added to `docs/API_CONTRACT.md` Section 13 and `docs/SECURITY_PRIVACY.md` |
| No onboarding flow spec | Added to `docs/UX_FLOWS.md` Section 9 |
| No loading/skeleton state spec | Added to `docs/UX_FLOWS.md` Section 10 |
| Calibration point names not specified | Added to `docs/UX_FLOWS.md` Section 11 (9-point spec) |
| No keyboard shortcut spec | Added to `docs/UX_FLOWS.md` Section 12 |
| No visual regression testing | Added Playwright screenshot testing to `docs/TESTING_STRATEGY.md` Section 8 |
| No test coverage thresholds | Added per-phase coverage floors to `docs/TESTING_STRATEGY.md` Section 5 |
| No property-based tests for analytics math | Added Hypothesis testing spec to `docs/TESTING_STRATEGY.md` Section 7 |
| Contract test automation not specified | Added CI step spec to `docs/TESTING_STRATEGY.md` Section 4 |
| No resource limits in Docker Compose | Added to `ARCHITECTURE.md` Section 2.8 and `infra/docker-compose.yml` |
| Redis persistence not specified | Added to `ARCHITECTURE.md` Section 2.9 and `infra/docker-compose.yml` |
| No CI/CD pipeline | Created `.github/workflows/ci.yml` |
| Phase 06/05 dependency unclear | Clarified in `phases/PHASE_06_COURT_CALIBRATION.md` — backend first |
| `docs/QUICKSTART.md` missing | Created |
| `.env.example` missing | Created |
| `Makefile` missing | Created |
| `infra/docker-compose.yml` missing | Created |
| `infra/docker-compose.prod.yml` missing | Created |
| `infra/docker-compose.gpu.yml` missing (ROCm) | Created |
| `scripts/setup.sh` missing | Created |
| `scripts/check_health.sh` missing | Created |
| `data/sample/README.md` missing | Created |
| `packages/shared_types/README.md` missing | Created |
| Phase 01 missing CI, Turborepo, shadcn/ui scope | Updated `phases/PHASE_01_REPO_BOILERPLATE.md` |
| Phase 02 missing ARQ lock, resource limits, Redis persistence | Updated `phases/PHASE_02_LOCAL_DEV_STACK.md` |
| Phase 03 missing TanStack Query polling spec | Updated `phases/PHASE_03_MOCK_DATA_DASHBOARD.md` |

---

## 4. Remaining Owner Decisions

The following require owner input before or during implementation:

1. **Confirm Phase 01 start.** Phase 00 is confirmed. Owner may begin Phase 01.
2. **ROCm setup.** Confirm WSL2 is set up with Ubuntu 22.04 and `rocm-smi` shows the AMD R9700 AI.
3. **LLM model.** Default is `llama3.1:8b`. Confirm if owner wants to test `llama3.1:70b-q4` with 32 GB VRAM.
4. **Court type default.** NBA is the default. Confirm if FIBA should be the default for the owner's use case.
5. **Phase execution order.** Confirm whether Phase 06 backend should be completed before Phase 05 integration testing (recommended).

---

## 5. Recommended Pre-Code Gate

- [x] Owner reviews `INPUTS_NEEDED.md` and marks it confirmed. ✅ Done
- [x] Phase 00 closed. ✅ Done
- [ ] Owner reviews `docs/DESIGN_SYSTEM.md` and confirms visual direction.
- [ ] Owner reviews `docs/QUICKSTART.md` and confirms WSL2 setup is feasible.
- [ ] Owner reviews Phase 01 task list and confirms scope is correct.

---

## 6. Documentation Maintenance Rule

When implementation begins, every PR should answer:

1. Did this change alter an API endpoint? If yes, update `docs/API_CONTRACT.md`.
2. Did this change alter stored JSON or database shape? If yes, update `docs/DATA_SCHEMAS.md` and generated types.
3. Did this change alter a user workflow? If yes, update `docs/UX_FLOWS.md`.
4. Did this change alter setup, testing, or release commands? If yes, update `CONTRIBUTING.md` and `docs/TESTING_STRATEGY.md`.
5. Did this change alter privacy/security posture? If yes, update `docs/SECURITY_PRIVACY.md` and consider an ADR.

# Planning Gap Review — Open Hoops

> Cross-document review of planning coverage and remaining owner decisions before coding begins.

---

## 1. Review Summary

The repository already had strong phase plans, architecture notes, ADRs, stack choices, and canonical data schemas. The main gaps were cross-cutting documents that connect the phase plans into a complete product planning package.

This review adds missing planning coverage for:

- Product requirements and MVP acceptance criteria.
- API contract and state transitions.
- UX flows and user-facing diagrams.
- Security, privacy, and data-handling rules.
- Testing strategy and release gates.

---

## 2. Gaps Closed

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

## 3. Remaining Owner Decisions

These are intentionally not resolved by agents without owner input:

1. Confirm all assumptions in `INPUTS_NEEDED.md`.
2. Confirm whether sample data will be synthetic only or include owner-provided video.
3. Confirm primary development hardware and whether GPU is available.
4. Confirm whether the initial implementation should follow file numbering or recommended execution order where Phase 11 may precede Phase 10 for higher-quality reports.
5. Confirm acceptable use/privacy expectations for uploaded game footage.

---

## 4. Recommended Pre-Code Gate

Before Phase 01 begins:

- [ ] Owner reviews `INPUTS_NEEDED.md` and marks it confirmed.
- [ ] Owner reviews `docs/PRODUCT_REQUIREMENTS.md` for MVP scope.
- [ ] Owner reviews `docs/UX_FLOWS.md` for expected user workflow.
- [ ] Owner reviews `docs/SECURITY_PRIVACY.md` for local-first/privacy assumptions.
- [ ] Agent updates Phase 00 completion note.

---

## 5. Documentation Maintenance Rule

When implementation begins, every PR should answer:

1. Did this change alter an API endpoint? If yes, update `docs/API_CONTRACT.md`.
2. Did this change alter stored JSON or database shape? If yes, update `docs/DATA_SCHEMAS.md` and generated types.
3. Did this change alter a user workflow? If yes, update `docs/UX_FLOWS.md`.
4. Did this change alter setup, testing, or release commands? If yes, update `CONTRIBUTING.md` and `docs/TESTING_STRATEGY.md`.
5. Did this change alter privacy/security posture? If yes, update `docs/SECURITY_PRIVACY.md` and consider an ADR.

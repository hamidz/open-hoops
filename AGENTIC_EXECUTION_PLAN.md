# Agentic Execution Plan — Open Hoops

> This document defines how AI agents should interpret, plan, and execute work on this project.
> It is the primary contract between the human owner and any agent operating in this repository.

---

## 1. What Is An Agentic SDLC?

An **agentic SDLC** is a software development lifecycle where AI agents act as the primary executors of defined phases. The human owner sets intent, reviews outputs, and unblocks decisions. Agents do the building.

This repo is managed agentic-first:

- Planning is done in Markdown before any code is written.
- Agents receive a phase document as their primary input.
- Agents produce code, tests, and updated docs as their output.
- The human owner reviews and confirms before the next phase begins.

---

## 2. Agent Operating Rules

Any agent working on this project **must** follow these rules:

### 2.1 Scope Boundary

- Work only within the current phase.
- Do not start work on a future phase without explicit owner confirmation.
- Do not refactor code from previous phases unless the current phase requires it.

### 2.2 Source of Truth

- Markdown files are the source of truth for design decisions.
- If code conflicts with a Markdown spec, the Markdown wins. Raise the conflict before resolving it.
- If a spec is ambiguous, ask before assuming.

### 2.3 Implementation Order

1. Read the phase document fully before writing any code.
2. Read `INPUTS_NEEDED.md` to understand confirmed constraints.
3. Read `ARCHITECTURE.md` to understand system context.
4. Write code only within the bounded scope of the phase.
5. Write or update tests for any new logic introduced.
6. Update relevant docs if the implementation differs from the spec.
7. Report output clearly (what was built, what was skipped, what needs review).

### 2.4 When To Stop And Ask

Agents must stop and ask the owner if:

- A required input from `INPUTS_NEEDED.md` is not yet confirmed.
- The phase doc is ambiguous about a technical decision that has high impact.
- A dependency version conflict appears.
- A security or data privacy concern arises.
- A task would require modifying more than 3 services simultaneously.

### 2.5 Output Expectations

After each phase, the agent should produce:

- Working code committed to the appropriate branch or directory.
- Updated `phases/PHASE_XX_*.md` with a completion checklist.
- A brief summary report: what was built, what tests pass, what was deferred.

---

## 3. Phase Execution Flow

```
Owner confirms INPUTS_NEEDED.md
        ↓
Agent reads Phase doc
        ↓
Agent reads ARCHITECTURE.md + relevant docs
        ↓
Agent implements bounded scope
        ↓
Agent writes/updates tests
        ↓
Agent updates phase doc with ✅ completion notes
        ↓
Owner reviews
        ↓
Owner confirms → next phase
```

---

## 4. Recommended Phase Execution Order

| Phase | Name | Status |
|---|---|---|
| 00 | [Discovery](./phases/PHASE_00_DISCOVERY.md) | 🔲 Pending |
| 01 | [Repo Boilerplate](./phases/PHASE_01_REPO_BOILERPLATE.md) | 🔲 Pending |
| 02 | [Local Dev Stack](./phases/PHASE_02_LOCAL_DEV_STACK.md) | 🔲 Pending |
| 03 | [Mock Data Dashboard](./phases/PHASE_03_MOCK_DATA_DASHBOARD.md) | 🔲 Pending |
| 04 | [Video Upload Workflow](./phases/PHASE_04_VIDEO_UPLOAD.md) | 🔲 Pending |
| 05 | [CV Engine MVP](./phases/PHASE_05_CV_ENGINE.md) | 🔲 Pending |
| 06 | [Court Calibration](./phases/PHASE_06_COURT_CALIBRATION.md) | 🔲 Pending |
| 07 | [Telemetry Export](./phases/PHASE_07_TELEMETRY_EXPORT.md) | 🔲 Pending |
| 08 | [Heatmaps and Visualizations](./phases/PHASE_08_HEATMAPS.md) | 🔲 Pending |
| 09 | [Basic Analytics](./phases/PHASE_09_BASIC_ANALYTICS.md) | 🔲 Pending |
| 11 | [Annotation Workflow](./phases/PHASE_11_ANNOTATION.md) | 🔲 Pending |
| 10 | [Local LLM Reports](./phases/PHASE_10_LOCAL_LLM_REPORTS.md) | 🔲 Pending |
| 12 | [Self-Hosted Release](./phases/PHASE_12_RELEASE.md) | 🔲 Pending |

> **⚠️ Phase Order Note:** Phase 11 (Annotation) is listed before Phase 10 (LLM Reports) intentionally. Phase 10 can run from Phase 09 fallback team assignments, but Phase 11 annotations produce higher-quality analytics and reports. File names retain their original numbering.

Update status to `🟡 In Progress` or `✅ Done` as each phase completes.

---

## 5. Agent Prompt Template

When invoking an agent on a phase, use this template:

```
You are working on the Open Hoops basketball analytics platform.

Your task is to implement Phase XX — [Phase Name].

Read the following files before starting:
- INPUTS_NEEDED.md (confirmed inputs only)
- ARCHITECTURE.md
- phases/PHASE_XX_[NAME].md

Rules:
- Work only within the scope of Phase XX.
- Do not modify services or files outside this phase.
- Write tests for all new logic.
- Update the phase doc checklist when done.
- If anything is ambiguous, stop and report it — do not assume.

Begin.
```

---

## 6. Branching Convention

| Branch pattern | Purpose |
|---|---|
| `main` | Stable, reviewed, owner-confirmed work |
| `phase/XX-short-name` | Active agent implementation branch |
| `fix/short-description` | Bug fixes between phases |
| `docs/short-description` | Documentation-only updates |

Agents work on `phase/XX-*` branches. Owner merges to `main` after review.

---

## 7. Definition of Done (Global)

A phase is **done** when:

- [ ] All tasks in the phase doc are checked off.
- [ ] All automated tests pass.
- [ ] The phase doc has a completion note with date.
- [ ] The owner has reviewed and confirmed.
- [ ] The phase status in this file is updated to `✅ Done`.

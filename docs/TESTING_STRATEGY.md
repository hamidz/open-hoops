# Testing and Quality Strategy — Open Hoops

> Cross-phase testing, validation, and release quality gates. Phase docs define local tasks; this document defines the global strategy.

---

## 1. Quality Goals

- Preserve trust in analytics despite imperfect computer vision.
- Detect schema drift before downstream services break.
- Keep local setup reproducible for new contributors and users.
- Make failures clear, recoverable, and visible in the UI.
- Ensure privacy and local-first guarantees are not accidentally broken.

---

## 2. Test Pyramid

| Layer | Tools | Purpose |
|---|---|---|
| Unit tests | `pytest`, Vitest/Jest | Validate isolated functions, schemas, UI logic |
| Property-based tests | `hypothesis` | Validate analytics math edge cases (zero-distance tracks, out-of-bounds, single-frame) |
| Integration tests | `pytest`, Docker Compose | Validate service boundaries and storage/queue/database interactions |
| Contract tests | Pydantic, OpenAPI, generated TypeScript checks | Ensure API and data schemas remain aligned |
| Visual regression tests | Playwright screenshot comparison | Validate court SVG and heatmap PNG render correctly across changes |
| End-to-end smoke tests | Playwright | Validate core upload → process → review flow |
| Manual owner review | Phase gates | Validate usefulness and UX |

---

## 3. Required Commands

Once implementation exists, these root commands must remain valid:

```bash
make lint
make test
make build
docker compose --env-file .env -f infra/docker-compose.yml config
```

Phase 12 adds release validation:

```bash
docker compose --env-file .env -f infra/docker-compose.yml -f infra/docker-compose.prod.yml up --build
./scripts/check_health.sh
```

---

## 4. Schema and Contract Validation

- Pydantic models are canonical for stored documents.
- TypeScript types are generated from Pydantic models per ADR-010.
- Stored JSON artifacts must include `schema_version` where documented.
- CV worker validates telemetry before writing to MinIO.
- Analytics worker validates analytics summaries before writing to MinIO.
- LLM service validates report JSON before writing to MinIO.
- API responses should match `docs/API_CONTRACT.md` and FastAPI OpenAPI output.

### Contract Test Automation (CI Gate)

The type sync check from ADR-010 is implemented as a concrete CI step in `.github/workflows/ci.yml`:

```yaml
- name: Check TypeScript type sync
  run: |
    make generate-types
    git diff --exit-code packages/shared_types/types/
    # Fails with non-zero exit if generated types differ from committed types
```

This step runs after the `build` job. If it fails, the PR is blocked. Developers must run `make generate-types` locally and commit the updated types before merging.

---

## 5. Phase-Level Minimum Test Coverage

| Phase | Minimum Validation | Coverage Floor |
|---|---|---|
| 01 | Lint/test/build commands exist and pass with scaffolded services | n/a (stubs) |
| 02 | Docker Compose config validates; `/api/v1/health` checks dependencies | n/a (infra) |
| 03 | Mock data generator creates schema-valid files; dashboard renders without console errors | 70% frontend utils |
| 04 | Upload validation, frame extraction, queueing, retry, delete, full upload integration | 80% API upload router |
| 05 | Frame extraction, detection format, homography, telemetry schema, short video integration | 80% CV worker pipeline |
| 06 | Homography computation, reprojection error, calibration API validation | 85% homography service |
| 07 | Telemetry schema validation, telemetry API endpoints, debug artifact retrieval | 80% telemetry writer |
| 08 | KDE heatmap output shape/range, API endpoints, PNG generation | 80% analytics/heatmap |
| 09 | Distance, speed, zone, spacing, analytics summary schema, full pipeline on mock telemetry | 85% analytics worker |
| 10 | Prompt rendering, mocked Ollama response, report schema, hallucination guard checks | 80% LLM service |
| 11 | Annotation model validation, flagged track exclusion, shot stats after recompute | 80% annotation layer |
| 12 | Clean-machine setup, production compose, health checks, release checklist | All prior floors maintained |

Coverage is measured per service. Use `pytest --cov=app --cov-fail-under=<floor>` in CI for each Python service. Frontend coverage via Vitest `--coverage`.

---

## 6. Test Data Strategy

Use three test data classes:

1. **Synthetic telemetry** — deterministic JSON for analytics and dashboard tests.
2. **Synthetic short video** — generated 5–10 second clip for frame extraction and pipeline smoke tests.
3. **Owner-provided sample video** — optional validation data, never committed unless explicitly approved and license/consent is clear.

Sample data rules:

- Prefer generated/synthetic fixtures in git.
- Do not commit real youth or private game footage.
- Large binaries should not be added without owner approval.
- Document sample provenance in `data/sample/README.md`.

---

## 7. Property-Based Testing (Analytics Math)

Analytics computations must be tested with **Hypothesis** to catch edge cases that unit tests miss.

Required property tests:

| Function | Properties to Test |
|---|---|
| `compute_distance(positions)` | Total distance ≥ 0; zero for single-position list; triangle inequality |
| `compute_speed(positions, fps)` | Speed ≥ 0; zero for stationary positions; max speed bounded by physics |
| `assign_zone(court_xy, dimensions)` | Every valid court position maps to exactly one zone; positions outside court boundary return `null` or `out_of_bounds` |
| `compute_kde(positions, grid_size)` | Output grid shape matches requested size; all values ≥ 0; sum of grid ≥ 0 |
| `compute_spacing(team_positions)` | Spacing ≥ 0 for any number of players; zero for single player; result is symmetric |

Hypothesis settings for CI: `max_examples=200` per test. In development: `max_examples=500`.

```python
from hypothesis import given, settings, strategies as st

@given(
    positions=st.lists(
        st.tuples(st.floats(0, 28.65), st.floats(0, 15.24)),
        min_size=1, max_size=200
    )
)
@settings(max_examples=200)
def test_compute_distance_non_negative(positions):
    assert compute_distance(positions) >= 0
```

---

## 8. Visual Regression Testing

The court SVG and heatmap PNG are the primary visual outputs. Visual regressions must be caught before merge.

**Implementation:** Playwright screenshot comparison from Phase 03 onward.

```
apps/web/tests/visual/
├── court-svg.spec.ts      # CourtSVG renders correctly at all orientations
├── heatmap.spec.ts        # HeatmapOverlay renders with known KDE data
├── calibration.spec.ts    # CalibrationCanvas renders frame + markers
└── dashboard.spec.ts      # Dashboard layout with mock data
```

Baseline screenshots are committed to `apps/web/tests/visual/__snapshots__/`. Any pixel difference above the threshold (0.1%) fails the test.

Update baselines with: `npx playwright test --update-snapshots`.

Visual regression tests run in CI on every PR. They do not run in the unit test pass — they run in a separate `visual` job that requires the dev stack to be running.

---

## 7. Performance Validation

| Area | MVP Target |
|---|---|
| CV CPU throughput | At least 5 sampled frames/sec on target hardware |
| Upload max | Default 4 GB, configurable |
| Job progress | Updates every 100 sampled frames |
| LLM report generation | Completes or times out within 120 seconds by default |
| Dashboard | Core job pages render without blocking on full telemetry download |

Performance results should be noted in phase completion notes when measured.

---

## 8. Security and Privacy Validation

Before release and whenever upload/storage/report paths change:

- [ ] No `.env` files or credentials committed.
- [ ] No raw MinIO credentials exposed to frontend.
- [ ] Uploads are size/type validated.
- [ ] Object keys use UUIDs, not untrusted path input.
- [ ] Delete job removes all artifacts.
- [ ] Logs do not contain secrets, signed URLs, or raw video/frame data.
- [ ] No external cloud or LLM API calls during normal analysis.

See `docs/SECURITY_PRIVACY.md` for the full checklist.

---

## 9. Manual Review Gates

Automated tests are not enough for this project. The owner must review:

- Phase 03 dashboard usefulness using mock data.
- Phase 06 calibration UX and accuracy.
- Phase 09 analytics usefulness and explainability.
- Phase 10 report tone, grounding, and usefulness.
- Phase 11 annotation workflow completeness.
- Phase 12 quickstart accuracy.

---

## 10. Release Gate

A release candidate cannot be tagged until:

- [ ] `INPUTS_NEEDED.md` is confirmed.
- [ ] All phase docs have completion notes.
- [ ] `make lint`, `make test`, and `make build` pass.
- [ ] Production Docker Compose starts and health checks pass.
- [ ] Documentation index, changelog, quickstart, ADRs, and schemas are current.
- [ ] Security/privacy checklist passes.
- [ ] Owner completes final manual review.

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
| Integration tests | `pytest`, Docker Compose | Validate service boundaries and storage/queue/database interactions |
| Contract tests | Pydantic, OpenAPI, generated TypeScript checks | Ensure API and data schemas remain aligned |
| End-to-end smoke tests | Playwright or scripted checks | Validate core upload → process → review flow |
| Manual owner review | Phase gates | Validate usefulness and UX |

---

## 3. Required Commands

Once implementation exists, these root commands must remain valid:

```bash
make lint
make test
make build
docker compose -f infra/docker-compose.yml config
```

Phase 12 adds release validation:

```bash
docker compose -f infra/docker-compose.prod.yml up --build
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

---

## 5. Phase-Level Minimum Test Coverage

| Phase | Minimum Validation |
|---|---|
| 01 | Lint/test/build commands exist and pass with scaffolded services |
| 02 | Docker Compose config validates; `/health` checks dependencies |
| 03 | Mock data generator creates schema-valid files; dashboard renders without console errors |
| 04 | Upload validation, frame extraction, queueing, retry, delete, full upload integration |
| 05 | Frame extraction, detection format, homography, telemetry schema, short video integration |
| 06 | Homography computation, reprojection error, calibration API validation |
| 07 | Telemetry schema validation, telemetry API endpoints, debug artifact retrieval |
| 08 | KDE heatmap output shape/range, API endpoints, PNG generation |
| 09 | Distance, speed, zone, spacing, analytics summary schema, full pipeline on mock telemetry |
| 10 | Prompt rendering, mocked Ollama response, report schema, hallucination guard checks |
| 11 | Annotation model validation, flagged track exclusion, shot stats after recompute |
| 12 | Clean-machine setup, production compose, health checks, release checklist |

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

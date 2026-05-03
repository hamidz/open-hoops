# Phase 10 — Local LLM Coaching Reports

> **Goal:** Generate a natural language coaching report from the analytics summary using a local Ollama LLM. Display the report in the dashboard.

---

## Status: 🔲 Pending

---

## Prerequisites

- Phase 09 complete (analytics summary JSON available).
- Ollama running locally (via Docker Compose).

---

## Agent Instructions

Read `ARCHITECTURE.md` for the LLM service responsibilities.
Read `docs/ADR.md` ADR-005 for the Ollama decision.

Your job is to implement `services/llm_service`. This service reads the analytics summary, builds a structured prompt, sends it to Ollama, and returns a coaching report.

Do not hallucinate statistics. The LLM must only use data from the analytics summary — no invented numbers.

---

## Design Principles for LLM Reports

1. **Grounded in data.** Every claim in the report must be traceable to the analytics summary.
2. **Confidence-aware.** If `tracking_coverage_pct` is low for a player, the report must acknowledge reduced confidence.
3. **Actionable.** Reports should suggest specific adjustments, not just describe stats.
4. **Concise.** Target: 200–400 words. Coaches don't want essays.
5. **Structured.** Use consistent sections: Observations, Strengths, Areas for Improvement, Recommendations.

---

## Prompt Template Design

The prompt is built from the analytics summary using Jinja2 templates. Do not use unstructured f-strings.

### System Prompt

```
You are a basketball analytics assistant. You generate coaching reports
based strictly on player tracking data from a game analysis system.

Rules:
- Only use statistics provided in the data below.
- Do not invent or estimate any numbers not in the data.
- If a player's tracking coverage is below 70%, note that their stats may be unreliable.
- Keep the report under 400 words.
- Use clear, coaching-friendly language.
- Structure your response with these sections:
  1. Game Overview
  2. Standout Players
  3. Team Spacing and Movement
  4. Areas for Improvement
  5. Recommendations
```

### User Prompt Template (`prompts/coaching_report.j2`)

```jinja2
Analyze the following basketball game data and generate a coaching report.

Game Duration: {{ duration_seconds | format_duration }}
Players Tracked: {{ players | length }}
Ball Tracking Coverage: {{ ball_tracking_coverage_pct }}%

PLAYER STATS:
{% for player in players %}
Player {{ player.label or player.track_id }} ({{ player.team }}):
  - Distance: {{ player.total_distance_m | round(0) }} m
  - Avg Speed: {{ player.avg_speed_ms | round(1) }} m/s
  - Court Coverage: {{ player.court_coverage_pct | round(1) }}%
  - Tracking Reliability: {{ player.tracking_coverage_pct | round(1) }}%
  - Zone Distribution: Paint {{ (player.zone_distribution.left_paint + player.zone_distribution.right_paint) * 100 | round(0) }}%,
    Three-Point {{ (player.zone_distribution.left_three + player.zone_distribution.right_three) * 100 | round(0) }}%
{% endfor %}

TEAM METRICS:
Home - Avg Spacing: {{ teams.home.avg_spacing_m | round(1) }} m, Court Coverage: {{ teams.home.court_coverage_pct | round(1) }}%
Away - Avg Spacing: {{ teams.away.avg_spacing_m | round(1) }} m, Court Coverage: {{ teams.away.court_coverage_pct | round(1) }}%
```

---

## Tasks

### LLM Service (`services/llm_service`)

- [ ] Implement `services/llm_service/service.py`:
  - Download analytics summary from MinIO.
  - Load and render Jinja2 prompt template.
  - POST to Ollama API: `POST http://ollama:11434/api/generate`.
  - Return generated report text.
  - Handle timeouts (default: 120 seconds) gracefully.

- [ ] Implement `services/llm_service/prompts/coaching_report.j2` — Jinja2 prompt template.

- [ ] Implement Jinja2 custom filters:
  - `format_duration(seconds)` → `"32 min 15 sec"`.

### Ollama Configuration

- [ ] LLM model configurable via env var: `OLLAMA_MODEL=llama3` (default).
- [ ] Ollama host configurable: `OLLAMA_HOST=http://ollama:11434`.
- [ ] On startup, service checks if Ollama is reachable and the model is pulled.
- [ ] If model is not pulled: log a clear error and fail the report job (do not crash the worker).

### API Endpoints

- [ ] `POST /api/jobs/{job_id}/report/generate` — trigger report generation:
  - Enqueues a report generation task.
  - Returns `{ status: "queued" }`.
- [ ] `GET /api/jobs/{job_id}/report` — return the generated report:
  - Returns `{ report_text, model, generated_at, analytics_summary_version }`.
  - Returns 404 if report not yet generated.
- [ ] `DELETE /api/jobs/{job_id}/report` — delete report (allow regeneration with different model).

### Report Storage

- [ ] Store report as `artifacts/{job_id}/coaching_report.json`:
```json
{
  "schema_version": "1.0",
  "job_id": "uuid",
  "model": "llama3",
  "generated_at": "ISO8601",
  "report_text": "...",
  "analytics_summary_version": "1.0",
  "prompt_template_version": "1.0",
  "annotations_applied": false
}
```

### Frontend — Report Display

- [ ] Replace placeholder in Report tab (Phase 03) with real report display.
- [ ] "Generate Report" button → polls until report available.
- [ ] Report text rendered as formatted markdown.
- [ ] Display: model used, generation timestamp, confidence caveat if ball tracking < 70%.
- [ ] "Regenerate" button (calls DELETE then POST).
- [ ] "Copy to Clipboard" button.

### Tests

- [ ] Unit test: Jinja2 prompt renders correctly for a known analytics summary.
- [ ] Unit test: `format_duration` filter.
- [ ] Unit test: report JSON schema validation.
- [ ] Integration test: full analytics → prompt → (mocked Ollama) → report pipeline.

---

## Outputs

- `services/llm_service/service.py`
- `services/llm_service/prompts/coaching_report.j2`
- `apps/api/app/routers/reports.py`
- `apps/web/src/app/dashboard/jobs/[job_id]/report/` — report display.
- Report JSON in MinIO for a test job.

---

## Definition of Done

- [ ] "Generate Report" button in dashboard triggers report generation.
- [ ] Report appears in the Report tab within 120 seconds (on standard hardware).
- [ ] Report text is coherent, data-grounded, and structured.
- [ ] Low-confidence warnings displayed when appropriate.
- [ ] All unit tests pass (including mocked Ollama integration test).
- [ ] Phase status updated in `AGENTIC_EXECUTION_PLAN.md`.

---

## Completion Note

> _Agent: add completion date and summary here when done._

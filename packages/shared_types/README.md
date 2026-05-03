# shared_types — Open Hoops

> Shared data models used across all Open Hoops services.
>
> **Python:** Canonical Pydantic models in `models/` — these are the source of truth.  
> **TypeScript:** Auto-generated types in `types/` — never edit these by hand.

---

## Structure

```
packages/shared_types/
├── models/                  # Canonical Pydantic v2 models (source of truth)
│   ├── __init__.py
│   ├── job.py               # Job, JobStatus, CalibrationRecord
│   ├── telemetry.py         # TelemetryDocument, FrameDetection, Detection
│   ├── analytics.py         # AnalyticsSummary, PlayerMetrics, TeamMetrics
│   ├── annotation.py        # AnnotationDocument, PlayerAnnotation, ShotAnnotation
│   └── report.py            # CoachingReport
├── types/                   # Auto-generated TypeScript types (do not edit)
│   ├── job.ts
│   ├── telemetry.ts
│   ├── analytics.ts
│   ├── annotation.ts
│   └── report.ts
├── generate_types.py        # Type generation script (pydantic-to-typescript)
├── requirements.txt         # pydantic, pydantic-to-typescript
└── README.md
```

---

## Usage

### Python Services

```python
from shared_types.models.telemetry import TelemetryDocument, FrameDetection
from shared_types.models.analytics import AnalyticsSummary
```

Install as a local package in each Python service:
```
# In each service's requirements.txt:
-e ../../packages/shared_types
```

### TypeScript (Next.js)

```typescript
import type { AnalyticsSummary, PlayerMetrics } from '@/packages/shared_types/types/analytics'
```

Or via the workspace package (after Phase 01 Turborepo setup):
```typescript
import type { AnalyticsSummary } from '@open-hoops/shared-types'
```

---

## Regenerating TypeScript Types

After changing any Pydantic model:

```bash
make generate-types
# or directly:
python packages/shared_types/generate_types.py
```

Then commit the updated files in `packages/shared_types/types/`.

> CI will fail if generated types are out of sync with the Pydantic models. See ADR-010 and ADR-015.

---

## Schema Versioning

All document models that are persisted to files include a `schema_version` field. See `docs/DATA_SCHEMAS.md` for the full versioning policy.

When making a breaking change to a model:
1. Bump the `schema_version` in the Pydantic model.
2. Run `make generate-types`.
3. Provide an Alembic migration if the change affects the `jobs` PostgreSQL table.
4. Note the change in `CHANGELOG.md`.

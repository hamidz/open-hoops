# Open Hoops API

FastAPI backend for local-first upload, job status, and generated MVP analytics.

Run locally:

```bash
cd apps/api
../../.venv/Scripts/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The current MVP API uses local JSON/filesystem storage. Set `OPEN_HOOPS_DATA_DIR` to control where upload artifacts and job records are written.

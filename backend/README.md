# Backend

FastAPI service for deterministic data generation and month-end reconciliation reporting.

## Start

```bash
uvicorn app.main:app --reload
```

## Main endpoint

`GET /reconcile`

Query params:

- `regenerate=true|false`
- `report_month=2026-03-01`

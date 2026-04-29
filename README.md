# Data Reconciliation

Month-end reconciliation demo for a payments company whose platform transactions and bank settlements do not line up cleanly.

## What this project does

- Generates deterministic March 2026 test data.
- Reconciles platform transactions against bank settlements.
- Explains the gaps instead of only flagging them.
- Surfaces the four required anomaly types:
  - cross-month settlement
  - rounding difference visible in totals
  - duplicate settlement entry
  - refund without a matching original transaction

## Assumptions

- The reporting month is March 2026.
- Platform transactions are recorded immediately.
- Bank settlements normally arrive 0-2 days later.
- Record-level amount matching allows a tolerance of `0.01`.
- Bank data can contain operational events such as refunds and duplicate rows.

## Run it

### Backend

```bash
cd backend
uvicorn app.main:app --reload
```

API endpoints:

- `GET /health`
- `GET /reconcile?regenerate=true`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the API at `http://localhost:8000` unless `VITE_API_BASE_URL` is set.

## Output

The reconciliation response includes:

- dataset profiles
- reporting-month totals
- record-level reconciliation results
- anomaly buckets with explanations
- sample rows from both datasets

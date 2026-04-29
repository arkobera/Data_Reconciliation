from __future__ import annotations

from pathlib import Path

import pandas as pd
from fastapi import APIRouter, Query

from app.models.schema import ReconciliationResponse
from app.services.anomalies import detect_anomalies
from app.services.matcher import reconcile
from app.services.profiler import profile
from data.generate_data import DATA_DIR, generate_assessment_data

router = APIRouter()


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/reconcile", response_model=ReconciliationResponse)
def run_reconciliation(
    regenerate: bool = Query(True, description="Regenerate deterministic assessment data before running."),
    report_month: str = Query("2026-03-01", description="Month to reconcile, expressed as any date in that month."),
) -> ReconciliationResponse:
    data_dir = Path(DATA_DIR)
    if regenerate:
        df_txn, df_settle = generate_assessment_data(data_dir=data_dir)
    else:
        df_txn = pd.read_csv(data_dir / "transactions.csv", parse_dates=["txn_date"])
        df_settle = pd.read_csv(data_dir / "settlements.csv", parse_dates=["settle_date"])

    summary = reconcile(df_txn, df_settle, report_month=report_month)
    anomalies = detect_anomalies(summary)

    highlights = [
        "Month-end reporting uses March 2026 platform activity against bank entries posted through March 31, 2026.",
        "Settlements are assumed to arrive 0-2 days after the platform transaction unless a planted anomaly pushes them outside the month.",
        "A 0.01 tolerance is allowed for record-level matching so small rounding drift can stay hidden until totals are rolled up.",
        "Settlement rows can include operational bank events, so refunds and duplicates are evaluated separately from normal customer payments.",
    ]

    return ReconciliationResponse(
        assumptions=highlights,
        transaction_profile=profile(df_txn, "txn_date", "Platform transactions"),
        settlement_profile=profile(df_settle, "settle_date", "Bank settlements"),
        reconciliation=summary,
        anomalies=anomalies,
        highlights=[
            f"Platform March total is {summary['totals']['platform_total']:.2f} versus bank March total {summary['totals']['settlement_total']:.2f}.",
            f"{summary['totals']['unmatched_count']} records require explanation outside clean matches.",
            "The generated dataset intentionally includes a next-month settlement, a rounding drift, a duplicate bank entry, and a refund without an original.",
        ],
        sample_source_rows=df_txn.head(5).assign(txn_date=lambda df: df["txn_date"].dt.strftime("%Y-%m-%d")).to_dict(
            orient="records"
        ),
        sample_target_rows=df_settle.head(5)
        .assign(settle_date=lambda df: df["settle_date"].dt.strftime("%Y-%m-%d"))
        .to_dict(orient="records"),
    )

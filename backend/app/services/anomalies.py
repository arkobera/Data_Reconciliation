from __future__ import annotations

from typing import Any


def _bucket(summary: dict[str, Any], status: str, title: str, description: str) -> dict[str, Any]:
    matches = [item for item in summary["record_results"] if item["status"] == status]
    return {
        "key": status,
        "title": title,
        "description": description,
        "count": len(matches),
        "net_amount": round(sum(item["amount_delta"] for item in matches), 2),
        "records": matches,
    }


def detect_anomalies(summary: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert reconciliation results into explainable anomaly buckets."""

    buckets = [
        _bucket(
            summary,
            "cross_month_settlement",
            "Cross-month settlement",
            "Platform transaction exists in the reporting month, but the bank posted settlement after month end.",
        ),
        _bucket(
            summary,
            "rounding_difference",
            "Rounding difference",
            "Record matched within tolerance, but a small amount drift remains and only becomes material in totals.",
        ),
        _bucket(
            summary,
            "duplicate_settlement",
            "Duplicate settlement",
            "The settlement dataset contains the same bank entry more than once.",
        ),
        _bucket(
            summary,
            "refund_without_original",
            "Refund without original",
            "A refund was received without a matching original platform transaction in the source month.",
        ),
        _bucket(
            summary,
            "missing_settlement",
            "Missing settlement",
            "Platform transaction has no settlement candidate at all.",
        ),
    ]
    return [bucket for bucket in buckets if bucket["count"] > 0]

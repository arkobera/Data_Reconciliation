from __future__ import annotations

from typing import Any

import pandas as pd

from app.utils.hashing import hash_record


def reconcile(
    df_txn: pd.DataFrame,
    df_settle: pd.DataFrame,
    report_month: str,
    tolerance: float = 0.01,
) -> dict[str, Any]:
    month_start = pd.Timestamp(report_month).to_period("M").start_time.normalize()
    month_end = pd.Timestamp(report_month).to_period("M").end_time.normalize()

    transactions = df_txn.copy()
    settlements = df_settle.copy()

    transactions["txn_date"] = pd.to_datetime(transactions["txn_date"])
    settlements["settle_date"] = pd.to_datetime(settlements["settle_date"])
    transactions["record_hash"] = transactions.apply(
        lambda row: hash_record(row, ["txn_id", "amount", "txn_date"]), axis=1
    )
    settlements["record_hash"] = settlements.apply(
        lambda row: hash_record(row, ["settle_id", "linked_txn_id", "amount", "settle_date", "entry_type"]),
        axis=1,
    )

    duplicate_mask = settlements.duplicated(
        subset=["linked_txn_id", "amount", "settle_date", "entry_type"], keep="first"
    )
    duplicate_rows = settlements[duplicate_mask].copy()
    settlements["is_duplicate"] = duplicate_mask

    reporting_txns = transactions[
        (transactions["txn_date"] >= month_start) & (transactions["txn_date"] <= month_end)
    ].copy()
    reporting_settlements = settlements[
        (settlements["settle_date"] >= month_start) & (settlements["settle_date"] <= month_end)
    ].copy()

    results: list[dict[str, Any]] = []

    for _, txn in reporting_txns.iterrows():
        candidates = settlements[
            (settlements["linked_txn_id"] == txn["txn_id"]) & (~settlements["is_duplicate"])
        ].sort_values("settle_date")

        if candidates.empty:
            results.append(
                {
                    "txn_id": txn["txn_id"],
                    "settle_id": None,
                    "status": "missing_settlement",
                    "transaction_date": txn["txn_date"].date().isoformat(),
                    "settlement_date": None,
                    "platform_amount": round(float(txn["amount"]), 2),
                    "settlement_amount": None,
                    "amount_delta": round(float(txn["amount"]), 2),
                    "days_to_settle": None,
                    "explanation": "No bank settlement was found for this platform transaction.",
                }
            )
            continue

        settlement = candidates.iloc[0]
        amount_delta = round(float(txn["amount"] - settlement["amount"]), 2)
        days_to_settle = int((settlement["settle_date"] - txn["txn_date"]).days)

        if settlement["settle_date"] > month_end:
            status = "cross_month_settlement"
            amount_delta = round(float(txn["amount"]), 2)
            explanation = "The settlement exists, but it landed after the reporting month closed."
        elif abs(amount_delta) > 0 and abs(amount_delta) <= tolerance:
            status = "rounding_difference"
            explanation = "The settlement matches within tolerance, but a small rounding drift remains."
        else:
            status = "matched"
            explanation = "Transaction and settlement reconcile inside the reporting month."

        results.append(
            {
                "txn_id": txn["txn_id"],
                "settle_id": settlement["settle_id"],
                "status": status,
                "transaction_date": txn["txn_date"].date().isoformat(),
                "settlement_date": settlement["settle_date"].date().isoformat(),
                "platform_amount": round(float(txn["amount"]), 2),
                "settlement_amount": round(float(settlement["amount"]), 2),
                "amount_delta": amount_delta,
                "days_to_settle": days_to_settle,
                "explanation": explanation,
            }
        )

    duplicate_amount = round(float(duplicate_rows["amount"].sum()), 2) if not duplicate_rows.empty else 0.0
    for _, duplicate in duplicate_rows.iterrows():
        results.append(
            {
                "txn_id": duplicate["linked_txn_id"],
                "settle_id": duplicate["settle_id"],
                "status": "duplicate_settlement",
                "transaction_date": None,
                "settlement_date": duplicate["settle_date"].date().isoformat(),
                "platform_amount": None,
                "settlement_amount": round(float(duplicate["amount"]), 2),
                "amount_delta": round(float(-duplicate["amount"]), 2),
                "days_to_settle": None,
                "explanation": "This bank settlement appears more than once in the target dataset.",
            }
        )

    refunds = settlements[
        (settlements["entry_type"] == "refund")
        & (~settlements["linked_txn_id"].isin(transactions["txn_id"]))
    ].copy()
    for _, refund in refunds.iterrows():
        results.append(
            {
                "txn_id": refund["linked_txn_id"],
                "settle_id": refund["settle_id"],
                "status": "refund_without_original",
                "transaction_date": None,
                "settlement_date": refund["settle_date"].date().isoformat(),
                "platform_amount": None,
                "settlement_amount": round(float(refund["amount"]), 2),
                "amount_delta": round(float(-refund["amount"]), 2),
                "days_to_settle": None,
                "explanation": "Refund settlement has no matching original transaction in the platform ledger.",
            }
        )

    matched_results = [item for item in results if item["status"] == "matched"]
    reporting_txn_total = round(float(reporting_txns["amount"].sum()), 2)
    reporting_settlement_total = round(float(reporting_settlements["amount"].sum()), 2)
    unmatched_total = round(
        sum(item["amount_delta"] for item in results if item["status"] != "matched"),
        2,
    )

    return {
        "reporting_month": pd.Timestamp(report_month).strftime("%Y-%m"),
        "month_start": month_start.date().isoformat(),
        "month_end": month_end.date().isoformat(),
        "tolerance": tolerance,
        "record_results": results,
        "totals": {
            "platform_total": reporting_txn_total,
            "settlement_total": reporting_settlement_total,
            "net_difference": round(reporting_txn_total - reporting_settlement_total, 2),
            "explained_difference": unmatched_total,
            "matched_count": len(matched_results),
            "unmatched_count": len(results) - len(matched_results),
            "duplicate_settlement_amount": duplicate_amount,
        },
    }

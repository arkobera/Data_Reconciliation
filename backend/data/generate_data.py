from __future__ import annotations

from pathlib import Path
import random

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent


def generate_assessment_data(data_dir: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    output_dir = data_dir or DATA_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    rng = random.Random(42)
    base_date = pd.Timestamp("2026-03-21")

    transactions: list[dict[str, object]] = []
    for index in range(1, 31):
        txn_date = base_date + pd.Timedelta(days=rng.randint(0, 7))
        amount = round(rng.uniform(95, 950), 2)
        transactions.append(
            {
                "txn_id": f"TXN-{index:03d}",
                "customer_id": f"CUST-{rng.randint(1000, 9999)}",
                "amount": amount,
                "currency": "INR",
                "txn_date": txn_date,
            }
        )

    df_txn = pd.DataFrame(transactions)

    settlements: list[dict[str, object]] = []
    for _, row in df_txn.iterrows():
        settle_date = row["txn_date"] + pd.Timedelta(days=rng.choice([0, 1, 2]))
        settlements.append(
            {
                "settle_id": f"SET-{row['txn_id']}",
                "linked_txn_id": row["txn_id"],
                "amount": row["amount"],
                "settle_date": settle_date,
                "entry_type": "settlement",
                "batch_id": f"BATCH-{settle_date.strftime('%Y%m%d')}",
            }
        )

    df_settle = pd.DataFrame(settlements)

    cross_month_txn = "TXN-001"
    cross_month_amount = 412.37
    df_txn.loc[df_txn["txn_id"] == cross_month_txn, ["amount", "txn_date"]] = [cross_month_amount, pd.Timestamp("2026-03-31")]
    df_settle.loc[df_settle["linked_txn_id"] == cross_month_txn, ["amount", "settle_date", "batch_id"]] = [
        cross_month_amount,
        pd.Timestamp("2026-04-01"),
        "BATCH-20260401",
    ]

    rounding_txn = "TXN-002"
    rounding_amount = 255.43
    df_txn.loc[df_txn["txn_id"] == rounding_txn, "amount"] = rounding_amount
    df_settle.loc[df_settle["linked_txn_id"] == rounding_txn, "amount"] = 255.42

    duplicate_txn = "TXN-003"
    df_txn.loc[df_txn["txn_id"] == duplicate_txn, "amount"] = 109.22
    df_settle.loc[df_settle["linked_txn_id"] == duplicate_txn, "amount"] = 109.22
    duplicate_row = df_settle[df_settle["linked_txn_id"] == duplicate_txn].copy()
    df_settle = pd.concat([df_settle, duplicate_row], ignore_index=True)

    refund_row = {
        "settle_id": "SET-REFUND-ORPHAN",
        "linked_txn_id": "TXN-404",
        "amount": -189.55,
        "settle_date": pd.Timestamp("2026-03-30"),
        "entry_type": "refund",
        "batch_id": "BATCH-20260330",
    }
    df_settle.loc[len(df_settle)] = refund_row

    df_txn = df_txn.sort_values("txn_date").reset_index(drop=True)
    df_settle = df_settle.sort_values("settle_date").reset_index(drop=True)

    df_txn.to_csv(output_dir / "transactions.csv", index=False)
    df_settle.to_csv(output_dir / "settlements.csv", index=False)

    return df_txn, df_settle


if __name__ == "__main__":
    generate_assessment_data()
    print("Assessment data generated.")

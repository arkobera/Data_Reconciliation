import pandas as pd

def reconcile(df_txn, df_settle, tolerance=0.01):
    results = []

    df_txn["matched"] = False

    for _, txn in df_txn.iterrows():
        candidates = df_settle[
            (abs(df_settle["amount"] - txn["amount"]) <= tolerance)
        ]

        if len(candidates) == 0:
            results.append({
                "txn_id": txn["txn_id"],
                "status": "missing_settlement"
            })
        else:
            df_txn.loc[df_txn.txn_id == txn.txn_id, "matched"] = True

    return results
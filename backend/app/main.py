from fastapi import FastAPI
import pandas as pd
from app.services.matcher import reconcile
from app.services.profiler import profile
from app.services.anomalies import detect_anomalies

app = FastAPI()

@app.get("/reconcile")
def run_reconciliation():
    df_txn = pd.read_csv("backend/data/transactions.csv")
    df_settle = pd.read_csv("backend/data/settlements.csv")

    summary = {
        "txn_profile": profile(df_txn),
        "settle_profile": profile(df_settle),
        "reconciliation": reconcile(df_txn, df_settle),
        "anomalies": detect_anomalies(df_txn, df_settle)
    }

    return summary
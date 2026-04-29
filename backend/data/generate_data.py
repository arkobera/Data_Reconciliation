import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)

N = 1000

base_date = datetime(2026, 3, 25)

transactions = []
for i in range(N):
    txn_date = base_date + timedelta(days=random.randint(0, 5))
    amount = round(np.random.uniform(100, 1000), 2)

    transactions.append({
        "txn_id": f"T{i}",
        "amount": amount,
        "txn_date": txn_date
    })

df_txn = pd.DataFrame(transactions)

# --- Create settlements ---
settlements = []

for _, row in df_txn.iterrows():
    delay = random.choice([0, 1, 2])
    settle_date = row["txn_date"] + timedelta(days=delay)

    settlements.append({
        "settle_id": f"S{row.txn_id}",
        "amount": row["amount"],
        "settle_date": settle_date
    })

df_settle = pd.DataFrame(settlements)

# 🔥 Inject discrepancies

# 1. Cross-month settlement
df_settle.loc[0, "settle_date"] = datetime(2026, 4, 1)

# 2. Rounding issue
df_settle.loc[1, "amount"] += 0.01 #type: ignore

# 3. Duplicate
df_settle = pd.concat([df_settle, df_settle.iloc[[2]]])

# 4. Refund without original
df_settle.loc[len(df_settle)] = ["S_refund", -500, datetime(2026, 3, 28)]

df_txn.to_csv("transactions.csv", index=False)
df_settle.to_csv("settlements.csv", index=False)

print("Data generated.")
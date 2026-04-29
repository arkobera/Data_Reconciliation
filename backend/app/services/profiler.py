from __future__ import annotations

from typing import Any

import pandas as pd


def profile(df: pd.DataFrame, date_column: str, label: str) -> dict[str, Any]:
    dated = df.copy()
    dated[date_column] = pd.to_datetime(dated[date_column])

    negatives = int((dated["amount"] < 0).sum())
    return {
        "label": label,
        "count": int(len(dated)),
        "total_amount": round(float(dated["amount"].sum()), 2),
        "duplicate_rows": int(dated.duplicated().sum()),
        "negative_amount_rows": negatives,
        "date_range": {
            "start": dated[date_column].min().date().isoformat(),
            "end": dated[date_column].max().date().isoformat(),
        },
    }

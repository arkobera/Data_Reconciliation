def detect_anomalies(df_txn, df_settle):
    anomalies = {}

    # Duplicate detection
    anomalies["duplicates"] = df_settle[df_settle.duplicated()]

    # Refund without match
    anomalies["refunds"] = df_settle[df_settle["amount"] < 0]

    return anomalies
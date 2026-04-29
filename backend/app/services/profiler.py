def profile(df):
    return {
        "count": len(df),
        "total_amount": df["amount"].sum(),
        "duplicates": df.duplicated().sum()
    }
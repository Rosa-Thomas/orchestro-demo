
def compute_kpis(df):
    #key performance indicators
    kpis = {}
    if "Amount" in df.columns:
        kpis["total_amount"] = df["Amount"].sum()
        kpis["avg_amount"] = df["Amount"].mean()
    if "Category" in df.columns:
        kpis["count_by_category"] = df["Category"].value_counts().to_dict()
    return kpis

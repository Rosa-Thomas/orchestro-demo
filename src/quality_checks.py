
def run_quality_checks(df):
    report = {}
    report["missing_values"] = df.isna().sum().to_dict()
    numeric = df.select_dtypes(include=['int64', 'float64'])
    report["negative_values"] = (numeric < 0).sum().to_dict()
    if "Category" in df.columns:
        allowed = {"A", "B", "C"}
        uniques = set(df["Category"].unique())
        report["invalid_categories"] = list(uniques - allowed)
    return report

from config import STRING_BOUNDS, VALUE_BOUNDS, CATEGORY_VALUE_BOUNDS

def run_quality_checks(df):
    report = {}

    # Missing values per column
    report["missing_values"] = df.isna().sum().to_dict()

    # Negative numeric values
    numeric = df.select_dtypes(include=['number'])
    report["negative_values"] = (numeric < 0).sum().to_dict()

    # Invalid strings (categories or other string bounds)
    report["invalid_strings"] = {}
    for col, allowed_values in STRING_BOUNDS.items():
        if col in df.columns:
            uniques = set(df[col].dropna().unique())
            allowed_set = set(allowed_values)
            invalids = sorted(uniques - allowed_set)
            if invalids:
                report["invalid_strings"][col] = invalids

    # Numeric values outside global VALUE_BOUNDS
    report["out_of_bounds"] = {}
    for col, bounds in VALUE_BOUNDS.items():
        if col in df.columns:
            min_val, max_val = bounds
            below_min = (df[col] < min_val).sum()
            above_max = (df[col] > max_val).sum()
            if below_min or above_max:
                report["out_of_bounds"][col] = {
                    "below_global_min": int(below_min),
                    "above_global_max": int(above_max)
                }

    # Numeric values outside CATEGORY_VALUE_BOUNDS
    for col, cat_bounds in CATEGORY_VALUE_BOUNDS.items():
        if col in df.columns and "Category" in df.columns:
            out_of_bounds_cat = {}
            for cat, (min_val, max_val) in cat_bounds.items():
                subset = df[df["Category"] == cat]
                below = (subset[col] < min_val).sum()
                above = (subset[col] > max_val).sum()
                if below or above:
                    out_of_bounds_cat[cat] = {"below_min": int(below), "above_max": int(above)}
            if out_of_bounds_cat:
                if col not in report["out_of_bounds"]:
                    report["out_of_bounds"][col] = {}
                report["out_of_bounds"][col]["category_bounds"] = out_of_bounds_cat

    return report

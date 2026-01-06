import pandas as pd
from config import COLUMNS, BEHAVIOR

def run_quality_checks(df: pd.DataFrame) -> dict:
    report = {}

    # Missing values
    report["missing_values"] = df.isna().sum().to_dict()

    # Negative numeric values
    numeric = df.select_dtypes(include=["number"])
    report["negative_values"] = (numeric < 0).sum().to_dict()

    # Invalid strings
    report["invalid_strings"] = {}

    for col, spec in COLUMNS.items():
        if col not in df.columns:
            continue
        rules = spec.get("rules", {})
        col_type = spec.get("type", "string")

        if col_type != "string":
            continue

        uniques = set(df[col].dropna().unique())

        # White list violations
        if "white_list" in rules:
            allowed_set = set(rules["white_list"])
            invalids = sorted(uniques - allowed_set)
            if invalids:
                report["invalid_strings"][col] = invalids

        # Black list violations
        if "black_list" in rules:
            forbidden_set = set(rules["black_list"])
            present_forbidden = sorted(uniques & forbidden_set)
            if present_forbidden:
                if col not in report["invalid_strings"]:
                    report["invalid_strings"][col] = present_forbidden
                else:
                    report["invalid_strings"][col] += present_forbidden

    # Numeric out-of-bounds
    report["out_of_bounds"] = {}

    for col, spec in COLUMNS.items():
        if col not in df.columns:
            continue
        rules = spec.get("rules", {})
        col_type = spec.get("type", "string")

        if col_type != "numeric":
            continue

        # Global bounds
        if "bounds" in rules:
            min_val, max_val = rules["bounds"]
            below_min = (df[col] < min_val).sum()
            above_max = (df[col] > max_val).sum()
            if below_min or above_max:
                report["out_of_bounds"][col] = {
                    "below_global_min": int(below_min),
                    "above_global_max": int(above_max)
                }

        # Category-specific bounds
        if "category_bounds" in rules and "Category" in df.columns:
            out_of_bounds_cat = {}
            for cat, (min_val, max_val) in rules["category_bounds"].items():
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

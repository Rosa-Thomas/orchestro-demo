import pandas as pd
from dataclasses import dataclass
from config import COLUMNS, BEHAVIOR, REMOVAL_REASON_COLUMN


@dataclass
class CleaningStats:
    rows_input: int
    rows_output: int
    rows_removed: int


def clean_data(df: pd.DataFrame):
    df = df.copy()
    rows_input = len(df)

    if REMOVAL_REASON_COLUMN not in df.columns:
        df[REMOVAL_REASON_COLUMN] = ""

    removed_rows = []

    def mark(mask, reason):
        nonlocal removed_rows
        affected = df.loc[mask].copy()
        if not affected.empty:
            affected[REMOVAL_REASON_COLUMN] = reason
            removed_rows.append(affected)
            df.loc[mask, REMOVAL_REASON_COLUMN] = reason

    string_strategy = BEHAVIOR.get("string_violations_strategy", "remove")
    numeric_strategy = BEHAVIOR.get("numeric_bounds_strategy", "remove")

    df.drop_duplicates(inplace=True)

    for col, spec in COLUMNS.items():
        if col not in df.columns:
            continue

        col_type = spec.get("type")
        rules = spec.get("rules", {})

        if col_type == "string":
            df[col] = df[col].astype(str).str.strip()

            if "white_list" in rules:
                allowed = rules["white_list"]
                mask = ~df[col].isin(allowed)
                if mask.any():
                    mark(mask, f"{col}: not in whitelist")
                    if string_strategy == "remove":
                        df = df[~mask]

            if "black_list" in rules:
                forbidden = rules["black_list"]
                mask = df[col].isin(forbidden)
                if mask.any():
                    mark(mask, f"{col}: in blacklist")
                    if string_strategy == "remove":
                        df = df[~mask]

        if col_type == "numeric":
            df[col] = pd.to_numeric(df[col], errors="coerce")

            fill_na = rules.get("fill_na", "ignore")
            if fill_na == "remove":
                mask = df[col].isna()
                mark(mask, f"{col}: missing value")
                df = df[~mask]
            elif fill_na == "median":
                if "Category" in df.columns:
                    df[col] = df.groupby("Category")[col].transform(
                        lambda x: x.fillna(x.median())
                    )
                else:
                    df[col] = df[col].fillna(df[col].median())
            elif fill_na == "mean":
                df[col] = df[col].fillna(df[col].mean())

            df[col] = df[col].abs()

            if "bounds" in rules and numeric_strategy != "ignore":
                min_val, max_val = rules["bounds"]
                if numeric_strategy == "clip":
                    df[col] = df[col].clip(min_val, max_val)
                elif numeric_strategy == "remove":
                    mask = (df[col] < min_val) | (df[col] > max_val)
                    mark(mask, f"{col}: outside global bounds")
                    df = df[~mask]

            if "category_bounds" in rules and "Category" in df.columns:
                for cat, (min_val, max_val) in rules["category_bounds"].items():
                    mask = (
                        (df["Category"] == cat)
                        & ((df[col] < min_val) | (df[col] > max_val))
                    )
                    if mask.any():
                        mark(mask, f"{col}: outside bounds for category {cat}")
                        if numeric_strategy == "clip":
                            df.loc[df["Category"] == cat, col] = df.loc[
                                df["Category"] == cat, col
                            ].clip(min_val, max_val)
                        elif numeric_strategy == "remove":
                            df = df[~mask]

    df_removed = (
        pd.concat(removed_rows, ignore_index=True)
        if removed_rows
        else pd.DataFrame(columns=df.columns)
    )

    stats = CleaningStats(
        rows_input=rows_input,
        rows_output=len(df),
        rows_removed=len(df_removed),
    )

    return df.reset_index(drop=True), df_removed.reset_index(drop=True), stats

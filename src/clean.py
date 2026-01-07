import pandas as pd
from dataclasses import dataclass, field
from config import (
    COLUMNS,
    BEHAVIOR,
    SORT_COLUMNS,
    SORT_ORDER,
    REMOVAL_REASON_COLUMN,
)

@dataclass
class CleaningStats:
    rows_initial: int = 0
    rows_final: int = 0
    rows_removed: int = 0
    removals_by_reason: dict = field(default_factory=dict)

def mark_for_removal(df, mask, reason):
    df.loc[mask, REMOVAL_REASON_COLUMN] = (
        df.loc[mask, REMOVAL_REASON_COLUMN]
        .fillna(reason)
        .where(
            df.loc[mask, REMOVAL_REASON_COLUMN].isna(),
            df.loc[mask, REMOVAL_REASON_COLUMN] + " | " + reason
        )
    )


def clean_data(df: pd.DataFrame):
    df = df.copy()
    stats = CleaningStats()
    stats.rows_initial = len(df)

    df[REMOVAL_REASON_COLUMN] = pd.NA
    df.drop_duplicates(inplace=True)

    for col, spec in COLUMNS.items():
        if col not in df.columns:
            continue

        rules = spec.get("rules", {})
        col_type = spec.get("type", "string")

        if col_type == "string":
            if "white_list" in rules:
                mask = ~df[col].isin(rules["white_list"])
                mark_for_removal(df, mask, f"{col}: not in whitelist")

            if "black_list" in rules:
                mask = df[col].isin(rules["black_list"])
                mark_for_removal(df, mask, f"{col}: blacklisted value")

        if col_type == "numeric":
            df[col] = df[col].abs()

            if rules.get("fill_na") == "remove":
                mask = df[col].isna()
                mark_for_removal(df, mask, f"{col}: missing value")

            if "bounds" in rules and BEHAVIOR["numeric_bounds_strategy"] == "remove":
                min_val, max_val = rules["bounds"]
                mask = (df[col] < min_val) | (df[col] > max_val)
                mark_for_removal(
                    df,
                    mask,
                    f"{col}: outside global bounds [{min_val}, {max_val}]",
                )

            if "category_bounds" in rules and "Category" in df.columns:
                for cat, (min_val, max_val) in rules["category_bounds"].items():
                    mask = (
                        (df["Category"] == cat)
                        & ((df[col] < min_val) | (df[col] > max_val))
                    )
                    if BEHAVIOR["numeric_bounds_strategy"] == "remove":
                        mark_for_removal(
                            df,
                            mask,
                            f"{col}: outside bounds for Category {cat} [{min_val}, {max_val}]",
                        )

    removed_df = df[df[REMOVAL_REASON_COLUMN].notna()].copy()
    clean_df = df[df[REMOVAL_REASON_COLUMN].isna()].drop(
        columns=[REMOVAL_REASON_COLUMN]
    )

    stats.rows_final = len(clean_df)
    stats.rows_removed = len(removed_df)

    if not removed_df.empty:
        stats.removals_by_reason = (
            removed_df[REMOVAL_REASON_COLUMN]
            .str.split(" \\| ")
            .explode()
            .value_counts()
            .to_dict()
        )

    sort_cols = [c for c in SORT_COLUMNS["default"] if c in clean_df.columns]
    if sort_cols:
        clean_df = clean_df.sort_values(
            by=sort_cols,
            ascending=SORT_ORDER["default"][:len(sort_cols)],
        ).reset_index(drop=True)

    return clean_df, removed_df, stats

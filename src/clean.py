import pandas as pd
from dataclasses import dataclass
from config import (
    COLUMNS,
    DEFAULT_BEHAVIOR,
    REMOVAL_REASON_COLUMN,
    FLAG_REASON_COLUMN,
)


@dataclass
class CleaningStats:
    rows_input: int
    rows_output: int
    rows_removed: int
    rows_flagged: int

    def __post_init__(self):
        self.rows_input = int(self.rows_input)
        self.rows_output = int(self.rows_output)
        self.rows_removed = int(self.rows_removed)
        self.rows_flagged = int(self.rows_flagged)


def resolve_behavior(spec, col_type, key):
    return (
        spec.get("behavior", {}).get(key)
        or DEFAULT_BEHAVIOR.get(col_type, {}).get(key)
        or "ignore"
    )


def clean_data(df: pd.DataFrame):
    df = df.copy()
    rows_input = len(df)

    for col in [REMOVAL_REASON_COLUMN, FLAG_REASON_COLUMN]:
        if col not in df.columns:
            df[col] = ""

    removed_rows = []

    def append_reason(mask, column, reason):
        for idx in df.index[mask]:
            existing = df.at[idx, column]
            if not existing:
                df.at[idx, column] = reason
            else:
                reasons = existing.split(" | ")
                if reason not in reasons:
                    df.at[idx, column] = existing + " | " + reason

    def handle_violation(mask, reason, action):
        nonlocal df, removed_rows

        if not mask.any():
            return

        if action == "remove":
            append_reason(mask, REMOVAL_REASON_COLUMN, reason)
            removed_rows.append(df.loc[mask].copy())
            df = df.loc[~mask]

        elif action == "flag":
            append_reason(mask, FLAG_REASON_COLUMN, reason)

    df.drop_duplicates(inplace=True)

    for col, spec in COLUMNS.items():
        if col not in df.columns:
            continue

        col_type = spec.get("type")
        rules = spec.get("rules", {})

        if col_type == "string":
            df[col] = df[col].astype(str).str.strip()

            violation_action = resolve_behavior(spec, "string", "violation")

            if "white_list" in rules:
                mask = ~df[col].isin(rules["white_list"])
                handle_violation(mask, f"{col}: not in whitelist", violation_action)

            if "black_list" in rules:
                mask = df[col].isin(rules["black_list"])
                handle_violation(mask, f"{col}: in blacklist", violation_action)

            for rule_name in ["contains", "starts_with", "ends_with", "regex"]:
                if rule_name in rules:
                    for value in rules[rule_name]:
                        if rule_name == "contains":
                            mask = df[col].str.contains(value, na=False)
                            reason = f"{col}: contains '{value}'"
                        elif rule_name == "starts_with":
                            mask = df[col].str.startswith(value, na=False)
                            reason = f"{col}: starts with '{value}'"
                        elif rule_name == "ends_with":
                            mask = df[col].str.endswith(value, na=False)
                            reason = f"{col}: ends with '{value}'"
                        else:
                            mask = df[col].str.match(value, na=False)
                            reason = f"{col}: matches regex '{value}'"

                        handle_violation(mask, reason, violation_action)

        elif col_type == "numeric":
            df[col] = pd.to_numeric(df[col], errors="coerce")

            missing_action = resolve_behavior(spec, "numeric", "missing")
            bounds_action = resolve_behavior(spec, "numeric", "bounds")

            fill_na = rules.get("fill_na", "ignore")
            if fill_na == "remove":
                mask = df[col].isna()
                handle_violation(mask, f"{col}: missing value", "remove")
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

            if "bounds" in rules and bounds_action != "ignore":
                min_val, max_val = rules["bounds"]
                if bounds_action == "clip":
                    df[col] = df[col].clip(min_val, max_val)
                elif bounds_action == "remove":
                    mask = (df[col] < min_val) | (df[col] > max_val)
                    handle_violation(mask, f"{col}: outside global bounds", "remove")

            if "category_bounds" in rules and "Category" in df.columns:
                for cat, (min_val, max_val) in rules["category_bounds"].items():
                    mask = (
                        (df["Category"] == cat)
                        & ((df[col] < min_val) | (df[col] > max_val))
                    )

                    if bounds_action == "clip":
                        df.loc[df["Category"] == cat, col] = df.loc[
                            df["Category"] == cat, col
                        ].clip(min_val, max_val)
                    elif bounds_action == "remove":
                        handle_violation(
                            mask,
                            f"{col}: outside bounds for category {cat}",
                            "remove",
                        )

    df_clean = df.reset_index(drop=True)

    if removed_rows:
        df_removed = pd.concat(removed_rows, ignore_index=True)
    else:
        df_removed = pd.DataFrame(columns=df.columns)

    stats = CleaningStats(
        rows_input=rows_input,
        rows_output=len(df_clean),
        rows_removed=len(df_removed),
        rows_flagged=(df_clean[FLAG_REASON_COLUMN] != "").sum(),
    )

    return df_clean, df_removed, stats

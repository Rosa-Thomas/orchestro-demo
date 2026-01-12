import pandas as pd
from dataclasses import dataclass
from config import COLUMNS, DEFAULT_BEHAVIOR, REMOVAL_REASON_COLUMN, FLAG_REASON_COLUMN


@dataclass
class CleaningStats:
    rows_input: int
    rows_output: int
    rows_removed: int
    rows_flagged: int


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

    def append_reason(mask, col, reason):
        for idx in df.index[mask]:
            existing = df.at[idx, col]
            if not existing:
                df.at[idx, col] = reason
            elif reason not in existing.split(" | "):
                df.at[idx, col] += " | " + reason

    def handle(mask, reason, action):
        nonlocal df, removed_rows

        if not mask.any():
            return

        if action == "flag":
            append_reason(mask, FLAG_REASON_COLUMN, reason)

        elif action == "remove":
            append_reason(mask, REMOVAL_REASON_COLUMN, reason)
            removed_rows.append(df.loc[mask].copy())
            df = df.loc[~mask]

    df.drop_duplicates(inplace=True)

    for col, spec in COLUMNS.items():
        if col not in df.columns:
            continue

        col_type = spec["type"]
        rules = spec.get("rules", {})

        if col_type == "string":
            df[col] = df[col].astype(str).str.strip()
            action = resolve_behavior(spec, "string", "violation")

            if "white_list" in rules:
                mask = ~df[col].isin(rules["white_list"])
                handle(mask, f"{col}: not in whitelist", action)

            if "black_list" in rules:
                mask = df[col].isin(rules["black_list"])
                handle(mask, f"{col}: in blacklist", action)

            for key in ["contains", "starts_with", "ends_with", "regex"]:
                for val in rules.get(key, []):
                    if key == "contains":
                        mask = df[col].str.contains(val, na=False)
                        reason = f"{col}: contains '{val}'"
                    elif key == "starts_with":
                        mask = df[col].str.startswith(val, na=False)
                        reason = f"{col}: starts with '{val}'"
                    elif key == "ends_with":
                        mask = df[col].str.endswith(val, na=False)
                        reason = f"{col}: ends with '{val}'"
                    else:
                        mask = df[col].str.match(val, na=False)
                        reason = f"{col}: matches regex '{val}'"

                    handle(mask, reason, action)

        elif col_type == "numeric":
            df[col] = pd.to_numeric(df[col], errors="coerce")

            missing_action = resolve_behavior(spec, "numeric", "missing")
            bounds_action = resolve_behavior(spec, "numeric", "bounds")

            if df[col].isna().any():
                handle(df[col].isna(), f"{col}: missing value", missing_action)

            if "bounds" in rules:
                lo, hi = rules["bounds"]
                if bounds_action == "clip":
                    df[col] = df[col].clip(lo, hi)
                elif bounds_action == "remove":
                    mask = (df[col] < lo) | (df[col] > hi)
                    handle(mask, f"{col}: outside global bounds", "remove")

            if "category_bounds" in rules and "Category" in df.columns:
                for cat, (lo, hi) in rules["category_bounds"].items():
                    mask = (df["Category"] == cat) & ((df[col] < lo) | (df[col] > hi))
                    if bounds_action == "clip":
                        df.loc[df["Category"] == cat, col] = df.loc[
                            df["Category"] == cat, col
                        ].clip(lo, hi)
                    elif bounds_action == "remove":
                        handle(mask, f"{col}: outside bounds for {cat}", "remove")

    df_clean = df.reset_index(drop=True)
    df_removed = pd.concat(removed_rows, ignore_index=True) if removed_rows else df.iloc[0:0]

    stats = CleaningStats(
        rows_input=int(rows_input),
        rows_output=int(len(df_clean)),
        rows_removed=int(len(df_removed)),
        rows_flagged=int((df_clean[FLAG_REASON_COLUMN] != "").sum()),
)


    return df_clean, df_removed, stats

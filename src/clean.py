import pandas as pd
from dataclasses import dataclass
from config import COLUMNS, BEHAVIOR, REMOVAL_REASON_COLUMN, FLAG_REASON_COLUMN


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


def clean_data(df: pd.DataFrame):
    df = df.copy()
    rows_input = len(df)

    # Initialize reason columns
    for col in [REMOVAL_REASON_COLUMN, FLAG_REASON_COLUMN]:
        if col not in df.columns:
            df[col] = ""

    removed_rows_list = []

    # Helper to append reasons safely
    def append_reason(df, mask, column, reason):
        for idx in df.index[mask]:
            existing = df.at[idx, column]
            if not existing:
                df.at[idx, column] = reason
            else:
                reasons = existing.split(" | ")
                if reason not in reasons:
                    df.at[idx, column] = existing + " | " + reason

    # Helper to handle violations
    def handle_violation(df, mask, reason, action):
        if not mask.any():
            return df

        if action == "remove":
            append_reason(df, mask, REMOVAL_REASON_COLUMN, reason)
            removed_rows_list.append(df.loc[mask].copy())  # save removed rows
            return df[~mask]

        elif action == "flag":
            append_reason(df, mask, FLAG_REASON_COLUMN, reason)
            return df

        # ignore
        return df

    string_strategy = BEHAVIOR.get("string_violations_strategy", "remove")
    numeric_strategy = BEHAVIOR.get("numeric_bounds_strategy", "remove")

    # Drop duplicates
    df.drop_duplicates(inplace=True)

    # Process each column
    for col, spec in COLUMNS.items():
        if col not in df.columns:
            continue

        col_type = spec.get("type")
        rules = spec.get("rules", {})

        if col_type == "string":
            df[col] = df[col].astype(str).str.strip()

            # White list
            if "white_list" in rules:
                mask = ~df[col].isin(rules["white_list"])
                df = handle_violation(df, mask, f"{col}: not in whitelist", string_strategy)

            # Black list
            if "black_list" in rules:
                mask = df[col].isin(rules["black_list"])
                df = handle_violation(df, mask, f"{col}: in blacklist", string_strategy)

            # Substring rules
            for rule_name in ["contains", "starts_with", "ends_with", "regex"]:
                if rule_name in rules:
                    values = rules[rule_name]
                    for value in values:
                        if rule_name == "contains":
                            mask = df[col].str.contains(value, na=False)
                            reason_text = f"{col}: contains '{value}'"
                        elif rule_name == "starts_with":
                            mask = df[col].str.startswith(value, na=False)
                            reason_text = f"{col}: starts with '{value}'"
                        elif rule_name == "ends_with":
                            mask = df[col].str.endswith(value, na=False)
                            reason_text = f"{col}: ends with '{value}'"
                        elif rule_name == "regex":
                            mask = df[col].str.match(value, na=False)
                            reason_text = f"{col}: matches regex '{value}'"
                        df = handle_violation(df, mask, reason_text, string_strategy)

        elif col_type == "numeric":
            df[col] = pd.to_numeric(df[col], errors="coerce")

            # Fill missing
            fill_na = rules.get("fill_na", "ignore")
            if fill_na == "remove":
                mask = df[col].isna()
                df = handle_violation(df, mask, f"{col}: missing value", "remove")
            elif fill_na == "median":
                if "Category" in df.columns:
                    df[col] = df.groupby("Category")[col].transform(lambda x: x.fillna(x.median()))
                else:
                    df[col] = df[col].fillna(df[col].median())
            elif fill_na == "mean":
                df[col] = df[col].fillna(df[col].mean())

            # Absolute values
            df[col] = df[col].abs()

            # Global bounds
            if "bounds" in rules and numeric_strategy != "ignore":
                min_val, max_val = rules["bounds"]
                if numeric_strategy == "clip":
                    df[col] = df[col].clip(min_val, max_val)
                elif numeric_strategy == "remove":
                    mask = (df[col] < min_val) | (df[col] > max_val)
                    df = handle_violation(df, mask, f"{col}: outside global bounds", "remove")

            # Category-specific bounds
            if "category_bounds" in rules and "Category" in df.columns:
                for cat, (min_val, max_val) in rules["category_bounds"].items():
                    mask = (df["Category"] == cat) & ((df[col] < min_val) | (df[col] > max_val))
                    if mask.any():
                        reason_text = f"{col}: outside bounds for category {cat}"
                        if numeric_strategy == "clip":
                            df.loc[df["Category"] == cat, col] = df.loc[df["Category"] == cat, col].clip(min_val, max_val)
                        elif numeric_strategy == "remove":
                            df = handle_violation(df, mask, reason_text, "remove")

    # Final clean / removed separation
    df_clean = df.reset_index(drop=True)
    if removed_rows_list:
        df_removed = pd.concat(removed_rows_list, ignore_index=True)
    else:
        df_removed = pd.DataFrame(columns=df.columns)

    stats = CleaningStats(
        rows_input=rows_input,
        rows_output=len(df_clean),
        rows_removed=len(df_removed),
        rows_flagged=(df_clean[FLAG_REASON_COLUMN] != "").sum(),
    )

    return df_clean, df_removed, stats

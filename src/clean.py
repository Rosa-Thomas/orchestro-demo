import pandas as pd
from dataclasses import dataclass, field
from config import COLUMNS, BEHAVIOR, SORT_COLUMNS, SORT_ORDER

@dataclass
class CleaningStats:
    rows_initial: int = 0
    rows_final: int = 0
    rows_dropped: dict = field(default_factory=dict)
    values_clipped: dict = field(default_factory=dict)
    values_filled_na: dict = field(default_factory=dict)

def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, CleaningStats]:
    df = df.copy()
    stats = CleaningStats()
    stats.rows_initial = len(df)

    df.drop_duplicates(inplace=True)

    for col, spec in COLUMNS.items():
        if col not in df.columns:
            continue

        rules = spec.get("rules", {})
        col_type = spec.get("type", "string")

        
        # String Columns        
        if col_type == "string":
            before = len(df)
            if "white_list" in rules:
                df = df[df[col].isin(rules["white_list"])]
            if "black_list" in rules:
                df = df[~df[col].isin(rules["black_list"])]
            dropped = before - len(df)
            if dropped > 0:
                stats.rows_dropped[col] = dropped

        
        # Numeric Columns    
        elif col_type == "numeric":
            # Fill missing values
            if "fill_na" in rules:
                strategy = rules["fill_na"]
                na_count = df[col].isna().sum()
                if na_count > 0:
                    if strategy == "median":
                        if "Category" in df.columns:
                            df[col] = df.groupby("Category")[col].transform(lambda x: x.fillna(x.median()))
                        else:
                            df[col] = df[col].fillna(df[col].median())
                    elif strategy == "mean":
                        if "Category" in df.columns:
                            df[col] = df.groupby("Category")[col].transform(lambda x: x.fillna(x.mean()))
                        else:
                            df[col] = df[col].fillna(df[col].mean())
                    elif strategy == "remove":
                        before = len(df)
                        df = df[df[col].notna()]
                        stats.rows_dropped[f"missing_{col}"] = before - len(df)
                        na_count = 0  # Already removed
                    stats.values_filled_na[col] = int(na_count)

            # Convert to absolute values
            df[col] = df[col].abs()

            # Apply global bounds
            if "bounds" in rules:
                min_val, max_val = rules["bounds"]
                if BEHAVIOR.get("numeric_bounds_strategy") == "clip":
                    below = (df[col] < min_val).sum()
                    above = (df[col] > max_val).sum()
                    stats.values_clipped[col] = int(below + above)
                    df[col] = df[col].clip(lower=min_val, upper=max_val)
                elif BEHAVIOR.get("numeric_bounds_strategy") == "remove":
                    before = len(df)
                    df = df[(df[col] >= min_val) & (df[col] <= max_val)]
                    stats.rows_dropped[f"{col}_out_of_bounds"] = before - len(df)

            # Apply category-specific bounds
            if "category_bounds" in rules and "Category" in df.columns:
                cat_bounds = rules["category_bounds"]
                if BEHAVIOR.get("numeric_bounds_strategy") == "clip":
                    clipped_total = 0
                    for cat, (min_val, max_val) in cat_bounds.items():
                        mask = df["Category"] == cat
                        below = (df.loc[mask, col] < min_val).sum()
                        above = (df.loc[mask, col] > max_val).sum()
                        clipped_total += below + above
                        df.loc[mask, col] = df.loc[mask, col].clip(lower=min_val, upper=max_val)
                    if clipped_total > 0:
                        stats.values_clipped[f"{col}_category_bounds"] = int(clipped_total)
                elif BEHAVIOR.get("numeric_bounds_strategy") == "remove":
                    mask_keep = pd.Series(False, index=df.index)
                    for cat, (min_val, max_val) in cat_bounds.items():
                        cat_mask = (df["Category"] == cat) & (df[col] >= min_val) & (df[col] <= max_val)
                        mask_keep = mask_keep | cat_mask
                    before = len(df)
                    df = df[mask_keep]
                    stats.rows_dropped[f"{col}_category_bounds"] = before - len(df)

    
    # Sorting
    sort_cols = SORT_COLUMNS.get("default", [])
    sort_order = SORT_ORDER.get("default", [True]*len(sort_cols))
    sort_cols = [c for c in sort_cols if c in df.columns]
    if sort_cols:
        df = df.sort_values(by=sort_cols, ascending=sort_order[:len(sort_cols)]).reset_index(drop=True)

    stats.rows_final = len(df)
    return df, stats

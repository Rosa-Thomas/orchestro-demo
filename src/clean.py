from config import WHITE_LIST, BLACK_LIST, VALUE_BOUNDS, CATEGORY_VALUE_BOUNDS, FILL_NA_STRATEGY, NUMERIC_BOUNDS_STRATEGY
import pandas as pd

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.drop_duplicates(inplace=True)

    # Fill missing numeric values
    numeric_cols = df.select_dtypes(include=["number"]).columns
    for col in numeric_cols:
        if col in FILL_NA_STRATEGY:
            strategy = FILL_NA_STRATEGY[col]
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
                df = df[df[col].notna()]

    # Convert numeric columns to absolute values
    df[numeric_cols] = df[numeric_cols].abs()

    # Strip whitespace from string/object columns
    str_cols = df.select_dtypes(include=["object"]).columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip())

    # Apply WHITE_LIST: only keep allowed values
    for col, allowed_values in WHITE_LIST.items():
        if col in df.columns:
            df = df[df[col].isin(allowed_values)]

    # Apply BLACK_LIST: remove explicitly forbidden values
    for col, forbidden_values in BLACK_LIST.items():
        if col in df.columns:
            df = df[~df[col].isin(forbidden_values)]

    # Apply global numeric bounds
    for col, bounds in VALUE_BOUNDS.items():
        if col in df.columns:
            min_val, max_val = bounds
            if NUMERIC_BOUNDS_STRATEGY == "clip":
                df[col] = df[col].clip(lower=min_val, upper=max_val)
            elif NUMERIC_BOUNDS_STRATEGY == "remove":
                df = df[(df[col] >= min_val) & (df[col] <= max_val)]

    # Apply category-specific numeric bounds
    for col, cat_bounds in CATEGORY_VALUE_BOUNDS.items():
        if col in df.columns and "Category" in df.columns:
            if NUMERIC_BOUNDS_STRATEGY == "clip":
                for cat, (min_val, max_val) in cat_bounds.items():
                    mask = df["Category"] == cat
                    df.loc[mask, col] = df.loc[mask, col].clip(lower=min_val, upper=max_val)
            elif NUMERIC_BOUNDS_STRATEGY == "remove":
                mask_keep = pd.Series(False, index=df.index)
                for cat, (min_val, max_val) in cat_bounds.items():
                    cat_mask = (df["Category"] == cat) & (df[col] >= min_val) & (df[col] <= max_val)
                    mask_keep = mask_keep | cat_mask
                df = df[mask_keep]

    # Sort rows
    sort_cols = [c for c in ["Category", "Amount"] if c in df.columns]
    if sort_cols:
        df = df.sort_values(by=sort_cols, ascending=[True]*len(sort_cols)).reset_index(drop=True)

    return df

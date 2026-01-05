from config import SORT_COLUMNS, SORT_ORDER
import pandas as pd

def sort_data(df: pd.DataFrame, dataset_key: str = "default") -> pd.DataFrame:
    # Get columns to sort by
    sort_cols = [c for c in SORT_COLUMNS.get(dataset_key, []) if c in df.columns]

    # Get ascending order (default all True)
    ascending = SORT_ORDER.get(dataset_key, [True]*len(sort_cols))
    ascending = ascending[:len(sort_cols)]  # ensure lengths match

    if sort_cols:
        df = df.sort_values(by=sort_cols, ascending=ascending).reset_index(drop=True)
    
    return df

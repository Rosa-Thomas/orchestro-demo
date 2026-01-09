import pandas as pd
from config import SORTING


def sort_data(df: pd.DataFrame, dataset_key: str = "default") -> pd.DataFrame:
    df = df.copy()

    sort_spec = SORTING.get(dataset_key)
    if not sort_spec:
        return df

    columns = [c for c in sort_spec.get("columns", []) if c in df.columns]
    ascending = sort_spec.get("ascending", [True] * len(columns))

    ascending = ascending[:len(columns)]

    if columns:
        df = df.sort_values(by=columns, ascending=ascending).reset_index(drop=True)

    return df


import pandas as pd
from pathlib import Path

def load_raw_data(path="data/raw/sample_data.csv"):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    df = pd.read_csv(p)
    return df

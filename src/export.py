
from pathlib import Path

def export_clean_data(df, path="data/processed/cleaned_data.csv"):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False)

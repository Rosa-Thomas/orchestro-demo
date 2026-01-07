from dataclasses import asdict
import json
from ingest import load_raw_data
from clean import clean_data
from quality_checks import run_quality_checks
from transform import compute_kpis
from export import export_clean_data
from sort import sort_data
from pathlib import Path
from config import DEFAULT_PATHS

def generate_report(quality, kpis, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write("# Quality Report\n\n")
        f.write("## Quality Checks\n")
        for k, v in quality.items():
            f.write(f"- {k}: {v}\n")
        f.write("\n## KPIs\n")
        for k, v in kpis.items():
            f.write(f"- {k}: {v}\n")

def main():
    df_raw = load_raw_data(DEFAULT_PATHS["input"])

    df_clean, df_removed, cleaning_stats = clean_data(df_raw)

    quality_raw = run_quality_checks(df_raw)
    quality_clean = run_quality_checks(df_clean)

    kpis_raw = compute_kpis(df_raw)
    kpis_clean = compute_kpis(df_clean)

    df_sorted = sort_data(df_clean)

    export_clean_data(df_sorted, DEFAULT_PATHS["output_clean"])

    Path(DEFAULT_PATHS["output_removed"]).parent.mkdir(parents=True, exist_ok=True)
    df_removed.to_csv(DEFAULT_PATHS["output_removed"], index=False)

    generate_report(quality_clean, kpis_clean, DEFAULT_PATHS["report_clean"])
    generate_report(quality_raw, kpis_raw, DEFAULT_PATHS["report_raw"])

    Path(DEFAULT_PATHS["cleaning_stats"]).parent.mkdir(parents=True, exist_ok=True)
    with open(DEFAULT_PATHS["cleaning_stats"], "w") as f:
        json.dump(asdict(cleaning_stats), f, indent=2)

    print("Pipeline executed successfully.")

if __name__ == "__main__":
    main()

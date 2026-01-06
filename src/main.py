
from dataclasses import asdict
import json
from ingest import load_raw_data
from clean import clean_data
from quality_checks import run_quality_checks
from transform import compute_kpis
from export import export_clean_data
from sort import sort_data
from pathlib import Path

def generate_report(quality, kpis, path="reports/quality_report.md"):
    Path("reports").mkdir(exist_ok=True)
    with open(path, "w") as f:
        f.write("# Quality Report\n\n")
        f.write("## Quality Checks\n")
        for k, v in quality.items():
            f.write(f"- {k}: {v}\n")
        f.write("\n## KPIs\n")
        for k, v in kpis.items():
            f.write(f"- {k}: {v}\n")

def main():
    df_raw = load_raw_data()

    # Run cleaning and track stats
    df_clean, cleaning_stats = clean_data(df_raw)

    # Quality checks
    quality_raw = run_quality_checks(df_raw)
    quality_clean = run_quality_checks(df_clean)

    # Compute KPIs
    kpis_raw = compute_kpis(df_raw)
    kpis_clean = compute_kpis(df_clean)

    # Sort cleaned data
    df_sorted = sort_data(df_clean)

    # Export
    export_clean_data(df_sorted)

    # Reports
    generate_report(quality_clean, kpis_clean, path="reports/quality_report.md")
    generate_report(quality_raw, kpis_raw, path="reports/quality_report_raw.md")

    # Optional: export cleaning stats
    with open("reports/cleaning_stats.json", "w") as f:
        json.dump(asdict(cleaning_stats), f, indent=2)

    print("Pipeline executed successfully.")


if __name__ == "__main__":
    main()

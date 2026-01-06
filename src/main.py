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

def main(input_path=None, output_path=None, report_path_clean=None, report_path_raw=None, stats_path=None):
    # Use default paths if none provided
    input_path = input_path or DEFAULT_PATHS["input"]
    output_path = output_path or DEFAULT_PATHS["output"]
    report_path_clean = report_path_clean or DEFAULT_PATHS["report"]
    report_path_raw = report_path_raw or report_path_clean.replace(".md", "_raw.md")
    stats_path = stats_path or "reports/cleaning_stats.json"

    # Load raw data
    df_raw = load_raw_data(input_path)

    # Clean data and track stats
    df_clean, cleaning_stats = clean_data(df_raw)

    # Run quality checks
    quality_raw = run_quality_checks(df_raw)
    quality_clean = run_quality_checks(df_clean)

    # Compute KPIs
    kpis_raw = compute_kpis(df_raw)
    kpis_clean = compute_kpis(df_clean)

    # Sort cleaned data
    df_sorted = sort_data(df_clean)

    # Export cleaned data
    export_clean_data(df_sorted, output_path)

    # Generate reports
    generate_report(quality_clean, kpis_clean, report_path_clean)
    generate_report(quality_raw, kpis_raw, report_path_raw)

    # Export cleaning stats
    Path(stats_path).parent.mkdir(parents=True, exist_ok=True)
    with open(stats_path, "w") as f:
        json.dump(asdict(cleaning_stats), f, indent=2)

    print("Pipeline executed successfully.")
    print(f"Cleaned data saved to: {output_path}")
    print(f"Reports saved to: {report_path_clean} and {report_path_raw}")
    print(f"Cleaning stats saved to: {stats_path}")

if __name__ == "__main__":
    main()

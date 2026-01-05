
from ingest import load_raw_data
from clean import clean_data
from quality_checks import run_quality_checks
from transform import compute_kpis
from export import export_clean_data
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
    df_clean = clean_data(df_raw)
    quality_raw = run_quality_checks(df_raw)
    kpis_raw = compute_kpis(df_raw)
    quality = run_quality_checks(df_clean)
    kpis = compute_kpis(df_clean)
    export_clean_data(df_clean)
    generate_report(quality, kpis)
    generate_report(quality_raw, kpis_raw, path="reports/quality_report_raw.md")
    print("Pipeline executed successfully.")

if __name__ == "__main__":
    main()

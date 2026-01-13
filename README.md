# Data Cleaning Pipeline

This repository contains a configurable **data cleaning and processing pipeline** designed to validate, clean, and transform raw datasets. It supports automated removal and flagging of invalid data, quality checks, KPI computation, and reporting.

---

## Features

* **Flexible column-based cleaning rules**

  * Handles both numeric and string columns
  * Supports whitelists, blacklists, regex, bounds, and category-specific rules
* **Configurable default behaviors**

  * Missing values can be flagged or removed
  * Numeric out-of-bounds values can be clipped or removed
  * String violations can be flagged or removed
* **Row-level tracking**

  * Tracks rows removed and flagged, with reasons
* **Quality checks & KPI computation**

  * Evaluates raw and cleaned datasets
* **Automated reporting**

  * Generates Markdown quality reports
  * Saves cleaning statistics as JSON
* **Sorting & export**

  * Cleaned and removed data exported in CSV format
  * Data can be sorted by configurable columns

---

## Installation

1. Clone this repository:

```bash
git clone <repo_url>
cd <repo_folder>
```

2. Install required dependencies:

```bash
pip install -r requirements.txt
```

---

## Configuration

All cleaning rules and behaviors are defined in `src/config.py`:

* `COLUMNS`: Defines columns, types, rules, and behavior overrides
* `DEFAULT_BEHAVIOR`: Default actions for missing values, violations, and numeric bounds
* `REMOVAL_REASON_COLUMN` & `FLAG_REASON_COLUMN`: Columns used to track issues
* `SORTING`: Default sorting rules
* `DEFAULT_PATHS`: File paths for input, output, reports, and statistics

You can modify these settings to fit your dataset.

---

## Usage

The main entry point is `src/main.py`:

```bash
python src/main.py
```

### Pipeline Steps:

1. **Load raw data** from `DEFAULT_PATHS["input"]`
2. **Clean data** according to rules in `config.py`
3. **Run quality checks** on both raw and cleaned data
4. **Compute KPIs** for analysis
5. **Sort data** based on configurable columns
6. **Export cleaned data** and removed rows
7. **Generate reports** in Markdown and JSON formats

After execution, the following files will be created:

| Path                              | Description                      |
| --------------------------------- | -------------------------------- |
| `data/processed/cleaned_data.csv` | CSV of cleaned data              |
| `data/processed/removed_rows.csv` | CSV of removed rows              |
| `reports/quality_report.md`       | Quality report of cleaned data   |
| `reports/quality_report_raw.md`   | Quality report of raw data       |
| `reports/cleaning_stats.json`     | JSON with statistics of cleaning |

---

## Cleaning Rules

### String Columns

* Whitelist & blacklist enforcement
* Regex, contains, starts with, ends with checks
* Default violation behavior: flag or remove

### Numeric Columns

* Numeric conversion & missing value handling
* Global and category-specific bounds
* Actions: clip, flag, remove

**Special Notes:**

* Numbers outside global bounds are removed
* Category A and B have their own limits that may override global bounds
* Other numeric columns still use default behavior

### Example

A column configuration might look like:

```python
"Category": {
    "type": "string",
    "rules": {
        "white_list": ["A", "B"],
        "contains": ["X"]
    },
    "behavior": {
        "violation": "remove"
    }
}
```

This configuration removes any category not in `['A', 'B']` or containing `'X'`.

---

## Project Structure

```
orchestro-demo/
├── data/
│   ├── raw/
│   │   └── sample_data.csv             # Raw input CSV files
│   └── processed/
│       ├── cleaned_data.csv            # Cleaned output
│       └── removed_rows.csv            # Rows removed with reasons
├── reports/
│   ├── quality_report.md               # Cleaned data report
│   ├── quality_report_raw.md           # Raw data report
│   └── cleaning_stats.json             # Stats about cleaning (counts, etc.)
├── src/
│   ├── __init__.py
│   ├── main.py                         # Orchestrates the full pipeline
│   ├── config.py                       # Configuration (rules, behavior, paths)
│   ├── ingest.py                       # Loads raw data into pandas DataFrame
│   ├── clean.py                        # Cleaning engine (removals, flagging)
│   ├── quality_checks.py               # Runs quality checks & generates report data
│   ├── transform.py                    # Computes KPIs or other metrics
│   ├── export.py                       # Exports cleaned data & removed rows
│   └── sort.py                         # Sorts DataFrames according to config
└── README.md                            # Documentation for project
```

---

## Statistics Tracking

After cleaning, the pipeline generates a `CleaningStats` object containing:

* `rows_input`: Total rows in raw dataset
* `rows_output`: Total rows after cleaning
* `rows_removed`: Number of removed rows
* `rows_flagged`: Number of flagged rows

This information is exported as JSON for auditing.

--

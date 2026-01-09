DEFAULT_BEHAVIOR = {
    "string": {
        "violation": "flag",
    },
    "numeric": {
        "bounds": "clip",
        "missing": "ignore",
    }
}

COLUMNS = {
    "ID": {
        "type": "numeric",
        "rules": {
            "fill_na": "remove",
        }
    },
    "Category": {
        "type": "string",
        "rules": {
            "white_list": ["A", "B", "C"],
        },
        "behavior": {
            "violation": "remove"
        }
    },
    "Description": {
        "type": "string",
        "rules": {
            "black_list": ["Invalid", "Unknown", "Chargeback"],
        },
        "behavior": {
            "violation": "flag"
        }
    },
    "Amount": {
        "type": "numeric",
        "rules": {
            "fill_na": "remove",
            "bounds": (0, 200),
            "category_bounds": {
                "A": (50, 200),
                "B": (100, 250),
            }
        },
        "behavior": {
            "bounds": "remove",
            "missing": "remove",
        }
    }
}

REMOVAL_REASON_COLUMN = "Removal Reason"
FLAG_REASON_COLUMN = "Flag Reason"

SORTING = {
    "default": {
        "columns": ["Category", "Amount"],
        "ascending": [True, True],
    }
}

DEFAULT_PATHS = {
    "input": "data/raw/sample_data.csv",
    "output_clean": "data/processed/cleaned_data.csv",
    "output_removed": "data/processed/removed_rows.csv",
    "report_clean": "reports/quality_report.md",
    "report_raw": "reports/quality_report_raw.md",
    "cleaning_stats": "reports/cleaning_stats.json",
}

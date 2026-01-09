 
# Column-level rules (human-readable)
COLUMNS = {
    "ID": {
        "type": "numeric",
        "rules": {
            "fill_na": "remove"  # median | mean | remove | ignore
        }
    },
    "Category": {
        "type": "string",
        "rules": {
            "white_list": ["A", "B", "C"]
        }
    },
    "Description": {
        "type": "string",
        "rules": {
            "black_list": ["Invalid", "Unknown", "Chargeback"]
        }
    },
    "Amount": {
        "type": "numeric",
        "rules": {
            "fill_na": "remove",  # median | mean | remove | ignore
            "bounds": (0, 200),   # global bounds
            "category_bounds": {   # optional per-category bounds
                "A": (50, 200),
                "B": (100, 250),
            }
        }
    }
}
# Special column names for marking removed/flagged rows
REMOVAL_REASON_COLUMN = "Removal Reason"
FLAG_REASON_COLUMN = "Flag Reason"

 
# Global behavior switches
BEHAVIOR = {
    "numeric_bounds_strategy": "clip",      # remove | clip | ignore
    "string_violations_strategy": "flag",   # remove | flag | ignore
}
# Sorting rules
SORT_COLUMNS = {
    "default": ["Category", "Amount"]
}

SORT_ORDER = {
    "default": [True, True]  # True=ascending, False=descending
}

# Default paths for operational script 
DEFAULT_PATHS = {
    "input": "data/raw/sample_data.csv",

    "output_clean": "data/processed/cleaned_data.csv",
    "output_removed": "data/processed/removed_rows.csv",

    "report_clean": "reports/quality_report.md",
    "report_raw": "reports/quality_report_raw.md",

    "cleaning_stats": "reports/cleaning_stats.json",
}


 
# Column-level rules (human-readable)
COLUMNS = {
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
 
# Global behavior switches
BEHAVIOR = {
    "numeric_bounds_strategy": "clip",  # remove | clip | ignore
    "string_violations_strategy": "remove",  # remove | flag
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
    "output": "data/processed/cleaned_data.csv",
    "report": "reports/quality_report.md"
}

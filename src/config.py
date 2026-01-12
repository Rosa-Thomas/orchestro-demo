# This config is designed to stress-test the cleaning engine

DEFAULT_BEHAVIOR = {
    "string": {
        "violation": "flag",     # default: strings are flagged
    },
    "numeric": {
        "bounds": "clip",       # default: numbers get clipped
        "missing": "flag",      # default: missing numbers get flagged
    }
}


COLUMNS = {

    # Should never be missing; tests missing+remove
    "ID": {
        "type": "numeric",
        "rules": {
            "fill_na": "ignore",
        },
        "behavior": {
            "missing": "remove",
        }
    },

    # Tests whitelist + override remove
    "Category": {
        "type": "string",
        "rules": {
            "white_list": ["A", "B"],
            "contains": ["X"],      # conflicting: something could be A but still contain X
        },
        "behavior": {
            "violation": "remove"
        }
    },

    # Tests blacklist + regex + default flagging
    "Description": {
        "type": "string",
        "rules": {
            "black_list": ["Invalid", "Chargeback"],
            "regex": ["^ERR", ".*FAIL.*"],
            "contains": ["test"],
        }
        # no behavior → uses DEFAULT_BEHAVIOR (flag)
    },

    # Tests overlapping numeric bounds
    "Amount": {
        "type": "numeric",
        "rules": {
            "bounds": (0, 100),
            "category_bounds": {
                "A": (10, 50),
                "B": (40, 120),   # overlaps global bounds
            }
        },
        "behavior": {
            "bounds": "remove"   # override default clip
        }
    },

    # Tests missing numeric default behavior (flag)
    "Tax": {
        "type": "numeric",
        "rules": {
            "bounds": (0, 30)
        }
        # missing behavior → uses DEFAULT_BEHAVIOR
    },

    # Tests string rules that overlap heavily
    "Notes": {
        "type": "string",
        "rules": {
            "contains": ["bad", "error"],
            "starts_with": ["!"],
            "ends_with": ["?"],
        },
        "behavior": {
            "violation": "flag"
        }
    }
}


REMOVAL_REASON_COLUMN = "Removal Reason"
FLAG_REASON_COLUMN = "Flag Reason"


SORTING = {
    "default": {
        "columns": ["Category", "Amount", "ID"],
        "ascending": [True, False, True],
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

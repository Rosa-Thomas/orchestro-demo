# Configuration for data cleaning and validation
WHITE_LIST = { 
    "Category": ["A", "B", "C"],
}
BLACK_LIST = {
    "Description": ["Invalid", "Unknown", "Chargeback"],
}

VALUE_BOUNDS = {
    "Amount": (0, 200),
}
# Strategy (median, mean, remove) for filling NA values per column
FILL_NA_STRATEGY = {
    "Amount": "remove",
}

# Category-specific numeric bounds
CATEGORY_VALUE_BOUNDS = {
    "Amount": {
        "A": (50, 200),
        "B": (100, 250),
        "C": (60, 160),
    }
}
 # Remove or set to nearest bound (clip) for out-of-bounds numeric values
NUMERIC_BOUNDS_STRATEGY = "remove"  # or "clip"

# Columns to sort by per dataset
SORT_COLUMNS = {
    "default": ["Category", "Amount"], 
}

# Sort order corresponding to SORT_COLUMNS (True=ascending, False=descending)
SORT_ORDER = {
    "default": [True, True],
}

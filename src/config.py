STRING_BOUNDS = { 
    "Category": ["A", "B", "C"],
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
        "A": (100, 110),
        "B": (100, 250),
        "C": (160, 160),
    }
}
 # Remove or set to nearest bound (clip) for out-of-bounds numeric values
NUMERIC_BOUNDS_STRATEGY = "remove"  # or "clip"
# Quality Report

## Quality Checks
- missing_values: {'ID': 1, 'Category': 2, 'Description': 1, 'Amount': 2, 'Tax': 4, 'Notes': 1}
- negative_values: {'ID': 0, 'Amount': 0, 'Tax': 0}
- invalid_strings: {'Category': ['AX', 'BX'], 'Description': ['Chargeback', 'Invalid']}
- out_of_bounds: {'Amount': {'below_global_min': 0, 'above_global_max': 5, 'category_bounds': {'A': {'below_min': 4, 'above_max': 5}, 'B': {'below_min': 2, 'above_max': 1}}}, 'Tax': {'below_global_min': 0, 'above_global_max': 2}}

## KPIs
- total_amount: 2121.0
- avg_amount: 48.20454545454545
- count_by_category: {'A': 26, 'B': 16, 'AX': 1, 'BX': 1}

# formulas/averages.py
"""
Utility functions for calculating averages from generated performance reports.
"""
from decimal import Decimal # Needed for checking numeric types

# Note: The original file had three almost identical functions.
# We can combine them into one generic function.

# generate_medium_performance: Calculates the average daily performance value for each key from a performance report.
# Input: dict like { key: [daily_value1, daily_value2, ...], ...} where values are numeric (int, float, Decimal)
# Output: dict { key: average_value_float, ... }
def generate_medium_performance(performance_data):
    """
    Calculates the average daily value for each entry in a performance report.

    Args:
        performance_data (dict): A dictionary where keys are identifiers (e.g., employee names)
                                 and values are lists of daily numeric performance figures.
                                 Example: {"(1) John Doe": [10.5, 12.0, 8.5], ...}

    Returns:
        dict: A dictionary with the same keys, where values are the calculated
              average performance, rounded to 2 decimal places (float).
              Returns 0.0 for entries with no valid numeric data or empty lists.
    """
    medium_performance_data = {}
    if not isinstance(performance_data, dict):
        print("AVERAGES Warning: Input must be a dictionary.")
        return {}

    for key, value_list in performance_data.items():
        if isinstance(value_list, list) and len(value_list) > 0:
            # Filter only numeric types to avoid errors during sum()
            numeric_values = [v for v in value_list if isinstance(v, (int, float, Decimal))]
            if len(numeric_values) > 0:
                 # Calculate average. Convert sum to float before division if mixing types,
                 # or handle potential Decimal averaging separately if precision needed.
                 # Sticking to float output as per original functions.
                 try:
                     average = float(sum(numeric_values)) / len(numeric_values)
                     medium_performance_data[key] = round(average, 2)
                 except TypeError:
                      print(f"AVERAGES Warning: Could not calculate average for key '{key}' due to non-numeric data.")
                      medium_performance_data[key] = 0.0
            else:
                 # List contained only non-numeric items
                 medium_performance_data[key] = 0.0
        else:
             # Handle empty list or non-list input for a key
             medium_performance_data[key] = 0.0

    return medium_performance_data

# You can create aliases if you want to keep the old names for backward compatibility
# or specific use cases, although using the generic one is cleaner.
generate_medium_sales = generate_medium_performance
generate_medium_sc_sales = generate_medium_performance
generate_medium_sales_performance = generate_medium_performance
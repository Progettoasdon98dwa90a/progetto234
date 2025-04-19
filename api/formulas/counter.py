# formulas/counter.py
"""
Functions related to people counter data (Ingressi, Traffico Esterno, Tasso Attrazione)
and derived KPIs like Conversion Rate.
"""
from datetime import datetime, timedelta
from decimal import Decimal # Keep if TA can be decimal

from api.models import Import, Branch # Assuming models are accessible

# Import functions from other modules needed for calculations
from api.formulas.receipts import get_total_scontrini_single_date


# get_number_ingressi_single_date: Retrieves the number of entries ('(Ing) Ingressi') for a branch on a single date from counter data.
# Output: int (number of entries) or 0 if branch/import/data not found or invalid.
def get_number_ingressi_single_date(branch_id, date):
    # ... (copy function code from original file) ...
    branch = None
    import_obj = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print(f"COUNTER Ingressi: No branch found with ID {branch_id}")
        return 0

    try:
        import_obj = Import.objects.get(import_date=date, branch=branch, import_type="counter_data")
    except Import.DoesNotExist:
        # print(f"COUNTER Ingressi: No counter_data import found for branch {branch_id} on {date}")
        return 0 # No counter data for this day
    except Import.MultipleObjectsReturned:
        print(f"COUNTER Ingressi Warning: Multiple 'counter_data' imports found for branch {branch_id} on {date}. Using first one.")
        import_obj = Import.objects.filter(import_date=date, branch=branch, import_type="counter_data").first()
        if not import_obj: return 0

    data = import_obj.data
    # Assuming counter data is a list containing ONE dictionary
    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        ingressi_str = data[0].get('(Ing) Ingressi')
        if ingressi_str is not None:
            try:
                # Handle potential non-integer values if necessary, clean first
                ingressi_cleaned = str(ingressi_str).split('.')[0] # Take integer part if float
                return int(ingressi_cleaned)
            except (ValueError, TypeError):
                 print(f"COUNTER Ingressi Warning: Invalid '(Ing) Ingressi' value '{ingressi_str}' for branch {branch_id} on {date}")
                 return 0
        else:
             # print(f"COUNTER Ingressi Info: Key '(Ing) Ingressi' missing in counter data for branch {branch_id} on {date}")
             return 0
    else:
        print(f"COUNTER Ingressi Warning: Unexpected counter data structure for branch {branch_id} on {date}")
        return 0

# get_traffico_esterno_single_date: Retrieves the external traffic ('(Est) Traffico Esterno') for a branch on a single date.
# Output: int (external traffic count) or 0 if not found/invalid.
def get_traffico_esterno_single_date(branch_id, date):
    # ... (copy function code from original file) ...
    branch = None
    import_obj = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print(f"COUNTER Traffico: No branch found with ID {branch_id}")
        return 0

    try:
        import_obj = Import.objects.get(import_date=date, branch=branch, import_type="counter_data")
    except Import.DoesNotExist:
        # print(f"COUNTER Traffico: No counter_data import found for branch {branch_id} on {date}")
        return 0
    except Import.MultipleObjectsReturned:
        print(f"COUNTER Traffico Warning: Multiple 'counter_data' imports for branch {branch_id} on {date}. Using first.")
        import_obj = Import.objects.filter(import_date=date, branch=branch, import_type="counter_data").first()
        if not import_obj: return 0

    data = import_obj.data
    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        traffico_str = data[0].get('(Est) Traffico Esterno')
        if traffico_str is not None:
            try:
                traffico_cleaned = str(traffico_str).split('.')[0]
                return int(traffico_cleaned)
            except (ValueError, TypeError):
                 print(f"COUNTER Traffico Warning: Invalid '(Est) Traffico Esterno' value '{traffico_str}' for branch {branch_id} on {date}")
                 return 0
        else:
            # print(f"COUNTER Traffico Info: Key '(Est) Traffico Esterno' missing for branch {branch_id} on {date}")
            return 0
    else:
        print(f"COUNTER Traffico Warning: Unexpected counter data structure for branch {branch_id} on {date}")
        return 0

# get_tasso_attrazione_single_date: Retrieves the attraction rate ('(TA) Tasso di Attrazione') for a branch on a single date.
# Output: float (attraction rate percentage) or 0.0 if not found/invalid. Assume it's a percentage.
def get_tasso_attrazione_single_date(branch_id, date):
    # ... (copy function code from original file) ...
    branch = None
    import_obj = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print(f"COUNTER TA: No branch found with ID {branch_id}")
        return 0.0

    try:
        import_obj = Import.objects.get(import_date=date, branch=branch, import_type="counter_data")
    except Import.DoesNotExist:
        # print(f"COUNTER TA: No counter_data import found for branch {branch_id} on {date}")
        return 0.0
    except Import.MultipleObjectsReturned:
        print(f"COUNTER TA Warning: Multiple 'counter_data' imports for branch {branch_id} on {date}. Using first.")
        import_obj = Import.objects.filter(import_date=date, branch=branch, import_type="counter_data").first()
        if not import_obj: return 0.0

    data = import_obj.data
    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        tasso_str = data[0].get('(TA) Tasso di Attrazione')
        if tasso_str is not None:
            try:
                # Assume TA is stored as percentage string, potentially with '%'
                tasso_cleaned = str(tasso_str).replace('%', '').replace(',', '.')
                return float(tasso_cleaned)
            except (ValueError, TypeError):
                 print(f"COUNTER TA Warning: Invalid '(TA) Tasso di Attrazione' value '{tasso_str}' for branch {branch_id} on {date}")
                 return 0.0
        else:
             # print(f"COUNTER TA Info: Key '(TA) Tasso di Attrazione' missing for branch {branch_id} on {date}")
             return 0.0
    else:
        print(f"COUNTER TA Warning: Unexpected counter data structure for branch {branch_id} on {date}")
        return 0.0

# get_number_ingressi_date_range: Calculates the total number of entries ('(Ing) Ingressi') for a branch over a date range.
# Output: int (total entries) or 0 if not found.
def get_number_ingressi_date_range(branch_id, start_date, end_date):
    # ... (copy function code from original file) ...
    branch = None
    import_objs_qs = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print(f"COUNTER Ingressi Range: No branch found with ID {branch_id}")
        return 0

    try:
        import_objs_qs = Import.objects.filter(import_date__range=(start_date, end_date), branch=branch, import_type="counter_data")
    except Exception as e:
        print(f"COUNTER Ingressi Range Error fetching imports for branch {branch_id}: {e}")
        return 0

    grand_total = 0

    if import_objs_qs.exists():
        for import_obj in import_objs_qs:
            data = import_obj.data
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                ingressi_str = data[0].get('(Ing) Ingressi')
                if ingressi_str is not None:
                    try:
                        ingressi_cleaned = str(ingressi_str).split('.')[0]
                        grand_total += int(ingressi_cleaned)
                    except (ValueError, TypeError):
                        print(f"COUNTER Ingressi Range Warning: Invalid value '{ingressi_str}' skipped on {import_obj.import_date} for branch {branch_id}")
            # else: Unexpected structure, adds 0

    return grand_total

# get_traffico_esterno_date_range: Calculates the total external traffic ('(Est) Traffico Esterno') for a branch over a date range.
# Output: int (total external traffic) or 0 if not found.
def get_traffico_esterno_date_range(branch_id, start_date, end_date):
    # ... (copy function code from original file) ...
    branch = None
    import_objs_qs = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print(f"COUNTER Traffico Range: No branch found with ID {branch_id}")
        return 0

    try:
        import_objs_qs = Import.objects.filter(import_date__range=(start_date, end_date), branch=branch, import_type="counter_data")
    except Exception as e:
        print(f"COUNTER Traffico Range Error fetching imports for branch {branch_id}: {e}")
        return 0

    grand_total = 0

    if import_objs_qs.exists():
        for import_obj in import_objs_qs:
            data = import_obj.data
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                traffico_str = data[0].get('(Est) Traffico Esterno')
                if traffico_str is not None:
                    try:
                        traffico_cleaned = str(traffico_str).split('.')[0]
                        grand_total += int(traffico_cleaned)
                    except (ValueError, TypeError):
                        print(f"COUNTER Traffico Range Warning: Invalid value '{traffico_str}' skipped on {import_obj.import_date} for branch {branch_id}")
            # else: Unexpected structure, adds 0

    return grand_total


# get_tasso_attrazione_date_range: Calculates the AVERAGE attraction rate ('(TA) Tasso di Attrazione') for a branch over a date range.
# Note: Changed from SUM to AVERAGE as summing rates is usually less meaningful.
# Output: float (average rate percentage) or 0.0 if not found or no valid data.
def get_tasso_attrazione_date_range(branch_id, start_date, end_date):
    # ... (copy function code from original file, modified for average) ...
    branch = None
    import_objs_qs = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print(f"COUNTER TA Range: No branch found with ID {branch_id}")
        return 0.0

    try:
        import_objs_qs = Import.objects.filter(import_date__range=(start_date, end_date), branch=branch, import_type="counter_data")
    except Exception as e:
        print(f"COUNTER TA Range Error fetching imports for branch {branch_id}: {e}")
        return 0.0

    total_rate = 0.0 # Sum of valid rates
    valid_days_count = 0 # Count of days with valid rate data

    if import_objs_qs.exists():
        for import_obj in import_objs_qs:
            data = import_obj.data
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                tasso_str = data[0].get('(TA) Tasso di Attrazione')
                if tasso_str is not None:
                    try:
                        tasso_cleaned = str(tasso_str).replace('%', '').replace(',', '.')
                        rate_value = float(tasso_cleaned)
                        total_rate += rate_value
                        valid_days_count += 1
                    except (ValueError, TypeError):
                        print(f"COUNTER TA Range Warning: Invalid value '{tasso_str}' skipped on {import_obj.import_date} for branch {branch_id}")
            # else: Unexpected structure, skip day

    if valid_days_count > 0:
        return total_rate / valid_days_count
    else:
        return 0.0


# generate_ingressi_branch_report: Generates a report of daily entries ('(Ing) Ingressi') for a branch over a date range.
# Output: dict { "YYYY-MM-DD": entries_int, ... }. Returns empty dict if error.
def generate_ingressi_branch_report(branch_id, start_date, end_date):
    # ... (copy function code from original file) ...
    # This function can be optimized by fetching all data at once
    try:
        Branch.objects.get(id=branch_id) # Check if branch exists
    except Branch.DoesNotExist:
        print(f"COUNTER Ingressi Report: No branch found with ID {branch_id}")
        return {}

    # Validate dates and create range
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        if start_date_obj > end_date_obj: return {}
    except ValueError:
        print("COUNTER Ingressi Report Error: Date format error. Please use YYYY-MM-DD.")
        return {}

    num_days = (end_date_obj - start_date_obj).days + 1
    date_range = [(start_date_obj + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)]

    # Initialize report
    report_data = {date_str: 0 for date_str in date_range}

    # Populate report by calling single-day function
    for date_str in date_range:
        report_data[date_str] = get_number_ingressi_single_date(branch_id, date_str)

    # report_data = dict(sorted(report_data.items())) # Sort if needed
    return report_data

# generate_branch_traffico_esterno_report: Generates a report of daily external traffic ('(Est) Traffico Esterno') for a branch over a date range.
# Output: dict { "YYYY-MM-DD": traffic_int, ... }. Returns empty dict if error.
def generate_branch_traffico_esterno_report(branch_id, start_date, end_date):
    # ... (copy function code from original file) ...
    try:
        Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print(f"COUNTER Traffico Report: No branch found with ID {branch_id}")
        return {}

    # Validate dates and create range
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        if start_date_obj > end_date_obj: return {}
    except ValueError:
        print("COUNTER Traffico Report Error: Date format error. Please use YYYY-MM-DD.")
        return {}

    num_days = (end_date_obj - start_date_obj).days + 1
    date_range = [(start_date_obj + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)]

    # Initialize report
    report_data = {date_str: 0 for date_str in date_range}

    # Populate report
    for date_str in date_range:
        report_data[date_str] = get_traffico_esterno_single_date(branch_id, date_str)

    # report_data = dict(sorted(report_data.items())) # Sort if needed
    return report_data

# generate_branch_tasso_attrazione_report: Generates a report of daily attraction rate ('(TA) Tasso di Attrazione') for a branch over a date range.
# Output: dict { "YYYY-MM-DD": rate_float, ... }. Returns empty dict if error.
def generate_branch_tasso_attrazione_report(branch_id, start_date, end_date):
    # ... (copy function code from original file) ...
    try:
        Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print(f"COUNTER TA Report: No branch found with ID {branch_id}")
        return {}

    # Validate dates and create range
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        if start_date_obj > end_date_obj: return {}
    except ValueError:
        print("COUNTER TA Report Error: Date format error. Please use YYYY-MM-DD.")
        return {}

    num_days = (end_date_obj - start_date_obj).days + 1
    date_range = [(start_date_obj + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)]

    # Initialize report
    report_data = {date_str: 0.0 for date_str in date_range} # Initialize with float 0.0

    # Populate report
    for date_str in date_range:
        report_data[date_str] = get_tasso_attrazione_single_date(branch_id, date_str)

    # report_data = dict(sorted(report_data.items())) # Sort if needed
    return report_data

# --- Conversion Rate Functions ---

# get_conversion_rate_single_date: Calculates the conversion rate ((total_scontrini / number_ingressi) * 100) for a branch on a single date.
# Output: float (conversion rate percentage) or 0.0 if calculation not possible (e.g., division by zero).
def get_conversion_rate_single_date(branch_id, date):
    # ... (copy function code from original file) ...
    # Uses get_number_ingressi_single_date (from this module)
    # Uses get_total_scontrini_single_date (imported from formulas.scontrini)

    ingressi_daily = get_number_ingressi_single_date(branch_id, date) # Returns int
    scontrini_daily = get_total_scontrini_single_date(branch_id, date) # Returns float

    conversion_rate = 0.0 # Default to float 0.0

    # Ensure inputs are valid numbers and avoid division by zero
    if isinstance(ingressi_daily, (int, float)) and isinstance(scontrini_daily, (int, float)):
        if ingressi_daily > 0: # Check for positive ingressi
             try:
                 # Calculate conversion rate
                 conversion_rate_fraction = float(scontrini_daily) / float(ingressi_daily)
                 conversion_rate_percent = conversion_rate_fraction * 100.0
                 # Ensure rate is not negative
                 conversion_rate = max(conversion_rate_percent, 0.0)
             except ZeroDivisionError:
                 conversion_rate = 0.0 # Should be caught by ingressi_daily > 0, but safe fallback
        # else: ingressi is 0 or less, conversion rate remains 0.0
    else:
        # print(f"CONV RATE Warning: Could not calculate for Branch {branch_id} on {date} due to invalid inputs (Ing: {ingressi_daily}, Sco: {scontrini_daily})")
        conversion_rate = 0.0 # One or both inputs were not valid numbers

    # Optional: Round the result if desired
    # return round(conversion_rate, 2)
    return conversion_rate


# generate_branch_report_conversion_rate: Generates a report of the daily conversion rate for a branch over a date range.
# Output: dict { "YYYY-MM-DD": conversion_rate_float, ... }. Returns empty dict if error.
def generate_branch_report_conversion_rate(branch_id, start_date_str, end_date_str):
    # ... (copy function code from original file) ...
    try:
        Branch.objects.get(id=branch_id) # Check if branch exists
    except Branch.DoesNotExist:
        print(f"CONV RATE Report: No branch found with ID {branch_id}")
        return {}

    # Validate dates and create range
    try:
        start_date_obj = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        if start_date_obj > end_date_obj:
             print("CONV RATE Report Error: Start date cannot be after end date.")
             return {}
    except ValueError:
        print("CONV RATE Report Error: Date format error. Please use YYYY-MM-DD.")
        return {}

    num_days = (end_date_obj - start_date_obj).days + 1
    date_range = [(start_date_obj + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)]

    # Initialize report with float 0.0
    report_data = {date_str: 0.0 for date_str in date_range}

    # Populate report by calculating conversion rate for each day
    # This part could be optimized by fetching all scontrini and ingressi data once
    for date_str in date_range:
        report_data[date_str] = get_conversion_rate_single_date(branch_id, date_str)

    # report_data = dict(sorted(report_data.items())) # Sort if needed
    return report_data
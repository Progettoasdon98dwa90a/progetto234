# formulas/scontrini.py
"""
Functions related to calculating and reporting receipt ('Scontrini' or 'Sco.') data.
"""
from datetime import datetime, timedelta
from api.models import Employee, Import, Branch # Assuming models are accessible

# Note: Removed unused imports like json, importlib.resources, Schedule, Decimal if not used here

# get_scontrini_dipendente_single_date: Retrieves the number of receipts ('Sco.') for a specific employee on a single date.
# Output: float/int (number of receipts) or 0 if employee/import/data not found.
def get_scontrini_dipendente_single_date(employee_id, date):
    # ... (copy function code from original file) ...
    employee = None
    branch = None
    import_obj = None

    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        print(f"SCONTRINI: No employee found with ID {employee_id}")
        return 0

    if employee:
        branch = employee.branch
    else: # Should not happen if previous try/except worked
        return 0

    try:
        import_obj = Import.objects.get(import_date=date, branch=branch, import_type="sales_data")
    except Import.DoesNotExist:
        # print(f"SCONTRINI: No sales_data import found for branch {branch.id} on {date}")
        return 0 # No import data for that date/branch
    except Import.MultipleObjectsReturned:
         print(f"SCONTRINI Warning: Multiple 'sales_data' imports found for branch {branch.id} on {date}. Using first one.")
         import_obj = Import.objects.filter(import_date=date, branch=branch, import_type="sales_data").first()
         if not import_obj: return 0

    data = import_obj.data
    if not isinstance(data, list):
        print(f"SCONTRINI Warning: Import data for {date} branch {branch.id} is not a list.")
        return 0

    for employee_data in data:
        if employee_data.get('Dipendente') == employee.id: # Use .get for safety
             sco_value = employee_data.get('Sco.')
             if sco_value is not None:
                try:
                    return float(sco_value) # Convert to float
                except (ValueError, TypeError):
                    print(f"SCONTRINI Warning: Invalid 'Sco.' value '{sco_value}' for employee {employee.id} on {date}")
                    return 0 # Return 0 if conversion fails
             else:
                 # print(f"SCONTRINI Info: 'Sco.' key missing for employee {employee.id} on {date}")
                 return 0 # Return 0 if 'Sco.' key is missing
    # print(f"SCONTRINI Info: Employee {employee.id} not found in data for {date}")
    return 0 # Return 0 if employee not found in data list

# get_scontrini_dipendente_date_range: Calculates the total number of receipts ('Sco.') for a specific employee over a date range.
# Output: float (total receipts) or 0 if employee/imports/data not found.
def get_scontrini_dipendente_date_range(employee_id, start_date, end_date):
    # ... (copy function code from original file) ...
    employee = None
    branch = None
    import_objs_qs = None

    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        print(f"SCONTRINI: No employee found with ID {employee_id}")
        return 0.0

    if employee:
        branch = employee.branch
    else:
        return 0.0

    try:
        import_objs_qs = Import.objects.filter(import_date__range=(start_date, end_date), branch=branch, import_type="sales_data")
    except Exception as e: # Catch potential database errors
        print(f"SCONTRINI Error fetching imports for employee {employee_id} range {start_date}-{end_date}: {e}")
        return 0.0

    grand_total = 0.0 # Initialize as float

    if import_objs_qs.exists():
        for import_obj in import_objs_qs:
            data = import_obj.data
            if not isinstance(data, list):
                 print(f"SCONTRINI Warning: Import data for {import_obj.import_date} branch {branch.id} is not a list.")
                 continue

            for employee_data in data:
                if employee_data.get('Dipendente') == employee.id:
                    sco_value = employee_data.get('Sco.')
                    if sco_value is not None:
                        try:
                            grand_total += float(sco_value) # Add to total
                        except (ValueError, TypeError):
                             print(f"SCONTRINI Warning: Invalid 'Sco.' value '{sco_value}' skipped for employee {employee.id} on {import_obj.import_date}")
                    # If 'Sco.' key missing or value invalid, do nothing (effectively adds 0)

    return grand_total

# get_total_scontrini_single_date: Calculates the total number of receipts ('Sco.') for a specific branch on a single date.
# Output: float (total receipts) or 0 if branch/imports/data not found.
def get_total_scontrini_single_date(branch_id, date):
    # ... (copy function code from original file) ...
    branch = None
    import_obj = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print(f"SCONTRINI: No branch found with ID {branch_id}")
        return 0.0

    try:
        import_obj = Import.objects.get(import_date=date, branch=branch, import_type="sales_data")
    except Import.DoesNotExist:
        # print(f"SCONTRINI: No sales_data import found for branch {branch_id} on {date}")
        return 0.0
    except Import.MultipleObjectsReturned:
         print(f"SCONTRINI Warning: Multiple 'sales_data' imports found for branch {branch_id} on {date}. Using first one.")
         import_obj = Import.objects.filter(import_date=date, branch=branch, import_type="sales_data").first()
         if not import_obj: return 0.0

    grand_total = 0.0 # Initialize as float
    data = import_obj.data
    if not isinstance(data, list):
        print(f"SCONTRINI Warning: Import data for {date} branch {branch.id} is not a list.")
        return 0.0

    for employee_data in data:
        sco_value = employee_data.get('Sco.')
        if sco_value is not None:
            try:
                grand_total += float(sco_value)
            except (ValueError, TypeError):
                print(f"SCONTRINI Warning: Invalid 'Sco.' value '{sco_value}' skipped in total calculation for branch {branch_id} on {date}")
        # If 'Sco.' key is missing or value invalid, do nothing (effectively adds 0)

    return grand_total

# generate_branch_report_scontrini: Generates a report of total daily receipts ('Sco.') for a branch over a date range.
# Output: dict { "YYYY-MM-DD": total_receipts_float, ... } sorted by date. Returns empty dict if error or no data.
def generate_branch_report_scontrini(branch_id, start_date, end_date):
    # ... (copy function code from original file) ...
    branch = None
    import_objs_qs = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print(f"SCONTRINI: No branch found with ID {branch_id}")
        return {}

    # Validate dates and create range
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        if start_date_obj > end_date_obj:
            print("SCONTRINI Error: Start date cannot be after end date.")
            return {}
    except ValueError:
        print("SCONTRINI Error: Date format error. Please use YYYY-MM-DD.")
        return {}

    num_days = (end_date_obj - start_date_obj).days + 1
    date_range = [(start_date_obj + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)]

    # Initialize report with 0.0 for all dates in the range
    report_data = {date_str: 0.0 for date_str in date_range}

    # Fetch imports for the range (optimization: process fetched data directly)
    try:
        import_objs_qs = Import.objects.filter(
            import_date__range=(start_date, end_date),
            branch=branch,
            import_type="sales_data"
        ).order_by('import_date')
    except Exception as e:
        print(f"SCONTRINI Error fetching imports for branch {branch_id} range {start_date}-{end_date}: {e}")
        return {} # Return empty dict on error

    # Process fetched imports and update the report
    for import_obj in import_objs_qs:
        imp_date = import_obj.import_date
        if imp_date in report_data: # Check if the date is within our desired range
            daily_total = 0.0
            imp_data = import_obj.data
            if isinstance(imp_data, list):
                for employee_data in imp_data:
                    sco_value = employee_data.get('Sco.')
                    if sco_value is not None:
                        try:
                            daily_total += float(sco_value)
                        except (ValueError, TypeError):
                            print(f"SCONTRINI Warning: Invalid 'Sco.' value '{sco_value}' skipped during report generation for date {imp_date}")
                            pass
                # Update the total for the day (handles multiple imports for the same day by summing)
                report_data[imp_date] += daily_total
            else:
                print(f"SCONTRINI Warning: Import data for {imp_date} branch {branch.id} is not a list.")

    # The report_data dictionary inherently maintains insertion order in Python 3.7+
    # If compatibility with older Python is needed, uncomment the sorting line:
    # report_data = dict(sorted(report_data.items(), key=lambda item: datetime.strptime(item[0], "%Y-%m-%d")))
    return report_data


# generate_report_performance_scontrini: Generates a performance report of daily receipts ('Sco.') for each employee in a branch over a date range.
# Output: dict { "(emp_id) First Last": [daily_sco_float_for_day1, daily_sco_float_for_day2, ...], ... }. Returns empty dict if error.
def generate_report_performance_scontrini(branch_id, start_date, end_date):
    # ... (copy function code from original file) ...
    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print(f"SCONTRINI Perf: No branch found with ID {branch_id}")
        return {}

    # Validate dates first
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        if start_date_obj > end_date_obj:
             print("SCONTRINI Perf Error: Start date cannot be after end date.")
             return {}
    except ValueError:
        print("SCONTRINI Perf Error: Date format error. Please use YYYY-MM-DD.")
        return {}

    # Get import objects and employees for the branch
    try:
        # Fetch employees first to initialize the structure
        employees_objs_qs = Employee.objects.filter(branch=branch)
        if not employees_objs_qs.exists():
            print(f"SCONTRINI Perf: No employees found for branch {branch_id}")
            return {} # Return empty if no employees to report on

        import_objs_qs = Import.objects.filter(
            import_date__range=(start_date, end_date),
            branch=branch,
            import_type="sales_data"
        ).order_by('import_date')

    except Exception as e:
        print(f"SCONTRINI Perf Error fetching data for branch {branch_id}: {e}")
        return {}

    # Create a date range list
    num_days = (end_date_obj - start_date_obj).days + 1
    date_range = [(start_date_obj + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)]

    # Initialize report_data: Map employee ID to a dictionary of {date: value}
    report_data = {emp.id: {date: 0.0 for date in date_range} for emp in employees_objs_qs}

    # Create employee lookup dict for quick access
    employee_dict = {emp.id: emp for emp in employees_objs_qs}

    # Process imports
    for import_obj in import_objs_qs:
        imp_date = import_obj.import_date
        if imp_date not in date_range: # Safety check
            continue

        imp_data = import_obj.data
        if not isinstance(imp_data, list):
            print(f"SCONTRINI Perf Warning: Import data for {imp_date} branch {branch.id} is not a list.")
            continue # Skip this import

        for employee_data in imp_data:
            try:
                emp_id_str = employee_data.get('Dipendente')
                sco_str = employee_data.get('Sco.')

                if emp_id_str is None or sco_str is None:
                    continue # Skip if essential keys are missing

                emp_id = int(emp_id_str)
                value = float(sco_str)

                # Check if employee ID belongs to the branch being reported
                if emp_id in report_data:
                    # Use += to sum values if multiple entries exist for the same employee on the same day
                    report_data[emp_id][imp_date] += value
                else:
                    # Log employee from data not in the initial branch list? Optional.
                    # print(f"SCONTRINI Perf Warning: Employee ID {emp_id} from data on {imp_date} not found in branch {branch_id} employee list.")
                    pass

            except (ValueError, TypeError) as e:
                print(f"SCONTRINI Perf Warning: Skipping data entry due to error ({e}) in import {import_obj.id} for date {imp_date}: {employee_data}")
                continue # Skip malformed entries

    # Build display_data: Format for output
    display_data = {}
    for emp_id, daily_data in report_data.items():
        # We already know emp_id is in employee_dict from the initialization
        emp = employee_dict[emp_id]
        key = f"({emp.id}) {emp.first_name} {emp.last_name}"
        # Create the list of values in the correct date order
        display_data[key] = [daily_data[date] for date in date_range]

    # Sorting by employee key (name) is often desired for reports
    display_data_sorted = dict(sorted(display_data.items()))
    return display_data_sorted
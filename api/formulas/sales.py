# formulas/sales.py
"""
Functions related to calculating and reporting sales amount ('Importo')
and quantity ('Qta. Vend.') data.
"""
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from turtledemo.penrose import start

from api.models import Employee, Import, Branch # Assuming models are accessible

# generate_report_performance_sales: Generates a performance report of daily sales ('Importo') for each employee in a branch over a date range.
# Output: dict { "(emp_id) First Last": [daily_sales_float_for_day1, ...], ... } sorted by employee key. Returns empty dict if error.
def generate_report_performance_sales(branch_id, start_date, end_date):
    # ... (copy function code from original file) ...
    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print(f"SALES Perf: No branch found with ID {branch_id}")
        return {}

    # Validate dates
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        if start_date_obj > end_date_obj:
             print("SALES Perf Error: Start date cannot be after end date.")
             return {}
    except ValueError:
        print("SALES Perf Error: Date format error. Please use YYYY-MM-DD.")
        return {}

    # Get data
    try:
        employees_objs_qs = Employee.objects.filter(branch=branch)
        if not employees_objs_qs.exists():
            print(f"SALES Perf: No employees found for branch {branch_id}")
            return {}

        import_objs_qs = Import.objects.filter(
            import_date__range=(start_date, end_date),
            branch=branch,
            import_type="sales_data"
        ).order_by('import_date')

    except Exception as e:
        print(f"SALES Perf Error fetching data for branch {branch_id}: {e}")
        return {}

    # Date range
    num_days = (end_date_obj - start_date_obj).days + 1
    date_range = [(start_date_obj + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)]

    # Initialize report data structure: employee ID -> {date: value_float}
    report_data = {employee.id: {date: 0.0 for date in date_range} for employee in employees_objs_qs}
    employee_dict = {emp.id: emp for emp in employees_objs_qs}

    # Process imports
    for import_obj in import_objs_qs:
        imp_date = import_obj.import_date
        if imp_date not in date_range: continue

        imp_data = import_obj.data
        if not isinstance(imp_data, list):
            print(f"SALES Perf Warning: Import data for {imp_date} branch {branch.id} is not a list.")
            continue

        for employee_data in imp_data:
            try:
                emp_id_str = employee_data.get('Dipendente')
                importo_str = employee_data.get('Importo') # Sales amount string

                if emp_id_str is None or importo_str is None:
                    continue

                emp_id = int(emp_id_str)

                # Clean and convert sales amount string (e.g., "1.234,56" -> 1234.56)
                value_str_cleaned = str(importo_str).replace(".", "").replace(",", ".")
                value = float(value_str_cleaned) # Use float for this report as per original

                if emp_id in report_data:
                    report_data[emp_id][imp_date] += value
                else:
                    # Optional: Log employee not found in branch list
                    pass

            except (ValueError, TypeError) as e:
                print(f"SALES Perf Warning: Skipping sales data entry due to error ({e}) in import {import_obj.id} for date {imp_date}: {employee_data}")
                continue

    # Build display data
    display_data = {}
    for emp_id, daily_data in report_data.items():
         emp = employee_dict[emp_id]
         key = f"({emp.id}) {emp.first_name} {emp.last_name}"
         display_data[key] = [daily_data[date] for date in date_range]

    # Sort final output by employee key (name)
    display_data_sorted = dict(sorted(display_data.items()))

    return display_data_sorted

def get_sales_dipendente_single_date(employee_id, date):
    # ... (copy function code from original file) ...
    employee = None
    branch = None
    import_obj = None

    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        print(f"SALES: No employee found with ID {employee_id}")
        return 0

    if employee:
        branch = employee.branch
    else:
        return 0

    try:
        import_obj = Import.objects.get(import_date=date, branch=branch, import_type="sales_data")
    except Import.DoesNotExist:
        # print(f"SALES: No sales_data import found for branch {branch.id} on {date}")
        return 0
    except Import.MultipleObjectsReturned:
         print(f"SALES Warning: Multiple 'sales_data' imports found for employee {employee_id}'s branch on {date}. Using first one.")
         import_obj = Import.objects.filter(import_date=date, branch=branch, import_type="sales_data").first()
         if not import_obj: return 0

    data = import_obj.data
    if not isinstance(data, list):
         print(f"SALES Warning: Import data for {date} branch {branch.id} is not a list.")
         return 0

    for employee_data in data:
        emp_id_str = employee_data.get('Dipendente')
        if emp_id_str is not None and int(emp_id_str) == employee_id:
            importo_str = employee_data.get('Importo') # Sales amount string
            if importo_str is not None:
                # Clean and convert sales amount string (e.g., "1.234,56" -> 1234.56)
                value_str_cleaned = str(importo_str).replace(".", "").replace(",", ".")
                value = float(value_str_cleaned) # Use float for this report as per original
                return value

    return 0

def get_total_sales_dipendente(employee_id):
    # ... (copy function code from original file) ...
    employee = None
    branch = None
    import_obj = None

    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        print(f"SALES: No employee found with ID {employee_id}")
        return 0

    if employee:
        branch = employee.branch
    else:
        return 0

    import_objs_qs = Import.objects.filter(branch=branch, import_type="sales_data")
    if not import_objs_qs.exists():
        print(f"SALES: No sales_data imports found for employee {employee_id}'s branch between {start_date} and {end_date}")
        return 0

    grand_total = 0 # Initialize as integer

    for import_obj in import_objs_qs:
        data = import_obj.data
        if not isinstance(data, list):
             print(f"SALES Warning: Import data for {import_obj.import_date} branch {branch.id} is not a list.")
             continue

        for employee_data in data:
            emp_id_str = employee_data.get('Dipendente')
            if emp_id_str is not None and int(emp_id_str) == employee_id:
                importo_str = employee_data.get('Importo') # Sales amount string
                if importo_str is not None:
                    # Clean and convert sales amount string (e.g., "1.234,56" -> 1234.56)
                    value_str_cleaned = str(importo_str).replace(".", "").replace(",", ".")
                    value = float(value_str_cleaned) # Use float for this report as per original
                    grand_total += value

    return grand_total


# get_branch_single_day_sales: Calculates the total sales for a specific branch on a single date, handling brand-specific logic.
# Output: Decimal (total sales) or Decimal("0.00") if branch/import/data not found or processing fails.
def get_branch_single_day_sales(branch_id, date):
    # ... (copy function code from original file) ...
    branch = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print(f"SALES: No branch found with ID {branch_id}")
        return Decimal("0.00")

    try:
        import_obj = Import.objects.get(import_date=date, branch=branch, import_type="sales_data")
    except Import.DoesNotExist:
        # print(f"SALES: No sales_data import found for branch {branch_id} on {date}")
        return Decimal("0.00")
    except Import.MultipleObjectsReturned:
         print(f"SALES Warning: Multiple 'sales_data' imports found for branch {branch_id} on {date}. Using first one.")
         import_obj = Import.objects.filter(import_date=date, branch=branch, import_type="sales_data").first()
         if not import_obj: return Decimal("0.00")

    sales = Decimal("0.00") # Use Decimal for financial calculations
    data = import_obj.data
    brand = branch.get_brand() # Assuming get_brand() method exists on Branch model

    if brand == "equivalenza":
        if not isinstance(data, list):
             print(f"SALES Warning: Equivalenza import data for {date} branch {branch.id} is not a list.")
             return Decimal("0.00")
        for employee_data in data:
             importo_value = employee_data.get('Importo')
             if importo_value is not None:
                try:
                    # Clean string and convert to Decimal
                    value_str = str(importo_value).replace(".", "").replace(",", ".")
                    value = Decimal(value_str)
                    sales += value
                except (InvalidOperation, TypeError) as e:
                    print(f"SALES Warning: Invalid 'Importo' value '{importo_value}' skipped for equivalenza branch {branch_id} on {date}: {e}")

    elif brand == "original":
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            importo_value = data[0].get('Importo')
            if importo_value is not None:
                 try:
                     # Assuming 'Importo' might be number or string representation
                     sales += Decimal(str(importo_value)) # Convert to Decimal safely
                 except (InvalidOperation, TypeError) as e:
                     print(f"SALES Warning: Invalid 'Importo' value '{importo_value}' skipped for original branch {branch_id} on {date}: {e}")
            else:
                 print(f"SALES Warning: 'Importo' key missing in original branch data for {date} branch {branch_id}")
        else:
             print(f"SALES Warning: Unexpected data structure for original branch {branch_id} on {date}")

    else: # Handle other potential brands or default case
        print(f"SALES Warning: Unknown or unhandled brand '{brand}' for branch {branch_id}. Cannot calculate sales.")
        return Decimal("0.00")

    return sales.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) # Return rounded Decimal


# generate_branch_report_sales: Generates a report of total daily sales for a branch over a date range.
# Output: dict { "YYYY-MM-DD": total_sales_Decimal, ... }. Returns empty dict if error or no data.
def generate_branch_report_sales(branch_id, start_date, end_date):
    # ... (copy function code from original file) ...
    branch = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print(f"SALES Report: No branch found with ID {branch_id}")
        return {}

    # Validate dates and create range
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        if start_date_obj > end_date_obj:
            print("SALES Report Error: Start date cannot be after end date.")
            return {}
    except ValueError:
        print("SALES Report Error: Date format error. Please use YYYY-MM-DD.")
        return {}

    num_days = (end_date_obj - start_date_obj).days + 1
    date_range = [(start_date_obj + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)]

    # Initialize report with Decimal 0 for all dates
    report_data = {date_str: Decimal("0.00") for date_str in date_range}

    # OPTION 1: Call single day function (simpler, potentially less efficient)
    # for date_str in date_range:
    #     daily_sales = get_branch_single_day_sales(branch_id, date_str)
    #     report_data[date_str] = daily_sales

    # OPTION 2: Fetch all imports once and process (more efficient)
    try:
        import_objs_qs = Import.objects.filter(
            import_date__range=(start_date, end_date),
            branch=branch,
            import_type="sales_data"
        )
    except Exception as e:
        print(f"SALES Report Error fetching sales imports for branch {branch_id}: {e}")
        return {}

    brand = branch.get_brand() # Get brand once

    for import_obj in import_objs_qs:
        imp_date = import_obj.import_date
        if imp_date in report_data: # Check if the date is within our desired range
            data = import_obj.data
            daily_sales_increase = Decimal("0.00")

            if brand == "equivalenza":
                if isinstance(data, list):
                    for employee_data in data:
                         importo_value = employee_data.get('Importo')
                         if importo_value is not None:
                            try:
                                value_str = str(importo_value).replace(".", "").replace(",", ".")
                                daily_sales_increase += Decimal(value_str)
                            except (InvalidOperation, TypeError): pass # Ignore bad data point
                else:
                    print(f"SALES Report Warning: Equivalenza import data for {imp_date} branch {branch.id} is not a list.")

            elif brand == "original":
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                    importo_value = data[0].get('Importo')
                    if importo_value is not None:
                         try:
                             daily_sales_increase += Decimal(str(importo_value))
                         except (InvalidOperation, TypeError): pass # Ignore bad data point
                    # else: Missing key ignored
                else:
                    print(f"SALES Report Warning: Unexpected data structure for original branch {branch.id} on {imp_date}")
            else:
                 # Unknown brand already handled in get_branch_single_day_sales if used
                 # If processing directly, might need handling here too
                 pass

            report_data[imp_date] += daily_sales_increase # Add calculated sales for the day

    # Quantize final results
    for date_key in report_data:
        report_data[date_key] = report_data[date_key].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # report_data = dict(sorted(report_data.items())) # Sort if needed
    return report_data


# get_number_sales_performance_single_date: Retrieves the quantity of items sold ('Qta. Vend.') by a specific employee on a single date.
# Output: int (quantity sold) or 0 if employee/import/data not found or invalid.
def get_number_sales_performance_single_date(employee_id, date):
    # ... (copy function code from original file) ...
    employee = None
    branch = None
    import_obj = None

    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        print(f"SALES Qty: No employee found with ID {employee_id}")
        return 0

    if employee:
        branch = employee.branch
    else:
        return 0

    try:
        import_obj = Import.objects.get(import_date=date, branch=branch, import_type="sales_data")
    except Import.DoesNotExist:
        # print(f"SALES Qty: No sales_data import found for branch {branch.id} on {date}")
        return 0
    except Import.MultipleObjectsReturned:
         print(f"SALES Qty Warning: Multiple 'sales_data' imports found for employee {employee_id}'s branch on {date}. Using first one.")
         import_obj = Import.objects.filter(import_date=date, branch=branch, import_type="sales_data").first()
         if not import_obj: return 0

    data = import_obj.data
    if not isinstance(data, list):
         print(f"SALES Qty Warning: Import data for {date} branch {branch.id} is not a list.")
         return 0

    for employee_data in data:
        if employee_data.get('Dipendente') == employee.id:
             qty_str = employee_data.get('Qta. Vend.')
             if qty_str is not None:
                 try:
                     # Remove potential thousand separators (like '.') before converting
                     qty_cleaned = str(qty_str).replace('.', '')
                     return int(qty_cleaned)
                 except (ValueError, TypeError):
                     print(f"SALES Qty Warning: Invalid 'Qta. Vend.' value '{qty_str}' for employee {employee.id} on {date}")
                     return 0 # Return 0 if conversion fails
             else:
                 # print(f"SALES Qty Info: Key 'Qta. Vend.' missing for employee {employee.id} on {date}")
                 return 0 # Return 0 if key 'Qta. Vend.' is missing
    # print(f"SALES Qty Info: Employee {employee.id} not found in data for {date}")
    return 0 # Return 0 if employee not found in data

# get_number_sales_performance_employee_date_range: Calculates the total quantity of items sold ('Qta. Vend.') by a specific employee over a date range.
# Output: int (total quantity sold) or 0 if employee/imports/data not found.
def get_number_sales_performance_employee_date_range(employee_id, start_date, end_date):
    # ... (copy function code from original file) ...
    employee = None
    branch = None
    import_objs_qs = None

    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        print(f"SALES Qty Range: No employee found with ID {employee_id}")
        return 0

    if employee:
        branch = employee.branch
    else:
        return 0

    try:
        import_objs_qs = Import.objects.filter(import_date__range=(start_date, end_date), branch=branch, import_type="sales_data")
    except Exception as e:
        print(f"SALES Qty Range Error fetching imports for employee {employee_id}: {e}")
        return 0

    grand_total = 0 # Initialize as integer

    if import_objs_qs.exists():
        for import_obj in import_objs_qs:
            data = import_obj.data
            if not isinstance(data, list):
                 print(f"SALES Qty Range Warning: Import data for {import_obj.import_date} branch {branch.id} is not a list.")
                 continue

            for employee_data in data:
                if employee_data.get('Dipendente') == employee.id:
                    qty_str = employee_data.get('Qta. Vend.')
                    if qty_str is not None:
                        try:
                            qty_cleaned = str(qty_str).replace('.', '')
                            grand_total += int(qty_cleaned)
                        except (ValueError, TypeError):
                             print(f"SALES Qty Range Warning: Invalid 'Qta. Vend.' value '{qty_str}' skipped for employee {employee.id} on {import_obj.import_date}")
                    # If key missing or value invalid, effectively adds 0

    return grand_total


# generate_number_sales_performance: Generates a report of daily quantity sold ('Qta. Vend.') performance for each employee over a date range.
# Output: dict { "(emp_id) First Last": [daily_qty_int_for_day1, ...], ... }. Returns empty dict if error.
def generate_number_sales_performance(branch_id, start_date, end_date):
    # ... (copy function code from original file, correcting the logic) ...
    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print(f"SALES Qty Perf: No branch found with ID {branch_id}")
        return {}

    # Validate dates
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        if start_date_obj > end_date_obj:
            print("SALES Qty Perf Error: Start date cannot be after end date.")
            return {}
    except ValueError:
        print("SALES Qty Perf Error: Date format error. Please use YYYY-MM-DD.")
        return {}

    # Get data
    try:
        employees_objs_qs = Employee.objects.filter(branch=branch)
        if not employees_objs_qs.exists():
            print(f"SALES Qty Perf: No employees found for branch {branch_id}")
            return {}

        import_objs_qs = Import.objects.filter(
            import_date__range=(start_date, end_date),
            branch=branch,
            import_type="sales_data"
        ).order_by('import_date')
    except Exception as e:
        print(f"SALES Qty Perf Error fetching data for branch {branch_id}: {e}")
        return {}

    # Date range
    num_days = (end_date_obj - start_date_obj).days + 1
    date_range = [(start_date_obj + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)]

    # Initialize report data structure: employee ID -> {date: quantity_int}
    report_data = {employee.id: {date: 0 for date in date_range} for employee in employees_objs_qs}
    employee_dict = {emp.id: emp for emp in employees_objs_qs}

    # Process imports
    for import_obj in import_objs_qs:
        imp_date = import_obj.import_date
        if imp_date not in date_range: continue

        imp_data = import_obj.data
        if not isinstance(imp_data, list):
            print(f"SALES Qty Perf Warning: Import data for {imp_date} branch {branch.id} is not a list.")
            continue

        for employee_data in imp_data:
            try:
                emp_id_str = employee_data.get('Dipendente')
                qty_str = employee_data.get('Qta. Vend.')

                if emp_id_str is None or qty_str is None:
                    continue

                emp_id = int(emp_id_str)

                if emp_id in report_data:
                    try:
                        qty_cleaned = str(qty_str).replace('.', '')
                        value = int(qty_cleaned) # Convert quantity to int
                        report_data[emp_id][imp_date] += value # Sum quantities if multiple entries exist
                    except (ValueError, TypeError):
                         print(f"SALES Qty Perf Warning: Skipping quantity data entry due to invalid value '{qty_str}' in import {import_obj.id} for date {imp_date}")
                # else: Employee not in branch list, ignore.

            except (ValueError, TypeError) as e: # Catch error during emp_id conversion
                print(f"SALES Qty Perf Warning: Skipping quantity data entry due to error ({e}) processing employee ID in import {import_obj.id} for date {imp_date}: {employee_data}")
                continue

    # Build display data: employee key -> list of daily quantities
    display_data = {}
    for emp_id, daily_data in report_data.items():
         emp = employee_dict[emp_id]
         key = f"({emp.id}) {emp.first_name} {emp.last_name}"
         display_data[key] = [daily_data[date] for date in date_range]

    # Sort final output by employee key (name)
    display_data_sorted = dict(sorted(display_data.items()))

    return display_data_sorted
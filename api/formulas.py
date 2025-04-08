import importlib.resources
import json
from datetime import datetime, timedelta
from pprint import pprint

from api.models import Employee, Schedule, Import, Branch


def orario_exists(start_date, end_date):
    return Schedule.objects.filter(start_date=start_date, end_date=end_date).exists()

### SCONTRINI

def get_scontrini_dipendente_single_date(employee_id, date):

    employee = None
    branch = None
    import_obj = None

    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        print("no emp")

    if employee:
        branch = employee.branch

    try:
        import_obj = Import.objects.get(import_date=date, branch=branch, import_type="sales_data")
    except Import.DoesNotExist:
        return 0

    data = import_obj.data
    for employee_data in data:
        if employee_data['Dipendente'] == employee.id:
            return employee_data['Sco.']


def get_scontrini_dipendente_date_range(employee_id, start_date, end_date):

    employee = None
    branch = None
    import_objs_qs = None


    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        print("no emp")

    if employee:
        branch = employee.branch

    try:
        import_objs_qs = Import.objects.filter(import_date__range=(start_date, end_date), branch=branch, import_type="sales_data")
    except Import.DoesNotExist:
        return 0

    grand_total = 0

    if import_objs_qs.count() > 0:
        for import_obj in import_objs_qs:
            data = import_obj.data
            for employee_data in data:
                if employee_data['Dipendente'] == employee.id:
                    grand_total += float(employee_data['Sco.'])

        return grand_total


def get_total_scontrini_single_date(branch_id, date):

    branch = None
    import_objs_qs = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print("no branch")

    try:
        import_objs_qs = Import.objects.filter(import_date=date, branch=branch, import_type="sales_data")
    except Import.DoesNotExist:
        return 0

    grand_total = 0
    if import_objs_qs.count() > 0:
        for import_obj in import_objs_qs:
            data = import_obj.data
            for employee_data in data:
                grand_total += float(employee_data['Sco.'])

        return grand_total
    return 0


def generate_branch_report_scontrini(branch_id, start_date, end_date):

    branch = None
    import_objs_qs = None
    employees_objs_qs = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print("no branch")

    try:
        import_objs_qs = Import.objects.filter(import_date__range=(start_date, end_date), branch=branch, import_type="sales_data")
    except Import.DoesNotExist:
        return 0

    try:
        employees_objs_qs = Employee.objects.filter(branch=branch)
    except Employee.DoesNotExist:
        print("no employees")

    # data = {"YYYY/MM/DD": 203, "YYYY/MM/DD": 101}

    data = {}

    for import_obj in import_objs_qs:
        data[import_obj.import_date] = get_total_scontrini_single_date(branch_id, import_obj.import_date)

    data = dict(sorted(data.items(), key=lambda x: x[0]))

    return data


def generate_report_performance_scontrini(branch_id, start_date, end_date):
    # Get the branch object
    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print("No branch found")
        return {}, []

    # Get import objects and employees for the branch
    import_objs_qs = Import.objects.filter(import_date__range=(start_date, end_date), branch=branch, import_type="sales_data")
    employees_objs_qs = Employee.objects.filter(branch=branch)

    # Create a date range list from start_date to end_date (inclusive)
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        print("Date format error. Please use YYYY-MM-DD.")
        return {}, []

    num_days = (end_date_obj - start_date_obj).days + 1
    date_range = [(start_date_obj + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)]

    # Initialize report_data: each employee gets a dictionary with every date set to 0
    report_data = {}
    for employee in employees_objs_qs:
        report_data[employee.id] = {date: 0 for date in date_range}

    # Loop through each import and add the performance values for the appropriate date & employee.
    for import_obj in import_objs_qs:
        # Assumption: import_obj.import_date is a string in "YYYY-MM-DD" format.
        imp_date = import_obj.import_date
        if imp_date not in date_range:
            continue  # skip if date not in range

        # import_obj.data is assumed to be a list of dictionaries, one per employee
        for employee_data in import_obj.data:
            try:
                emp_id = int(employee_data['Dipendente'])
            except (KeyError, ValueError):
                continue  # skip if employee id is missing or invalid

            if emp_id in report_data:
                try:
                    # Convert the performance value to float.
                    # (Adjust this conversion if you prefer Decimal arithmetic.)
                    value = float(employee_data['Sco.'])
                except (KeyError, ValueError):
                    value = 0
                # Sum the value if there are multiple entries for the same day.
                report_data[emp_id][imp_date] += value

    # Build display_data: convert each employee's dictionary into a list in the same date order.
    display_data = {}
    for emp_id, daily_data in report_data.items():
        try:
            emp = employees_objs_qs.get(id=emp_id)
        except Employee.DoesNotExist:
            continue  # just in case
        key = f"({emp.id}) {emp.first_name} {emp.last_name}"
        # Create a list of values corresponding to each day in date_range.
        display_data[key] = [daily_data[date] for date in date_range]

    return display_data


def generate_report_performance_sales(branch_id, start_date, end_date):
    # Get the branch object
    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print("No branch found")
        return {}, []

    # Get import objects and employees for the branch
    import_objs_qs = Import.objects.filter(import_date__range=(start_date, end_date), branch=branch, import_type="sales_data")
    employees_objs_qs = Employee.objects.filter(branch=branch)

    # Create a date range list from start_date to end_date (inclusive)
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        print("Date format error. Please use YYYY-MM-DD.")
        return {}, []

    num_days = (end_date_obj - start_date_obj).days + 1
    date_range = [(start_date_obj + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)]

    # Initialize report_data: each employee gets a dictionary with every date set to 0
    report_data = {}
    for employee in employees_objs_qs:
        report_data[employee.id] = {date: 0 for date in date_range}

    # Loop through each import and add the performance values for the appropriate date & employee.
    for import_obj in import_objs_qs:
        # Assumption: import_obj.import_date is a string in "YYYY-MM-DD" format.
        imp_date = import_obj.import_date
        if imp_date not in date_range:
            continue  # skip if date not in range

        # import_obj.data is assumed to be a list of dictionaries, one per employee
        for employee_data in import_obj.data:
            try:
                emp_id = int(employee_data['Dipendente'])
            except (KeyError, ValueError):
                continue  # skip if employee id is missing or invalid

            if emp_id in report_data:
                try:
                    # Convert the performance value to float.
                    # (Adjust this conversion if you prefer Decimal arithmetic.)
                    value = float(employee_data['Importo'].replace(".", "").replace(",", "."))

                except (KeyError, ValueError):
                    value = 0
                # Sum the value if there are multiple entries for the same day.
                report_data[emp_id][imp_date] += value

    # Build display_data: convert each employee's dictionary into a list in the same date order.
    display_data = {}
    for emp_id, daily_data in report_data.items():
        try:
            emp = employees_objs_qs.get(id=emp_id)
        except Employee.DoesNotExist:
            continue  # just in case
        key = f"({emp.id}) {emp.first_name} {emp.last_name}"
        # Create a list of values corresponding to each day in date_range.
        display_data[key] = [daily_data[date] for date in date_range]

    display_data_sorted = dict(sorted(display_data.items(), key=lambda x: x[0]))

    return display_data_sorted


### VENDITE

def get_branch_single_day_sales(branch_id, date):

    branch = None
    import_objs_qs = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print("no branch")

    try:
        import_objs_qs = Import.objects.filter(import_date=date, branch=branch, import_type="sales_data")
    except Import.DoesNotExist:
        return 0

    from decimal import Decimal, ROUND_HALF_UP

    sales = 0
    if import_objs_qs.count() > 0:
        for import_obj in import_objs_qs:
            data = import_obj.data

            if branch.get_brand() == "equivalenza":
                for employee_data in data:
                    value = Decimal(employee_data['Importo'].replace(".", "").replace(",", "."))
                    rounded_value = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    sales += rounded_value
            elif branch.get_brand() == "original":
                data = data[0]
                sales += data["Importo"]



    return sales

def generate_branch_report_sales(branch_id, start_date, end_date):

    branch = None
    import_objs_qs = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print("no branch")

    try:
        import_objs_qs = Import.objects.filter(import_date__range=(start_date, end_date), branch=branch, import_type="sales_data")
    except Import.DoesNotExist:
        return 0

    # data = {"YYYY/MM/DD": 203, "YYYY/MM/DD": 101}

    data = {}

    for import_obj in import_objs_qs:
        data[import_obj.import_date] = get_branch_single_day_sales(branch_id, import_obj.import_date)

    return data

def get_number_sales_performance_single_date(employee_id, date):

    employee = None
    branch = None
    import_obj = None

    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        print("no emp")

    if employee:
        branch = employee.branch

    try:
        import_obj = Import.objects.get(import_date=date, branch=branch, import_type="sales_data")
    except Import.DoesNotExist:
        return 0

    data = import_obj.data
    for employee_data in data:
        if employee_data['Dipendente'] == employee.id:
            return employee_data['Qta. Vend.']

    return 0

def get_number_sales_performance_employee_date_range(employee_id, start_date, end_date):

    employee = None
    branch = None
    import_objs_qs = None


    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        print("no emp")

    if employee:
        branch = employee.branch

    try:
        import_objs_qs = Import.objects.filter(import_date__range=(start_date, end_date), branch=branch, import_type="sales_data")
    except Import.DoesNotExist:
        return 0

    grand_total = 0

    if import_objs_qs.count() > 0:
        for import_obj in import_objs_qs:
            data = import_obj.data
            for employee_data in data:
                if employee_data['Dipendente'] == employee.id:
                    grand_total += int(employee_data['Qta. Vend.'])

    return grand_total


def generate_number_sales_performance(branch_id, start_date, end_date):

    branch = None
    import_objs_qs = None
    employees_objs_qs = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print("no branch")

    try:
        import_objs_qs = Import.objects.filter(import_date__range=(start_date, end_date), branch=branch, import_type="sales_data")
    except Import.DoesNotExist:
        return 0

    try:
        employees_objs_qs = Employee.objects.filter(branch=branch)
    except Employee.DoesNotExist:
        print("no employees")

    # data = {"YYYY/MM/DD": 203, "YYYY/MM/DD": 101}

    data = {}

    for import_obj in import_objs_qs:
        data[import_obj.import_date] = get_number_sales_performance_single_date(branch_id, import_obj.import_date)

    return data

def generate_medium_sales(sales_performance):

    medium_sales_performance_data = {}

    for key, value in sales_performance.items():
        medium_sales_performance_data[key] = round(sum(value)/len(value), 2)

    return medium_sales_performance_data


def generate_medium_sc_sales(sc_performance):

    medium_sc_performance_data = {}

    for key, value in sc_performance.items():
        medium_sc_performance_data[key] = round(sum(value)/len(value), 2)

    return medium_sc_performance_data




def generate_medium_sales_performance(sales_performance):

    medium_sales_performance_data = {}

    for key, value in sales_performance.items():
        medium_sales_performance_data[key] = round(sum(value)/len(value), 2)

    return medium_sales_performance_data


#### COUNTER


def get_number_ingressi_single_date(branch_id, date):

    branch = None
    import_obj = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print("no branch")

    try:
        import_obj = Import.objects.get(import_date=date, branch=branch, import_type="counter_data")
    except Import.DoesNotExist:
        return 0

    data = import_obj.data
    for counter_data in data:
        return counter_data['(Ing) Ingressi']

    return 0

def get_traffico_esterno_single_date(branch_id, date):

    branch = None
    import_obj = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print("no branch")

    try:
        import_obj = Import.objects.get(import_date=date, branch=branch, import_type="counter_data")
    except Import.DoesNotExist:
        return 0

    data = import_obj.data
    for counter_data in data:
        return counter_data['(Est) Traffico Esterno']

    return 0

def get_tasso_attrazione_single_date(branch_id, date):

    branch = None
    import_obj = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print("no branch")

    try:
        import_obj = Import.objects.get(import_date=date, branch=branch, import_type="counter_data")
    except Import.DoesNotExist:
        return 0

    data = import_obj.data
    for counter_data in data:
        return counter_data['(TA) Tasso di Attrazione']

    return 0


def get_number_ingressi_date_range(branch_id, start_date, end_date):

    branch = None
    import_objs_qs = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print("no branch")

    try:
        import_objs_qs = Import.objects.filter(import_date__range=(start_date, end_date), branch=branch, import_type="counter_data")
    except Import.DoesNotExist:
        return 0

    grand_total = 0

    if import_objs_qs.count() > 0:
        for import_obj in import_objs_qs:
            data = import_obj.data
            for counter_data in data:
                grand_total += int(counter_data['(Ing) Ingressi'])

    return grand_total


def get_traffico_esterno_date_range(branch_id, start_date, end_date):

    branch = None
    import_objs_qs = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print("no branch")

    try:
        import_objs_qs = Import.objects.filter(import_date__range=(start_date, end_date), branch=branch, import_type="counter_data")
    except Import.DoesNotExist:
        return 0

    grand_total = 0

    if import_objs_qs.count() > 0:
        for import_obj in import_objs_qs:
            data = import_obj.data
            for counter_data in data:
                grand_total += int(counter_data['(Est) Traffico Esterno'])

    return grand_total


def get_tasso_attrazione_date_range(branch_id, start_date, end_date):

    branch = None
    import_objs_qs = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print("no branch")

    try:
        import_objs_qs = Import.objects.filter(import_date__range=(start_date, end_date), branch=branch, import_type="counter_data")
    except Import.DoesNotExist:
        return 0

    grand_total = 0

    if import_objs_qs.count() > 0:
        for import_obj in import_objs_qs:
            data = import_obj.data
            for counter_data in data:
                grand_total += int(counter_data['(TA) Tasso di Attrazione'])

    return grand_total



def generate_ingressi_branch_report(branch_id, start_date, end_date):

    branch = None
    import_objs_qs = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print("no branch")

    try:
        import_objs_qs = Import.objects.filter(import_date__range=(start_date, end_date), branch=branch, import_type="counter_data")
    except Import.DoesNotExist:
        return 0

    print(import_objs_qs.count())

    # data = {"YYYY/MM/DD": 203, "YYYY/MM/DD": 101}

    data = {}

    for import_obj in import_objs_qs:
        data[import_obj.import_date] = get_number_ingressi_single_date(branch_id, import_obj.import_date)

    return data


def generate_branch_traffico_esterno_report(branch_id, start_date, end_date):

    branch = None
    import_objs_qs = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print("no branch")

    try:
        import_objs_qs = Import.objects.filter(import_date__range=(start_date, end_date), branch=branch, import_type="counter_data")
    except Import.DoesNotExist:
        return 0

    # data = {"YYYY/MM/DD": 203, "YYYY/MM/DD": 101}

    data = {}

    for import_obj in import_objs_qs:
        data[import_obj.import_date] = get_traffico_esterno_single_date(branch_id, import_obj.import_date)

    return data

def generate_branch_tasso_attrazione_report(branch_id, start_date, end_date):

    branch = None
    import_objs_qs = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print("no branch")

    try:
        import_objs_qs = Import.objects.filter(import_date__range=(start_date, end_date), branch=branch, import_type="counter_data")
    except Import.DoesNotExist:
        return 0

    # data = {"YYYY/MM/DD": 203, "YYYY/MM/DD": 101}

    data = {}

    for import_obj in import_objs_qs:
        data[import_obj.import_date] = get_tasso_attrazione_single_date(branch_id, import_obj.import_date)

    return data


def get_employee_worked_hours_single_day(employee_id, date):
    """
    Calculate the total hours an employee worked on a specific day.

    Assumes schedule_data is structured as:
      {
         "2025-02-01": {
             "540": ["2", "3"],
             "570": ["2", "3"],
             "600": ["2", "3", "4"],
             ...
         },
         ...
      }
    where each time key represents a 30-minute block.
    """

    employee = None


    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        print("Employee does not exist.")
        return 0  # or choose an error code / exception

    branch = employee.branch

    try:
        schedule_obj = Schedule.objects.get(start_date__lte=date, end_date__gte=date, branch=branch)
    except Schedule.DoesNotExist:
        # No schedule for that day
        return -1

    # Parse schedule_data if it is a JSON string
    schedule_data = schedule_obj.schedule_data
    if isinstance(schedule_data, str):
        schedule_data = json.loads(schedule_data)

    # Get the schedule for the provided date
    day_schedule = schedule_data.get(date)
    if not day_schedule:
        print("No")
        return 0

    worked_slots = 0
    # Loop over each time block in the day's schedule
    for time_key, employee_list in day_schedule.items():
        # Make sure to compare as strings, since the stored IDs might be strings
        if str(employee_id) in [str(emp) for emp in employee_list]:
            worked_slots += 1

    # Each slot is 30 minutes (0.5 hours)
    worked_hours = worked_slots * 0.5
    return worked_hours


def get_conversion_rate_single_date(branch_id, date):

    ingressi_daily = get_number_ingressi_single_date(branch_id, date)
    scontrini_daily = get_total_scontrini_single_date(branch_id, date)

    print(type(scontrini_daily))

    if scontrini_daily > 0 and ingressi_daily > 0:
        conversion_rate_percentual = (scontrini_daily / ingressi_daily) * 100
        conversion_rate = conversion_rate_percentual if conversion_rate_percentual > 0 else 0
    else:
        conversion_rate = 0
    return conversion_rate


def generate_branch_report_conversion_rate(branch_id, start_date_str, end_date_str):

    branch = None
    import_objs_qs = None

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        print("no branch")

    # Create a date range list from start_date to end_date (inclusive)
    try:
        start_date_obj = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        print("Date format error. Please use YYYY-MM-DD.")
        return {}, []

    num_days = (end_date_obj - start_date_obj).days + 1
    date_range = [(start_date_obj + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_days)]

    data = {}

    for date in date_range:
        data[date] = get_conversion_rate_single_date(branch_id, date)

    return data


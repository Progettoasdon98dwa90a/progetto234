from asyncio import current_task
from datetime import timedelta, datetime

from django.http import JsonResponse

from api.management.commands.seed import current_directory
from api.models import Employee, Target
from api.formulas.receipts import get_total_scontrini_date_range
from api.formulas.sales import get_total_sales_date_range
from api.formulas.counter import get_number_ingressi_date_range


def get_last_7_days_start_date():
    today = datetime.now()
    last_7_days_start_date = today - timedelta(days=7)
    return last_7_days_start_date.strftime('%Y-%m-%d')

def dashboard_data(request, branch_id):
    if request.method == 'GET':
        last_7_days_start_date = get_last_7_days_start_date()
        total_receipts = get_total_scontrini_date_range(branch_id,
                                                        last_7_days_start_date,
                                                        datetime.now().date().strftime('%Y-%m-%d'))
        last_month_start_date = (datetime.now().replace(day=1)).strftime('%Y-%m-%d')
        current_date = datetime.now().date().strftime('%Y-%m-%d')

        total_sales = get_total_sales_date_range(branch_id, last_month_start_date, current_date)

        people_count = get_number_ingressi_date_range(branch_id, last_month_start_date, current_date)
        current_target = Target.objects.filter(branch_id=branch_id, start_date=last_month_start_date).first()
        reached_income_percentage = 0

        # Calculate the percentage, ensuring the monthly budget is not zero to prevent division error
        if current_target.sales_target is not None and current_target.sales_target > 0:
            # Perform the division and multiply by 100
            reached_income_percentage = (total_sales / current_target) * 100
            # Optional: Round the percentage to a reasonable number of decimal places
            reached_income_percentage = round(reached_income_percentage, 2)  # Round to 2 decimal places
            # Note: This will correctly show percentages > 100 if actual_income exceeds the target
        data = {
            'metrics' :{},
            'topEmployees': [],
            'pendingShifts': {},
        }

        metrics_data = {
            'totalReceipts' : total_receipts, # Last 7 Days
            'incomes' : total_sales, # Current Month
            'peopleCount' : people_count, # Current Month
            'monthlyTarget' : {
                'monthlyBudget' : current_target.sales_target, # Current Month
                'actualIncome' : total_sales,
                'reachedIncomePercentage' : reached_income_percentage,
                'variation_percentage' : 0,

            }
        }

        data['metrics'] = metrics_data

        top_employees_data = []

        employee_object = {
            'name' : '',
            'averageSoldPieces' : 0,
            'mediumReceipts' : 0, # value
            'averageReceipts' : 0,
        }

        employees = Employee.objects.filter(branch_id=branch_id)

        for employee in employees:
            employee_object = {}
            employee_object['name'] = employee.first_name + ' ' + employee.last_name
            employee_object['averageSoldPieces'] = 0
            employee_object['mediumReceipts'] = 0
            employee_object['averageReceipts'] = 0

            top_employees_data.append(employee_object)

        data['topEmployees'] = top_employees_data

        pending_shifts_data = []

        return JsonResponse(data)
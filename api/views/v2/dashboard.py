from datetime import timedelta, datetime

from django.http import JsonResponse

from api.models import Employee
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
                'monthlyBudget' : 0,
                'actualIncome' : 0,
                'reachedIncomePercentage' : 0,
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
from django.http import JsonResponse

from api.models import Employee


def dashboard_data(request, branch_id):
    if request.method == 'GET':

        data = {
            'metrics' :{},
            'topEmployees': [],
            'pendingShifts': {},
        }

        metrics_data = {
            'totalReceipts' : 0, # Last 7 Days
            'incomes' : 0, # Current Month
            'peopleCount' : 0, # Current Month
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
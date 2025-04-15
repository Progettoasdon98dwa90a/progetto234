import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.models import Employee, Role, Branch


def get_all_employees(request):

    if request.method == 'GET':
        employees = Employee.objects.all()

        data = {"data" : []}

        for employee in employees:
            data['data'].append({
                'id': employee.id,
                'first_name': employee.first_name,
                'last_name': employee.last_name,
                'role': employee.role.name,
                'gender': employee.gender,
                'branch': employee.branch.name,
                "actions": [
                    {"label": "Gestisci", "url": f"/manage_employee/{employee.id}"},
                ]
            })

        return JsonResponse(data)


def get_employee_data(request, employee_id):
    if request.method == 'GET':
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Employee not found'})

        data = {"data": []}

        employee_data = {
            'id': employee.id,
            'first_name': employee.first_name,
            'last_name': employee.last_name,
            'branch': employee.branch.id,
            'role': employee.role.id,
        }

        data['data'].append(employee_data)
        return JsonResponse(data)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
def manage_employee(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        employee_id = data.get('employee_id')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        branch = data.get('branch')
        role = data.get('role')

        try:
            employee = Employee.objects.get(id=employee_id)
            updated = False

            if first_name and employee.first_name != first_name:
                employee.first_name = first_name
                updated = True

            if last_name and employee.last_name != last_name:
                employee.last_name = last_name
                updated = True

            if branch and employee.branch.id != branch:
                employee.branch = Branch.objects.get(id=branch)
                updated = True

            if role and employee.role.id != role:
                employee.role = Role.objects.get(id=role)
                updated = True

            if updated:
                employee.save()
                return JsonResponse({'status': 'success'}, status=200)
            else:
                return JsonResponse({'status': 'no change'}, status=203)

        except Employee.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Employee not found'})


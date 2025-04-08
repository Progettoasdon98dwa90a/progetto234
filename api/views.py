from datetime import datetime
import json

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from api.models import Employee, Branch, Role
from django.views.decorators.csrf import csrf_exempt

from api.models import Schedule

from api.formulas import orario_exists


# Create your views here.

# BRANCHES

def get_all_branches(request):

    if request.method == 'GET':
        branches = Branch.objects.all()

        data = {"data" : []}

        for branch in branches:
            data['data'].append({
                'id': branch.id,
                'name': branch.name,
            })

        return JsonResponse(data)




# EMPLOYEES

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



def get_employee_data(request, employee_id):
    if request.method == 'GET':
        try:
            employee = Employee.objects.get(id=employee_id)
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
        except Employee.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Employee not found'})




# ROLES

def get_all_roles(request):

    if request.method == 'GET':
        roles = Role.objects.all()

        data = {"data" : []}

        for role in roles:
            data['data'].append({
                'id': role.id,
                'name': role.name,
            })

        return JsonResponse(data)


def get_branch_employees(request, branch_id):

    if request.method == 'GET':
        try:
            branch = Branch.objects.get(id=branch_id)
            employees = Employee.objects.filter(branch=branch)

            data = {"data" : []}

            for employee in employees:
                data['data'].append({
                    'id': employee.id,
                    'name': f"({employee.id}) {employee.first_name} {employee.last_name}",
                })

            return JsonResponse(data)
        except Branch.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Branch not found'})


@csrf_exempt
def new_schedule(request):


    if request.method == 'POST':
        data = json.loads(request.body)
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        branch = data.get('branch')
        employees = data.get('employees')
        allEmployees = data.get('allEmployees')

        if orario_exists(start_date, end_date):
            return JsonResponse({'status': 'error', 'message': 'Un orario per questa data e sede esiste già'}, status=500)

        if allEmployees:
            employees = Employee.objects.filter(branch=branch).values_list('id', flat=True)
            employees = list(employees)

        try:
            branch = Branch.objects.get(id=branch)
        except Branch.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Branch not found'})

        schedule = Schedule.objects.create(
            branch=branch,
            employees=employees,
            start_date=start_date,
            end_date=end_date,
        )

        schedule.save()

        return JsonResponse({'status': 'success', 'schedule_id' : schedule.id})


def schedules(request,schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)

    start_date_dt = datetime.strptime(schedule.start_date, "%Y-%m-%d").date().isoformat()
    end_date_dt = datetime.strptime(schedule.end_date, "%Y-%m-%d").date().isoformat()

    data = {
        "start_date": start_date_dt,
        "end_date": end_date_dt,
        "branch": {
            "id": schedule.branch.id,
            "name": schedule.branch.name
        }
    }
    return JsonResponse(data)


def schedules_employees(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)

    employees = Employee.objects.filter(id__in=schedule.employees)

    # Format the response
    formatted_employees = {"data": []}
    for emp in employees:
        formatted_employees["data"].append({
            "id": emp.id,
            "full_name": f"{emp.first_name} {emp.last_name}",
        })

    return JsonResponse(formatted_employees)


def get_all_schedules(request):

    if request.method == 'GET':
        schedules = Schedule.objects.all()

        data = {"data" : []}



        for schedule in schedules:
            start_date_str = schedule.start_date
            end_date_str = schedule.end_date

            start_date = f"{start_date_str}T00:00:00"
            end_date = f"{end_date_str}T00:00:00"

            data['data'].append({
                'schedule_id': schedule.id,
                'schedule_start_date': start_date,
                'schedule_end_date': end_date,
                'schedule_branch_name': schedule.branch.name,
                'actions': [
                    {"label": "Manage", "url": f"/manage_schedule/{schedule.id}"},
                ]
            })
        print(data)
        return JsonResponse(data)
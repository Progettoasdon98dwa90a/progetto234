import json
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from api.formulas.schedule import orario_exists
from api.models import Schedule, Employee, Branch


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
        return JsonResponse(data)
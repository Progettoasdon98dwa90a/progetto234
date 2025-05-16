import json

from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt

from api.models import Schedule, Branch
from api.tasks import async_create_schedule

def get_branch_schedules(request, branch_id):
    """
    Get all schedules for a specific branch.
    """
    if request.method == 'GET':
        schedules = Schedule.objects.filter(branch_id=branch_id)
        schedule_list = []
        for schedule in schedules:
            schedule_list.append({
                "id": schedule.id,
                "name": get_random_string(10),
                "startDate": schedule.start_date,
                "endDate": schedule.end_date,
                "lastUpdate": "asdasdasd",
                "state": schedule.processed, # 0 = Da verificare, 1 = Confermato, 2 = Passato
            })
        return JsonResponse(schedule_list, safe=False)

@csrf_exempt
def create_new_schedule(request, branch_id):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        start_date = data.get('startDate')
        end_date = data.get('endDate')
        employees = data.get('employees')
        free_days = data.get('freeDays')
        particular_days = data.get('particularDays')
        shifts_data = data.get('shiftsData')
        if not all([branch_id, start_date, end_date,
                    employees, free_days, particular_days,
                    shifts_data]): # if even one is missing
            return JsonResponse({"error": "Missing required fields"}, status=400)

        try:
            branch = Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            return JsonResponse({"error": "Branch not found"}, status=404)

        try:
            s = Schedule.objects.create(branch=branch,
                                        start_date=start_date,
                                        end_date=end_date,
                                        employees=employees,
                                        shifts_data=shifts_data,
                                        free_days=free_days,
                                        particular_days=particular_days)
            s.save()
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

        return JsonResponse({"success": True, "message": "Schedule created successfully."}, status=200)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def start_schedule(request, schedule_id):
    if request.method == 'POST':
        if not schedule_id:
            return JsonResponse({"error": "Missing required fields"}, status=400)
        try:
            schedule = Schedule.objects.get(id=schedule_id)
        except Schedule.DoesNotExist:
            return JsonResponse({"error": "Schedule not found"}, status=404)

        if schedule.processed:
            return JsonResponse({"error": "Schedule already processed"}, status=400)

        async_create_schedule.defer(schedule_id=schedule_id)
        return JsonResponse({"success": True}, status=200)

    return JsonResponse({"error": "Invalid request method"}, status=405)


def backup_schedule(request, schedule_id):
    if request.method == 'GET':
        try:
            schedule = Schedule.objects.get(id=schedule_id)
            schedule.backup_to_json()
            schedule.can_modify = True
            schedule.save(update_fields=['can_modify'])
        except Schedule.DoesNotExist:
            return JsonResponse({"error": "Schedule not found"}, status=404)
        return JsonResponse({"success": True}, status=200)


def restore_schedule(request, schedule_id):
    if request.method == 'GET':
        try:
            schedule = Schedule.objects.get(id=schedule_id)
            schedule.restore_from_json()
            schedule.save(update_fields=['can_modify'])
        except Schedule.DoesNotExist:
            return JsonResponse({"error": "Schedule not found"}, status=404)
        return JsonResponse({"success": True}, status=200)


def get_saved_settings(request, branch_id):
    if request.method == 'GET':
        try:
            # latest schedule from branch
            schedule = Schedule.objects.filter(branch_id=branch_id).latest('id')
        except Schedule.DoesNotExist:
            return JsonResponse({"error": "Schedule not found"}, status=404)

        return JsonResponse({"success": True, "settings": schedule.get_settings()}, status=200)
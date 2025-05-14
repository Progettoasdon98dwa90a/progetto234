from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt

from api.models import Schedule
from api.tasks import create_schedule

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
def start_schedule(request, schedule_id):
    if request.method == 'POST':
        create_schedule.defer(schedule_id=schedule_id)
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
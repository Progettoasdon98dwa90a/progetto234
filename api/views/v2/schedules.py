import json

from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from openpyxl.styles.builtins import title

from api.models import Schedule, Branch
from api.tasks import async_create_schedule

def get_branch_schedules(request, branch_id):
    """
    Get all schedules for a specific branch.
    """
    if request.method == 'GET':
        schedules = Schedule.objects.filter(branch_id=branch_id, processed=True)
        schedule_list = []
        for schedule in schedules:
            schedule_list.append({
                "id": schedule.id,
                "name": get_random_string(10),
                "startDate": schedule.start_date,
                "endDate": schedule.end_date,
                "lastUpdate": "asdasdasd",
                "state": 0, # 0 = Da verificare, 1 = Confermato, 2 = Passato
            })
        return JsonResponse(schedule_list, safe=False)

@csrf_exempt
def create_new_schedule(request, branch_id):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        print(data)

        basic_info = data.get('basicInfo')
        title = basic_info.get('title')
        start_date = basic_info.get('startDate').split('T')[0]
        end_date = basic_info.get('endDate').split('T')[0]

        saveShift = data.get('saveShift', False)

        free_dates_keys = [key for key in basic_info.keys() if key.startswith('freeDates_')]
        employees_ids_free_days = [key.split('_')[1] for key in free_dates_keys]
        employees_ids = data.get('employees') #actually in the schedule
        free_days = []

        for employee_id in employees_ids:
            free_days.append(
                {
                    "employee_id": employee_id,
                    "dates": basic_info.get('freeDates_{}'.format(employee_id))
                }
            )
        shifts_data = data.get('shifts')

        particular_days = data.get('holidaysDates')
        particular_days_data = []
        for i in range(len(particular_days)): # for each particular_days:
            for day in particular_days[i]['dates']:

                day = day.split('T')[0]

                particular_days_data.append({
                    day : particular_days[i]['moreEmployee'], # TODO: add shift parameter
                })
        particular_days = particular_days_data

        try:
            branch = Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            return JsonResponse({"error": "Branch not found"}, status=404)

        try:
            s = Schedule.objects.create(title=title,
                                        branch=branch,
                                        start_date=start_date,
                                        end_date=end_date,
                                        employees=employees_ids,
                                        shifts_data=shifts_data,
                                        free_days=free_days,
                                        particular_days=particular_days)
            s.save()
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

        async_create_schedule.defer(schedule_id=s.id)

        return JsonResponse({"success": True, "message": "Schedule creation started."}, status=200)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def start_schedule(request, schedule_id):
    if request.method == 'POST':
        if not schedule_id:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        try:
            schedule = Schedule.objects.get(id=schedule_id)
            async_create_schedule.defer(schedule_id=schedule.id)
            return JsonResponse({"success": True, "message": "Schedule creation started."}, status=200)
        except Schedule.DoesNotExist:
            return JsonResponse({"error": "Schedule not found"}, status=404)

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
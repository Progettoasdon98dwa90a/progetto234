import json
import time
from datetime import datetime

from django.db.models.signals import post_save, post_delete
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from openpyxl.styles.builtins import title

from api.models import Schedule, Branch, ScheduleEvent
from api.signals import schedule_event_saved, schedule_event_deleted
from api.tasks import async_create_schedule

def parse_date(date_str, format_from, format_to='%Y-%m-%d'):
    """Parse and convert date between formats"""
    return datetime.strptime(date_str, format_from).strftime(format_to)

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
                "state": schedule.state, # 0 = Da verificare, 1 = Confermato, 2 = Passato
            })
        return JsonResponse(schedule_list, safe=False)

@csrf_exempt
def create_new_schedule(request, branch_id):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        print(data)
        basic_info = data.get('basicInfo')
        title = basic_info.get('title')
        start_date = basic_info.get('startDate')
        end_date = basic_info.get('endDate')

        saveShift = data.get('saveShift', False)

        employees_ids = data.get('employees') #actually in the schedule
        free_days = []

        for employee_id in employees_ids:
            free_days.append(
                {
                    "employee_id": employee_id,
                    "dates": basic_info.get('freeDates_{}'.format(employee_id))
                }
            )

        # convert all the dates from dd/mm/yyyy to yyyy-mm-dd
        shifts_data = data.get('shifts')

        particular_days = data.get('holidaysDates')
        particular_days_data = {}
        for i in range(len(particular_days)): # for each particular_days:
            for day in particular_days[i]['dates']:
                particular_days_data[day] = [particular_days[i]['moreEmployee'], particular_days[i]['shift']]
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
    if request.method == 'GET':
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


def rollback_schedule(request, schedule_id):
    if request.method == 'GET':
        schedule = None # Define schedule outside try to access in finally if needed
        try:
            schedule = Schedule.objects.get(id=schedule_id)

            # --- Temporarily disable ScheduleEvent signals ---
            # Disconnect the receivers for post_save and post_delete signals
            # for the ScheduleEvent sender.
            # Ensure the receiver function names match what you have in signals.py
            post_save.disconnect(receiver=schedule_event_saved, sender=ScheduleEvent)
            post_delete.disconnect(receiver=schedule_event_deleted, sender=ScheduleEvent)
            # -------------------------------------------------

            try:
                # Call the method that potentially creates/deletes ScheduleEvents
                # Signals for ScheduleEvent will be skipped here
                schedule.restore_from_json()

                # Saving the main schedule object (this *will* trigger Schedule's post_save,
                # but you only wanted to skip ScheduleEvent's signals, which is fine)
                schedule.save(update_fields=['can_modify'])

                # Fetch the events *after* the restore is complete
                all_events = ScheduleEvent.objects.filter(schedule=schedule) # Filter by the schedule instance
                data_events = [event.format_json() for event in all_events]

                time.sleep(0.1) # Consider if this is truly necessary
                schedule.delete_backup() # Assuming this method does not involve ScheduleEvents

            except Exception as e:
                 # Catch any error that occurs *after* disconnecting signals
                 print(f"An error occurred during rollback: {e}") # Log the error
                 # Re-raise the exception after ensuring signals are reconnected
                 raise # The 'finally' block will execute before the raise

            finally:
                # --- Re-enable ScheduleEvent signals ---
                # Reconnect the receivers in the finally block to ensure they are
                # reconnected even if an error occurred.
                post_save.connect(receiver=schedule_event_saved, sender=ScheduleEvent)
                post_delete.connect(receiver=schedule_event_deleted, sender=ScheduleEvent)
                # ---------------------------------------

        except Schedule.DoesNotExist:
            return JsonResponse({"error": "Schedule not found"}, status=404)
        except Exception as e:
            # Catch the re-raised exception or other exceptions
            return JsonResponse({"error": str(e)}, status=500)


        # If everything was successful
        return JsonResponse({"success": True, 'events': data_events}, status=200)


def get_saved_settings(request, branch_id):
    if request.method == 'GET':
        try:
            # latest schedule from branch
            schedule = Schedule.objects.filter(branch_id=branch_id).latest('id')
        except Schedule.DoesNotExist:
            return JsonResponse({"error": "Schedule not found"}, status=404)

        return JsonResponse({"success": True, "settings": schedule.get_settings()}, status=200)

@csrf_exempt
def confirm_schedule(request, schedule_id):
    if request.method == 'GET':
        try:
            schedule = Schedule.objects.get(id=schedule_id)
            schedule.state = 1
            schedule.save()
            return JsonResponse({"success": True, 'current_state': schedule.state}, status=200)
        except Schedule.DoesNotExist:
            return JsonResponse({"error": "Schedule not found"}, status=404)

    return JsonResponse({"error": "Invalid request method"}, status=405)
import json
import time
from datetime import datetime

from django.db.models.signals import post_save, post_delete
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from openpyxl.styles.builtins import title

from api.models import Schedule, Branch, ScheduleEvent
from api.tasks import async_create_schedule

def parse_date(date_str, format_from, format_to='%Y-%m-%d'):
    """Parse and convert date between formats"""
    return datetime.strptime(date_str, format_from).strftime(format_to)

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
                "name": schedule.title,
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

        shifts_data = data.get('shifts')


        particular_days = data.get('holidaysDates')
        particular_days_data = {}
        for i in range(len(particular_days)): # for each object of dates, shift (id), moreEmployees, in particular_days:
            for day in particular_days[i]['dates']:
                matching_shift_name = shifts_data[particular_days[i]['shift']]['name']
                particular_days_data[day] = [particular_days[i]['moreEmployee'], matching_shift_name]


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

@csrf_exempt
def confirm_schedule(request, schedule_id):
    if request.method == 'GET':
        try:
            schedule = Schedule.objects.get(id=schedule_id)
            schedule.state = 1
            schedule.delete_backup()
            schedule.save()
            return JsonResponse({"success": True, 'current_state': schedule.state}, status=200)
        except Schedule.DoesNotExist:
            return JsonResponse({"error": "Schedule not found"}, status=404)

    return JsonResponse({"error": "Invalid request method"}, status=405)

def rollback_schedule(request, schedule_id):

    if request.method == 'GET':
        schedule = None # Define schedule outside try to access in finally if needed
        try:
            schedule = Schedule.objects.get(id=schedule_id)
            try:
                schedule.restore_from_json()
                all_events = ScheduleEvent.objects.filter(schedule=schedule) # Filter by the schedule instance
                data_events = [event.format_json() for event in all_events]
                schedule.delete_backup() # Assuming this method does not involve ScheduleEvents
            except Exception as e:
                 # Catch any error that occurs *after* disconnecting signals
                 print(f"An error occurred during rollback: {e}") # Log the error
                 # Re-raise the exception after ensuring signals are reconnected
                 raise # The 'finally' block will execute before the raise

        except Schedule.DoesNotExist:
            return JsonResponse({"error": "Schedule not found"}, status=404)
        except Exception as e:
            # Catch the re-raised exception or other exceptions
            return JsonResponse({"error": str(e)}, status=500)

        # If everything was successful
        return JsonResponse({"success": True, 'events': data_events}, status=200)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def delete_schedules(request):
    if request.method == 'DELETE':
        deleted_ids = []
        errors = []

        try:
            schedules_ids_to_delete = json.loads(request.body.decode('utf-8'))
            if not isinstance(schedules_ids_to_delete, list):
                return JsonResponse({
                    "error": "Request body must be a JSON array of schedule IDs."
                }, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format in request body."}, status=400)
        except Exception as e: # Catch other potential errors during body parsing
            return JsonResponse({"error": f"Error processing request body: {str(e)}"}, status=400)

        if not schedules_ids_to_delete:
            return JsonResponse({
                "message": "No schedule IDs provided for deletion.",
                "deleted_ids": [],
                "errors": []
            }, status=200) # Or 400 if you consider empty list an error

        for schedule_id in schedules_ids_to_delete:
            try:
                # It's good to validate the type of schedule_id if possible
                if not isinstance(schedule_id, int): # Assuming IDs are integers
                    errors.append({
                        "id": schedule_id,
                        "error": "Invalid ID format. ID must be an integer."
                    })
                    continue # Skip to the next ID

                schedule = Schedule.objects.get(id=schedule_id)
                schedule.delete() # This might also raise an exception
                deleted_ids.append(schedule_id)
            except Schedule.DoesNotExist:
                errors.append({
                    "id": schedule_id,
                    "error": "Schedule not found"
                })
            except Exception as e: # Catch any other unexpected errors during get() or delete()
                errors.append({
                    "id": schedule_id,
                    "error": f"An unexpected error occurred: {str(e)}"
                })

        response_data = {
            "deleted_ids": deleted_ids,
            "errors": errors
        }

        # Determine appropriate status code
        # 200 OK: If all operations were successful OR if some were successful and some failed (client can check body)
        # 207 Multi-Status: More semantically correct if there's a mix, but 200 is often simpler for clients.
        # 404 Not Found: Only if ALL requested IDs were not found and NO other errors occurred.
        # 400 Bad Request: If the input itself was malformed (e.g., non-integer IDs if that's a strict rule).

        status_code = 200 # Default to 200 OK
        if not deleted_ids and errors:
            if all(err.get("error") == "Schedule not found" for err in errors):
                # If everything failed and all were "not found", 404 might be suitable.
                # However, for a batch operation, returning 200 with details is often preferred
                # to avoid masking that the *request itself* was processed.
                # Let's stick with 200 and let the client parse the body.
                pass
            # elif any other type of error occurred, 200 is still fine with details in body.
            # Or you could use 500 if there were server-side errors for some items.
            # For simplicity, we'll generally stick to 200 if the request format was valid and processed.

        return JsonResponse(response_data, status=status_code)

    return JsonResponse({"error": "Invalid request method"}, status=405)



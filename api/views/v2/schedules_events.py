from django.http import JsonResponse
from api.models import Employee, Schedule, ScheduleEvent
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def create_schedule_event(request, schedule_id):
    if request.method != 'POST':
        return JsonResponse({"status" : "error"}, status=405)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    try:
        schedule_id = int(schedule_id)
        schedule = Schedule.objects.get(id=schedule_id)
    except:
        return JsonResponse({"status" : "error", 'message': 'Invalid schedule ID'}, status=400)
    try:
        employee_id = int(data.get('employeeId'))
        employee = Employee.objects.get(id=employee_id)
    except:
        return JsonResponse({"status" : "error", 'message': 'Invalid employee ID'}, status=400)
    
    date = data.get('date')
    start_time = data.get('startTime')
    end_time = data.get('endTime')
    color = data.get('color')

    try:
        schedule_event = ScheduleEvent.objects.create(
            schedule=schedule, 
            employee=employee, 
            date = date,
            start_time=start_time, 
            end_time=end_time, 
            color=color)
        
        schedule_event.save()
        print(f"Schedule event created successfully: {schedule_event}")
        # return all events of this schedule
        all_schedule_events = ScheduleEvent.objects.filter(schedule_id=schedule_id)
        events_data = [event.format_json() for event in all_schedule_events]

        return JsonResponse({"status": "success", "events": events_data}, status=200)
    except Exception as e:
        print(f"Error creating schedule event: {e}")
        schedule_event = None
        return JsonResponse({"status" : "error"}, status=500)
    

def get_schedule_events(request, schedule_id):
    if request.method == 'GET':
        try:
            schedule_events = ScheduleEvent.objects.filter(schedule_id=schedule_id)
            return JsonResponse({"status": "success"}, status=200)
        except ScheduleEvent.DoesNotExist:
            return JsonResponse({"status" : "error"}, status=404)
        except Exception as e:
            print(f"Error getting schedule events: {e}")
            return JsonResponse({"status" : "error"}, status=500)
    else:
        return JsonResponse({"status" : "error"}, status=405)
    

from django.http import JsonResponse
from api.models import ScheduleEvent
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def create_schedule_event(request, schedule_id, employee_id, event, start_time, end_time, color):
    if request.method != 'POST':
        return JsonResponse("Invalid request method", status=405)
    if not all([schedule_id, employee_id, event, start_time, end_time, color]):
        return JsonResponse("Missing required parameters", status=400)
    
    try:
        schedule_event = ScheduleEvent.objects.create(
            schedule_id=schedule_id, 
            employee_id=employee_id, 
            event=event, 
            start_datetime=start_time, 
            end_datetime=end_time, color=color)
        
        schedule_event.save()
        print(f"Schedule event created successfully: {schedule_event}")
        return JsonResponse("Schedule event created successfully", status=201)
    except Exception as e:
        print(f"Error creating schedule event: {e}")
        schedule_event = None
        return JsonResponse("Error creating schedule event", status=500)
    

def get_schedule_events(request, schedule_id):
    if request.method == 'GET':
        try:
            schedule_events = ScheduleEvent.objects.filter(schedule_id=schedule_id)
            return JsonResponse("Schedule events retrieved successfully", status=200)
        except ScheduleEvent.DoesNotExist:
            return JsonResponse("Schedule events not found", status=404)
        except Exception as e:
            print(f"Error getting schedule events: {e}")
            return JsonResponse("Error getting schedule events", status=500)
    else:
        return JsonResponse("Invalid request method", status=405)
    

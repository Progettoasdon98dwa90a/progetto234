from django.http import JsonResponse
from api.models import ScheduleEvent
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def create_schedule_event(schedule_id, employee_id, event, start_time, end_time, color):
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
